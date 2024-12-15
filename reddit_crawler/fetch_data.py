import psycopg2
import csv

from dotenv import load_dotenv
load_dotenv()

import os

FAKTORY_SERVER_URL = os.environ.get("FAKTORY_SERVER_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")


def fetch_and_save_to_csv(table_name, output_file_path):
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(dsn=DATABASE_URL)
        cur = conn.cursor()

        # Execute the query to fetch all rows from the "posts" table
        cur.execute("SELECT * FROM "+table_name)

        # Fetch all rows
        rows = cur.fetchall()

        # Get column names from the cursor
        column_names = [desc[0] for desc in cur.description]

        # Specify the output CSV file path
        output_file = output_file_path

        # Open CSV file for writing
        with open(output_file, mode="w", newline="") as file:
            csv_writer = csv.writer(file)

            # Write column headers
            csv_writer.writerow(column_names)

            # Write the data rows
            csv_writer.writerows(rows)

        print(f"Data from 'posts' table has been written to {output_file}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
    
    finally:
        # Close the cursor and the connection
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":

    fetch_and_save_to_csv("posts", 
        "/home/mvenkatarama/Documents/DSSMP/Projects/project1_impl/reddit_crawler/data/posts/posts_table_oct_23.csv")
    
    fetch_and_save_to_csv("comments", 
        "/home/mvenkatarama/Documents/DSSMP/Projects/project1_impl/reddit_crawler/data/comments/comments_table_oct_23.csv")
    
