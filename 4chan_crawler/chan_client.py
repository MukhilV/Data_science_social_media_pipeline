# 4chan api client that has minimal functionality to collect data

import logging
import requests

# logger setup
logger = logging.getLogger("4chan client")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

# API_BASE = "http://a.4cdn.org"


class ChanClient:
    API_BASE = "http://a.4cdn.org"
    # def __init__(self):

    # need to be able to collect threads
    """
    Get json for a given thread
    """

    def get_thread(self, board, thread_number):
        # sample api call: http://a.4cdn.org/pol/thread/124205675.json
        # make an http request to the url
        request_pieces = [board, "thread", f"{thread_number}.json"]

        api_call = self.build_request(request_pieces)
        return self.execute_request(api_call)

    """
    Get catalog json for a given board
    """

    def get_catalog(self, board):
        request_pieces = [board, "catalog.json"]
        api_call = self.build_request(request_pieces)

        return self.execute_request(api_call)

    """
    Build a request from pieces
    """

    def build_request(self, request_pieces):
        api_call = "/".join([self.API_BASE] + request_pieces)
        return api_call

    """
    This executes an http request and returns json
    """

    def execute_request(self, api_call):
        resp = requests.get(api_call)  # error handling needed
        logger.info("API REQUEST MADE!")
        logger.info(resp.status_code)
        json = None 
        try: 
            json = resp.json()  # error handling needed
            # logger.info(f"json: {json}")
        except:
            logger.error("Error: The server did not return valid JSON.")
        return json


if __name__ == "__main__":
    client = ChanClient()
    json = client.get_thread("pol", 124205675)
    # print(json)
