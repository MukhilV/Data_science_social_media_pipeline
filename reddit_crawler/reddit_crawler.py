import os
import psycopg2
import logging
from pyfaktory import Client, Consumer, Producer, Job
from reddit_client import RedditClient
import time
import datetime
import requests

logger = logging.getLogger("Reddit crawler")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

# load in function for .env reading
from dotenv import load_dotenv
load_dotenv()

FAKTORY_SERVER_URL = os.environ.get("FAKTORY_SERVER_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")
MODERATE_HATESPEECH_API_KEY = os.environ.get("MODERATE_HATESPEECH_API_KEY")
MODERATE_HATESPEECH_API = os.environ.get("MODERATE_HATESPEECH_API")

def hs_check_comment(comment):
    CONF_THRESHOLD = 0.9

    data = {
        "token": MODERATE_HATESPEECH_API_KEY,
        "text": comment
    }

    resp = requests.post(MODERATE_HATESPEECH_API, json=data)
    response = None
    try: 
        if resp.headers.get('Content-Type') == 'application/json; charset=utf-8':
            response = resp.json()
        else:
            logger.error("Non-JSON response from hs_check_comment")
            return None, None, None

        if response["response"] == "Success":
            if response["class"] == "flag" and float(response["confidence"]) >= CONF_THRESHOLD:
                return (True, response["class"], float(response["confidence"]))
            else:
                return (False, response["class"], float(response["confidence"]))
        else: 
            logger.error(f"API call to ModerateHateSpeechFailed: Response - {response["response"]}")
            return None, None, None
    except Exception as e:
        logger.error(f"Encountered an exception in hs_check_comment: {e}\n Response: {resp}")
        
    return None, None, None


def store_post_to_db(post):
    try:
        # print("Inside store_post_to_db()")
        conn = psycopg2.connect(dsn=DATABASE_URL)
        cur = conn.cursor()

        # Convert the Unix timestamp to a Python datetime object
        # created_at = datetime.datetime.utcfromtimestamp(post["data"]["created_utc"])
        
        created_at = post["data"].get("created_utc")
        if created_at is not None:
            created_at = datetime.datetime.fromtimestamp(post["data"]["created_utc"], tz=datetime.timezone.utc)
        else:
            logger.warning("Post is missing 'created_utc'")
            created_at = None


        # logger.info(f"Inside store_post_to_db(), just before Query execution.")
        # print("#############Inside store_post_to_db(), just before Query execution.")

        # Insert post data into the posts table
        # q = """INSERT INTO posts (post_id, title, content, author, score, comments, created_at, subreddit, url) 
        #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (post_id) DO NOTHING RETURNING post_id"""
        #   ON CONFLICT (id) DO NOTHING

        toxic_flag, toxic_class, toxic_score = None, None, None
        if "data" in post.keys():
            keys = post["data"].keys()
            content = post["data"].get("selftext", "")
            if "title" in keys  and  content!="" and content is not None: 
                toxic_flag, toxic_class, toxic_score = hs_check_comment(str(post["data"]["title"]) + ":" + str(content))
            elif "title" in keys:
                toxic_flag, toxic_class, toxic_score = hs_check_comment(post["data"]["title"])

        q = """INSERT INTO posts_from_nov17 (post_id, title, content, author, score, comments, created_at, subreddit, url, toxic_flag, toxic_class, toxic_score) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (post_id) DO NOTHING RETURNING post_id"""

        cur.execute(q, (
            post["data"]["id"],
            post["data"]["title"],
            post["data"].get("selftext", ""),  # Post content (can be empty)
            post["data"]["author"],  # Author
            post["data"]["score"],  # Post score
            post["data"]["num_comments"],  # Number of comments
            created_at,  # Use the converted datetime object
            post["data"]["subreddit"],  # Subreddit name
            post["data"]["url"],  # Post URL
            toxic_flag,
            toxic_class,
            toxic_score
        ))

        conn.commit()

        result = cur.fetchone()
        if result: 
            # print("Is this causing error?")
            # print(result == None)
            post_id = result[0]
            logger.info(f"Inserted {post["data"]["subreddit"]} post ID: {post_id}")
        
        cur.close()
        conn.close()
        # print("Exiting store_post_to_db()")

    except Exception as e:
        logger.error(f"Error storing post: {e}")
    finally:
        cur.close()
        conn.close()


def store_comments_to_db(comments, post):
    # print("Inside store_comments_to_db()")
    post_id = post['data']['id']
    conn = psycopg2.connect(dsn=DATABASE_URL)
    cur = conn.cursor()
    
    for comment in comments[1]["data"]["children"]:
        # created_at = datetime.datetime.utcfromtimestamp(comment["data"]["created_utc"])
        if comment["data"].get("created_utc"):
            created_at = datetime.datetime.fromtimestamp(comment["data"]["created_utc"], tz=datetime.timezone.utc)

            # logger.info(f"Inside store_comments_to_db(), just before Query execution of comment ID:" + comment["data"]["id"])
            
            # q = """INSERT INTO comments (post_id, comment_id, author, body, score, created_at) 
            #     VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (comment_id) DO NOTHING"""

            toxic_flag, toxic_class, toxic_score = None, None, None
            if "data" in comment.keys() and "body" in comment["data"].keys(): 
                toxic_flag, toxic_class, toxic_score = hs_check_comment(comment["data"]["body"])

            q = """INSERT INTO comments_from_nov17th (post_id, comment_id, author, body, score, created_at, 
            toxic_flag, toxic_class, toxic_score, subreddit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON CONFLICT (comment_id) DO NOTHING"""


            cur.execute(q, (
                post_id,
                comment["data"]["id"],
                comment["data"]["author"],
                comment["data"]["body"],
                comment["data"]["score"],
                created_at,  # Use the converted datetime object
                toxic_flag, 
                toxic_class, 
                toxic_score,
                post["data"]["subreddit"]
            ))
            logger.info(f"Inserted {post["data"]["subreddit"]} comment ID: {comment["data"]["id"]}")

    cur.close()
    conn.commit()
    conn.close()

def crawl_subreddit(subreddit):
    client = RedditClient()
    posts_data = client.get_new_posts(subreddit)

    if posts_data:
        for post in posts_data['data']['children']:
            if post['data'] is not None: 
                store_post_to_db(post)

                # Now get the comments for the post
                comments_data = client.get_comments(subreddit, post['data']['id'])
                if comments_data:
                    store_comments_to_db(comments_data, post)


    subreddits = os.getenv('SUBREDDITS', '').split(',')
    with Client(faktory_url=FAKTORY_SERVER_URL, role="producer") as client:
        producer = Producer(client=client)

        run_at = datetime.datetime.utcnow() + datetime.timedelta(minutes= len(subreddits) * 1)
        run_at = run_at.isoformat()[:-7] + "Z"
        
        job = Job(jobtype="crawl-subreddit", args=(subreddit,), queue="crawl-subreddit", at=run_at)
        producer.push(job)
        logger.info("Produced and scheduled a Job to crawl - "+ subreddit)


if __name__ == "__main__":
    with Client(faktory_url=FAKTORY_SERVER_URL, role="consumer") as client:
        consumer = Consumer(client=client, queues=["crawl-subreddit"], concurrency=5)
        consumer.register("crawl-subreddit", crawl_subreddit)
        consumer.run()


