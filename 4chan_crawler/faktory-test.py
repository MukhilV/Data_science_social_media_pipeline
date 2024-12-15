import logging
from pyfaktory import Client, Consumer, Job, Producer
import time
import random

logger = logging.getLogger("faktory test")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)


def adder(x, y):
    logger.info(f"{x} + {y} = {x + y}")
    # make random sleep time?
    sleep_for = random.randint(0, 10)
    time.sleep(sleep_for)
    logger.info(f"finished sleeping")


if __name__ == "__main__":
    # Default url for a Faktory server running locally
    faktory_server_url = "tcp://:password@localhost:7419"

    with Client(faktory_url=faktory_server_url, role="producer") as client:
        producer = Producer(client=client)

        # generate 10 adder jobs
        jobs = []
        for job_num in range(10):
            # see https://github.com/ghilesmeddour/faktory_worker_python/blob/main/src/pyfaktory/models.py
            # what a `Job` looks like
            job = Job(jobtype="adder", args=(job_num, 4), queue="default")
            # job = Job(jobtype="adder", args=(job_num, 'a'), queue="default")
            # producer.push(job)
            jobs.append(job)

        producer.push_bulk(jobs)

    print("Starting consumer")

    with Client(faktory_url=faktory_server_url, role="consumer") as client:
        consumer = Consumer(client=client, queues=["default"], concurrency=3)
        consumer.register("adder", adder)
        consumer.run()
