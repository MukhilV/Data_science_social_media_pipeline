from chan_client import ChanClient
import logging
from pyfaktory import Client, Consumer, Job, Producer
import datetime
import psycopg2
import requests

# these three lines allow psycopg to insert a dict into
# a jsonb coloumn
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter

register_adapter(dict, Json)

# load in function for .env reading
from dotenv import load_dotenv


logger = logging.getLogger("4chan client")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

load_dotenv()

import os

FAKTORY_SERVER_URL = os.environ.get("FAKTORY_SERVER_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")
MODERATE_HATESPEECH_API_KEY = os.environ.get("MODERATE_HATESPEECH_API_KEY")
MODERATE_HATESPEECH_API = os.environ.get("MODERATE_HATESPEECH_API")

'''
The function gets in a text and returns if the text is toxic or not based on the threshold
'''
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
        logger.error(f"Encountered an exception in hs_check_comment: {e}")
        
    return None, None, None
  
  


"""
Return all the thread numbers from a catalog json object
"""


def thread_numbers_from_catalog(catalog):
    thread_numbers = []
    for page in catalog:
        for thread in page["threads"]:
            thread_number = thread["no"]
            thread_numbers.append(thread_number)

    return thread_numbers


"""
Return thread numbers that existed in previous but don't exist
in current
"""


def find_dead_threads(previous_catalog_thread_numbers, current_catalog_thread_numbers):
    dead_thread_numbers = set(previous_catalog_thread_numbers).difference(
        set(current_catalog_thread_numbers)
    )
    return dead_thread_numbers


"""
Crawl a given thread and get its json.
Insert the posts into db
"""


def crawl_thread(board, thread_number):
    chan_client = ChanClient()
    thread_data = chan_client.get_thread(board, thread_number)

    if thread_data is not None: 

        # logger.info(f"Thread: {board}/{thread_number}/:\n{thread_data}")
        logger.info(f"Thread: {board}/{thread_number}")

        # really soould use a connection pool
        conn = psycopg2.connect(dsn=DATABASE_URL)

        cur = conn.cursor()
        # now insert into db
        # iterate through the thread data and get all the post data
        for post in thread_data["posts"]:
            post_number = post["no"]

            toxic_flag, toxic_class, toxic_score = None, None, None 
            if "com" in post.keys(): 
                # toxic_flag: True/False, toxic_class: flag/normal, toxic_score: float in the range of [0,1]
                toxic_flag, toxic_class, toxic_score = hs_check_comment(post["com"])

            q = "INSERT INTO posts (board, thread_number, post_number, data, toxic_flag, toxic_class, toxic_score) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"
            cur.execute(q, (board, thread_number, post_number, post, toxic_flag, toxic_class, toxic_score))
            # commit our insert to the database.
            conn.commit()

            # it's often useful to know the id of the newly inserted
            # row. This is so you can launch other jobs that might
            # do additional processing.
            # e.g., to classify the toxicity of a post
            db_id = cur.fetchone()[0]
            logger.info(f"Inserted into DB id: {db_id}")

        # close cursor connection
        cur.close()
        # close connection
        conn.close()


"""
Go out, grab the catalog for a given board, and figure out what threads we need
to collect.

For each thread to collect, enqueue a new job to crawl the thread.

Schedule catalog crawl to run again at some point in the future.
"""


def crawl_catalog(board, previous_catalog_thread_numbers=[]):
    chan_client = ChanClient()

    current_catalog = chan_client.get_catalog(board)

    if current_catalog is not None:

        current_catalog_thread_numbers = thread_numbers_from_catalog(current_catalog)

        dead_threads = find_dead_threads(
            previous_catalog_thread_numbers, current_catalog_thread_numbers
        )
        logger.info(f"dead threads numbers: {dead_threads}")

        # issue the crawl thread jobs for each dead thread
        crawl_thread_jobs = []
        with Client(faktory_url=FAKTORY_SERVER_URL, role="producer") as client:
            producer = Producer(client=client)
            for dead_thread in dead_threads:
                # see https://github.com/ghilesmeddour/faktory_worker_python/blob/main/src/pyfaktory/models.py
                # what a `Job` looks like
                job = Job(
                    jobtype="crawl-thread", args=(board, dead_thread), queue="crawl-thread"
                )

                crawl_thread_jobs.append(job)

            producer.push_bulk(crawl_thread_jobs)

        # Schedule another catalog crawl to happen at some point in future
        with Client(faktory_url=FAKTORY_SERVER_URL, role="producer") as client:
            producer = Producer(client=client)
            # figure out how to use non depcreated methods on your own
            # run_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
            run_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
            run_at = run_at.isoformat()[:-7] + "Z"
            logger.info(f"run_at = {run_at}")
            job = Job(
                jobtype="crawl-catalog",
                args=(board, current_catalog_thread_numbers),
                queue="crawl-catalog",
                at=str(run_at),
            )
            producer.push(job)


if __name__ == "__main__":
    # we want to pull jobs off the queues and execute them
    # FOREVER (continuously)
    with Client(faktory_url=FAKTORY_SERVER_URL, role="consumer") as client:
        consumer = Consumer(
            client=client, queues=["crawl-catalog", "crawl-thread"], concurrency=5
        )
        consumer.register("crawl-catalog", crawl_catalog)
        consumer.register("crawl-thread", crawl_thread)
        # tell the consumer to pull jobs off queue and execute them!
        consumer.run()
