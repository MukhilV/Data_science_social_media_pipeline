import os
import psycopg2
import logging
from pyfaktory import Client, Consumer, Producer, Job
from reddit_client import RedditClient
import time
import datetime

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



if __name__ == "__main__":
    print("Cold start reddit crawl")
    subreddits = os.getenv('SUBREDDITS', '').split(',')
    
    with Client(faktory_url=FAKTORY_SERVER_URL, role="producer") as client:
        producer = Producer(client=client)
        
        # Schedule crawling for each subreddit
        for i in range(len(subreddits)):
            # Schedule a job for every 5 minutes
            run_at = datetime.datetime.utcnow() + datetime.timedelta(minutes= i * 1)
            run_at = run_at.isoformat()[:-7] + "Z"
            
            job = Job(jobtype="crawl-subreddit", args=(subreddits[i],), queue="crawl-subreddit", at=run_at)
            producer.push(job)
            logger.info("Produced and scheduled a Job to crawl - "+ subreddits[i])