import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data
df = pd.read_csv('your_data.csv')

# Extract 'time' from the 'data' JSON
df['time'] = df['data'].apply(lambda x: pd.json_normalize(eval(x))['time'][0])

# Convert Unix timestamps to datetime
df['datetime'] = pd.to_datetime(df['time'], unit='s')

# Optionally, you can aggregate the data by day
df.set_index('datetime', inplace=True)
daily_counts = df.resample('D').count()  # Change 'D' to 'W' for weekly, etc.

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(daily_counts.index, daily_counts['id'], marker='o')
plt.title('Posts Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Posts')
plt.xticks(rotation=45)
plt.grid()
plt.show()
