import os
import pandas as pd
from app.data.exceptions import BinanceAPIError
from app.data.schemas import KlineColumns
import httpx  # Use httpx for asynchronous HTTP requests
from loguru import logger
class BinanceKlines:
    def __init__(self, symbol, interval, start_time, end_time, chunk_size=3600000):  # Default chunk size = 1 hour in ms
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.chunk_size = chunk_size
        self.data = None
        logger.info(f"BinanceKlines initialized with symbol={symbol}, interval={interval}, start_time={start_time}, end_time={end_time}, chunk_size={chunk_size}")

    async def fetch_and_wrangle_klines(self, save_to_csv=True):
        try:
            # Loop through the time period in chunks
            current_start_time = self.start_time
            while current_start_time < self.end_time:
                current_end_time = min(current_start_time + self.chunk_size, self.end_time)
                logger.info(f"Fetching data from {current_start_time} to {current_end_time}")

                # Fetch data for the current chunk
                self.data = await self.fetch_data_from_binance(current_start_time, current_end_time)

                if not self.data:
                    logger.error("No data returned from fetch_data_from_binance.")
                    raise ValueError("No data fetched from Binance API.")
                
                df = self.convert_data_to_dataframe()

                # Save data to CSV immediately after each chunk is fetched
                if save_to_csv:
                    self.save_to_csv(df)

                # Move to the next chunk
                current_start_time = current_end_time

            return "Data fetched and saved successfully!"
        
        except Exception as e:
            logger.error(f"Error during fetching and wrangling klines: {e}")
            raise

    async def fetch_data_from_binance(self, start_time, end_time):
        base_url = "https://api.binance.com/api/v3/klines"
        all_klines = []

        async with httpx.AsyncClient() as client:
            params = {
                "symbol": self.symbol,
                "interval": self.interval.lower(),
                "startTime": start_time,
                "endTime": end_time
            }

            try:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                klines = response.json()

                if not klines:
                    logger.info(f"No more data found between {start_time} and {end_time}.")
                    return []

                all_klines.extend(klines)
                logger.info(f"Fetched {len(klines)} klines from Binance API between {start_time} and {end_time}.")

            except httpx.RequestError as e:
                logger.error(f"Error fetching data from Binance API: {str(e)}")
                raise BinanceAPIError(f"Error fetching data from Binance API: {str(e)}")
        
        return all_klines

    def convert_data_to_dataframe(self):
        if not self.data:
            logger.error("No data available for conversion.")
            raise ValueError("No data available to convert to DataFrame.")

        logger.info("Converting fetched data to DataFrame.")
        df = pd.DataFrame(self.data, columns=KlineColumns.COLUMNS)

        # Ensure columns exist before trying to convert types
        if 'open_price' in df.columns:
            df['open_price'] = df['open_price'].astype(float)
        if 'high_price' in df.columns:
            df['high_price'] = df['high_price'].astype(float)
        if 'low_price' in df.columns:
            df['low_price'] = df['low_price'].astype(float)
        if 'close_price' in df.columns:
            df['close'] = df['close_price'].astype(float)
        if 'volume' in df.columns:
            df['volume'] = df['volume'].astype(float)
        if 'quote_asset_volume' in df.columns:
            df['quote_asset_volume'] = df['quote_asset_volume'].astype(float)
        if 'number_of_trades' in df.columns:
            df['number_of_trades'] = df['number_of_trades'].astype(int)
        if 'taker_buy_base_asset_volume' in df.columns:
            df['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].astype(float)
        if 'taker_buy_quote_asset_volume' in df.columns:
            df['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].astype(float)

        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')
        df = df.drop(columns=["ignored"], axis=1, errors='ignore')
        
        logger.info("Data conversion to DataFrame completed.")
        return df

    def save_to_csv(self, df):
        # Ensure output directory exists
        output_dir = "klines_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save all chunks to the same CSV file (appending data)
        file_path = os.path.join(output_dir, f"{self.symbol}_{self.interval}_{self.start_time}_{self.end_time}.csv")

        # If the file exists, append; otherwise, create a new file
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
            logger.info(f"Appended data to {file_path}")
        else:
            df.to_csv(file_path, mode='w', header=True, index=False)
            logger.info(f"Saved data to {file_path}")
