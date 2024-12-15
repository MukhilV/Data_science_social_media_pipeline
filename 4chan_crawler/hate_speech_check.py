import requests
import os
import logging
# load in function for .env reading
from dotenv import load_dotenv

load_dotenv()



logger = logging.getLogger("Reddit crawler")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)


MODERATE_HATESPEECH_API_KEY = os.environ.get("MODERATE_HATESPEECH_API_KEY")
MODERATE_HATESPEECH_API = os.environ.get("MODERATE_HATESPEECH_API")


def hs_check_comment(comment):
    CONF_THRESHOLD = 0.9

    data = {
        "token": MODERATE_HATESPEECH_API_KEY,
        "text": comment
    }

    resp = requests.post(MODERATE_HATESPEECH_API, json=data)
    print(resp.json())
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

if __name__ == "__main__":
  # Data json from 4chan table
  data  = {"h": 436, "w": 600, "no": 145053648, 
           "com": "Say my name", "ext": ".png", 
           "md5": "7sUtiDc6193Uvwq6hpMf7A==", "now": "10/13/24(Sun)19:12:45", 
           "tim": 1728861165616443, "name": "Anonymous", 
           "time": 1728861165, "tn_h": 181, "tn_w": 250, 
           "fsize": 201478, "resto": 0, "closed": 1,
            "images": 1, "country": "US", "replies": 32,
            "archived": 1, "filename": "1728861068529087", 
            "bumplimit": 0, "imagelimit": 0, "archived_on": 1729050173,
            "country_name": "United States", "semantic_url": "say-my-name"}
  
  toxic_class, toxic_flag, score = hs_check_comment(data["com"])
  print(toxic_class, toxic_flag, score)


  
    # print(resp.headers)
    # print()
    # print(resp.headers.get('Content-Type'), "|", "application/json; charset=utf-8", )
    # print(type(resp.headers.get('Content-Type')), type('application/json; charset=utf-8'))
    # print(resp.headers.get('Content-Type') == 'application/json; charset=utf-8')
    # print("Response:", response)