import requests
import os
import logging


import psycopg2
from psycopg2.extras import execute_values


# load in function for .env reading
from dotenv import load_dotenv

load_dotenv()



logger = logging.getLogger("4chan toxicity")
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



def update_missing_toxic_scores(batch_size = 100):
    """
    Compute and update toxic_flag, toxic_class, and toxic_score for rows where these fields are missing.
    
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(dsn=DATABASE_URL)
        cursor = conn.cursor()

        iteration = 0

        while(True):
            check_query = """
                            SELECT 
                                count(id) as update_count
                            FROM 
                                posts
                            WHERE 
                                toxic_flag IS NULL
                                OR toxic_class IS NULL
                                OR toxic_score IS NULL;
                """
            cursor.execute(check_query)
            result_set = cursor.fetchall()

            update_count = result_set[0][0]
            logger.info(f"Rows yet to be updated - {update_count}")

            if update_count > 0 :
                # Fetch rows with missing toxic scores
                select_query = f"""SELECT 
                                        id, 
                                        thread_number, 
                                        data->>'com' AS comment
                                    FROM 
                                        posts
                                    WHERE 
                                        toxic_flag IS NULL
                                        OR toxic_class IS NULL
                                        OR toxic_score IS NULL
                                    ORDER BY 
                                        id DESC
                                    LIMIT {batch_size};
                                """
                # LIMIT 10;

                cursor.execute(select_query)
                rows = cursor.fetchall()

                if not rows:
                    print("No rows found with missing toxic scores.")
                    return

                # Compute toxic scores for each row
                updates = []
                for id, thread_number, comment in rows:
                    toxic_flag, toxic_class, toxic_score = get_hs_score(comment or "normal text")
                    updates.append((toxic_flag, toxic_class, toxic_score, id, thread_number))
                    # logger.info("Got hatespeech score for 1 row.")

                try:
                    # Update the database in batches for efficiency
                    update_query = """
                    UPDATE posts
                    SET toxic_flag = data.toxic_flag,
                        toxic_class = data.toxic_class,
                        toxic_score = data.toxic_score
                    FROM (VALUES %s) AS data(toxic_flag, toxic_class, toxic_score, id, thread_number)
                    WHERE posts.id = data.id and posts.thread_number = data.thread_number;
                    """
                    execute_values(cursor, update_query, updates)
                    conn.commit()
                except Exception as e:
                    logger.info("Problem with update query in update_missing_toxic_scores")

                logger.info(f"Updated {len(updates)} rows successfully.")

            else:
                logger.info("Updated all the rows!")
                return
            
            # iteration += 1
            # if iteration > 2:
            #     break

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
    batch_size = 100
    update_missing_toxic_scores(batch_size)
