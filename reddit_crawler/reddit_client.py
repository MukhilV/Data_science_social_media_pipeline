import requests
import logging
import os
import logging
import time

logger = logging.getLogger("Reddit client")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

from dotenv import load_dotenv
load_dotenv()

# class RedditClient:
#     API_BASE = "https://www.reddit.com"
    
#     def get_new_posts(self, subreddit):
#         url = f"{self.API_BASE}/r/{subreddit}/new.json"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             return response.json()
#         else:
#             logger.error(f"Failed to fetch posts from {subreddit}: {response.status_code}")
#             return None

#     def get_comments(self, subreddit, post_id):
#         url = f"{self.API_BASE}/r/{subreddit}/comments/{post_id}.json"
#         headers = {'User-Agent': 'Mozilla/5.0'}
#         response = requests.get(url, headers=headers)

#         if response.status_code == 200:
#             return response.json()
#         else:
#             logger.error(f"Failed to fetch comments for post {post_id}: {response.status_code}")
#             return None



class RedditClient:
    API_BASE = "https://oauth.reddit.com"
    TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
    
    def __init__(self):
        self.client_id = os.environ.get("REDDIT_CLIENT_ID")
        self.client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        self.user_agent = "Mozilla/5.0"
        self.access_token = None
        self.get_access_token()  # Fetch token on initialization

    def get_access_token(self):
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        headers = {"User-Agent": self.user_agent}
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(self.TOKEN_URL, auth=auth, data=data, headers=headers)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            logger.info("Successfully retrieved access token")
        else:
            logger.error(f"Failed to retrieve access token: {response.status_code}")

    def get_new_posts(self, subreddit):
        if not self.access_token:
            print(self.client_id, self.client_secret)
            logger.error("Access token is missing. Unable to fetch posts.")
            return None

        url = f"{self.API_BASE}/r/{subreddit}/new.json"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': self.user_agent
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:  # Token expired
            logger.warning("Access token expired. Refreshing token.")
            self.get_access_token()  # Refresh the token
            return self.get_new_posts(subreddit)
        else:
            logger.error(f"Failed to fetch posts from {subreddit}: {response.status_code}")
            return None

    def get_comments(self, subreddit, post_id):
        if not self.access_token:
            logger.error("Access token is missing. Unable to fetch comments.")
            return None

        url = f"{self.API_BASE}/r/{subreddit}/comments/{post_id}.json"
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'User-Agent': self.user_agent
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:  # Token expired
            logger.warning("Access token expired. Refreshing token.")
            self.get_access_token()  # Refresh the token
            return self.get_comments(subreddit, post_id)
        else:
            logger.error(f"Failed to fetch comments for post {post_id}: {response.status_code}")
            return None



if __name__ == "__main__":
    client = RedditClient()
    json = client.get_new_posts("sports")
    print("==================== Collected posts from sports ====================")
    print(json)
    json = client.get_comments("sports", 1)
    print("==================== Collected comments from sports ====================")
    print(json)