from app.data.klines import BinanceKlines
from app.strategies.indicators import Strategy
import datetime
import asyncio
from loguru import logger

# Fetch Binance Klines data
async def main():
    # Define the parameters
    symbol = "BTCUSDT"  # Replace with your desired symbol
    interval = "1h"     # Replace with your desired interval

    # Calculate start_time and end_time dynamically
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = int((datetime.datetime.now() - datetime.timedelta(days=60)).timestamp() * 1000)

    print(f"Fetching data from {datetime.datetime.fromtimestamp(start_time / 1000)} to {datetime.datetime.fromtimestamp(end_time / 1000)}")

    # Instantiate the BinanceKlines class
    binance_klines = BinanceKlines(symbol, interval, start_time, end_time)

    # Fetch and wrangle the kline data
    try:
        df = await binance_klines.fetch_and_wrangle_klines()

        # Print the DataFrame
        print(df.head())
        str = Strategy(df)
        condition = str.run_strategy()
        if condition:
            logger.info("decision got with buy")
        else:
            logger.info("decision got None")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())