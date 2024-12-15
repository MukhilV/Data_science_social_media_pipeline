import pandas as pd
import matplotlib.pyplot as plt

# File paths for the posts and comments CSV files
posts_csv = "/home/mvenkatarama/Documents/DSSMP/Projects/project1_impl/reddit_crawler/data/posts/posts_table_oct_23.csv"
comments_csv = "/home/mvenkatarama/Documents/DSSMP/Projects/project1_impl/reddit_crawler/data/comments/comments_table_oct_23.csv"

# Load the CSV files into pandas DataFrames
posts_df = pd.read_csv(posts_csv)
comments_df = pd.read_csv(comments_csv)

# Convert the 'created_at' columns to datetime format
posts_df['created_at'] = pd.to_datetime(posts_df['created_at'])
comments_df['created_at'] = pd.to_datetime(comments_df['created_at'])

# Aggregate the data by day for posts and comments
posts_by_day = posts_df.groupby(posts_df['created_at'].dt.date).size()
comments_by_day = comments_df.groupby(comments_df['created_at'].dt.date).size()

# Plot the data
plt.figure(figsize=(12, 6))

# Plot for posts
plt.plot(posts_by_day.index, posts_by_day.values, label="Posts", marker='o', color='blue')

# Plot for comments
plt.plot(comments_by_day.index, comments_by_day.values, label="Comments", marker='o', color='green')

# Labels and title
plt.xlabel('Date')
plt.ylabel('Number of Entries')
plt.title('Data Collected Over Time (Posts and Comments)')
plt.legend()
plt.grid(True)

# Show the plot
plt.xticks(rotation=45)  # Rotate date labels for better readability
plt.tight_layout()
plt.show()
