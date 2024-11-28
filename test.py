from app.data.klines import BinanceKlines
import datetime
import asyncio
from loguru import logger
import pandas as pd


# Fetch and Save to the csv .
""""
# Convert start_time and end_time from datetime to milliseconds
start_time = int(datetime.datetime(2024, 1, 1).timestamp() * 1000)  # January 1, 2024
end_time = int(datetime.datetime.now().timestamp() * 1000)  # Current time

# Create an instance of BinanceKlines
binance_klines = BinanceKlines(symbol="BTCUSDT", interval="1m", start_time=start_time, end_time=end_time)

# Define the async function
async def run():
    await binance_klines.fetch_and_wrangle_klines(save_to_csv=True)
"""


# remove duplicated rows on the csv .
"""
# Step 1: Load the data into a DataFrame
file_path = "klines_data/BTCUSDT_1m_1709164800000_1711843200000.csv"  # Replace with your CSV file path
data = pd.read_csv(file_path)

# Step 2: Check for duplicate rows
print(f"Number of duplicate rows: {data.duplicated().sum()}")

# Step 3: Optionally inspect duplicates
duplicates = data[data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Step 4: Drop duplicates while keeping the first occurrence
cleaned_data = data.drop_duplicates()

# Step 5: Save the cleaned data back to a new CSV
cleaned_file_path = "klines_data/03-btc_march.csv"  # Replace with the desired output path
cleaned_data.to_csv(cleaned_file_path, index=False)

print(f"Cleaned data saved to {cleaned_file_path}")
"""
# Running the asynchronous code properly using asyncio.run() within the main guard
"""if __name__ == "__main__":
    asyncio.run(run())
"""