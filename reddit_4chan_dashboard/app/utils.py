from collections import defaultdict
import psycopg2

# Function to fetch data from PostgreSQL database
def get_data_from_DB(query, database_url):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        result = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        return result
    except Exception as e:
        return [("Error", str(e))]
    

def mergeData(data1, data2):
    merged_data = defaultdict(int)
    
    for date, count in data1:
        merged_data[date] += count

    for date, count in data2:
        merged_data[date] += count
    
    # Convert back to a sorted list of tuples
    merged_data_list = sorted(merged_data.items())

    return merged_data_list


def mergeWith3columns(data1, data2):
    merged_data = defaultdict(int)

    for date, subreddit, count in data1 + data2:
        merged_data[(date, subreddit)] += count

    # Convert back to a sorted list of dictionaries
    merged_data_list = [{"date": date, "subreddit": subreddit, "count": count} 
                        for (date, subreddit), count in sorted(merged_data.items())]

    return merged_data_list
