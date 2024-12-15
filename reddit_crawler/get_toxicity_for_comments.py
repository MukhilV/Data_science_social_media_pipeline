import requests
import os
import logging


import psycopg2
from psycopg2.extras import execute_values


# load in function for .env reading
from dotenv import load_dotenv

load_dotenv()



logger = logging.getLogger("Reddit comments toxicity")
logger.propagate = False
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)


MODERATE_HATESPEECH_API_KEY = os.environ.get("MODERATE_HATESPEECH_API_KEY")
MODERATE_HATESPEECH_API = os.environ.get("MODERATE_HATESPEECH_API")
DATABASE_URL = os.environ.get("DATABASE_URL")


def get_hs_score(comment):
    CONF_THRESHOLD = 0.9

    data = {
        "token": MODERATE_HATESPEECH_API_KEY,
        "text": comment
    }

    resp = requests.post(MODERATE_HATESPEECH_API, json=data)
    # print(resp)
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



def update_missing_toxic_scores():
    """
    Compute and update toxic_flag, toxic_class, and toxic_score for rows where these fields are missing.
    
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(dsn=DATABASE_URL)
        cursor = conn.cursor()

        # Fetch rows with missing toxic scores
        select_query = """
        SELECT comment_id, body
        FROM comments
        WHERE toxic_flag IS NULL OR toxic_class IS NULL OR toxic_score IS NULL;
        """
        # LIMIT 10;

        cursor.execute(select_query)
        rows = cursor.fetchall()

        if not rows:
            print("No rows found with missing toxic scores.")
            return

        # Compute toxic scores for each row
        iteration = 0

        updates = []
        for comment_id, body in rows:
            toxic_flag, toxic_class, toxic_score = get_hs_score(body)
            updates.append((toxic_flag, toxic_class, toxic_score, comment_id))

            iteration += 1
            if iteration % 100 == 0:
                # Update the database in batches for efficiency
                update_query = """
                UPDATE comments
                SET toxic_flag = data.toxic_flag,
                    toxic_class = data.toxic_class,
                    toxic_score = data.toxic_score
                FROM (VALUES %s) AS data(toxic_flag, toxic_class, toxic_score, comment_id)
                WHERE comments.comment_id = data.comment_id;
                """
                execute_values(cursor, update_query, updates)
                conn.commit()
                updates= []
                logger.info(f"Updated {iteration//100}00 rows with hatespeech score.")

        print(f"Updated {len(updates)} rows successfully.")

    except Exception as e:
        print(f"Error in update_missing_toxic_scores(): {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()



if __name__ == "__main__":
    # comment ="STFU Noob"
    # get_hs_score(comment)
    # Call the function
    update_missing_toxic_scores()
