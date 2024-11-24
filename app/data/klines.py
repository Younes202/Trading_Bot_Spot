# app/data/klines.py

from app.data.exceptions import BinanceAPIError
from app.data.schemas import KlineColumns
import pandas as pd
import httpx  # Use httpx for asynchronous HTTP requests
from loguru import logger

class BinanceKlines:
    def __init__(self, symbol, interval, start_time, end_time):
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time
        self.data = None
        logger.info(f"BinanceKlines initialized with symbol={symbol}, interval={interval}, start_time={start_time}, end_time={end_time}")

    async def fetch_and_wrangle_klines(self):
        try:
            self.data = await self.fetch_data_from_binance()
            if not self.data:  # Check if data is empty
                logger.error("No data returned from fetch_data_from_binance.")
                raise ValueError("No data fetched from Binance API.")
            
            return self.convert_data_to_dataframe()
        except Exception as e:
            logger.error(f"Error during fetching and wrangling klines: {e}")
            raise


    async def fetch_data_from_binance(self):
        base_url = "https://api.binance.com/api/v3/klines"
        all_klines = []
        current_start_time = self.start_time

        async with httpx.AsyncClient() as client:
            while current_start_time < self.end_time:
                params = {
                    "symbol": self.symbol,
                    "interval": self.interval.lower(),
                    "startTime": current_start_time,
                    "endTime": self.end_time
                }

                try:
                    response = await client.get(base_url, params=params)
                    response.raise_for_status()
                    klines = response.json()

                    if not klines:
                        break  # Break the loop if no more data is returned

                    all_klines.extend(klines)
                    logger.info(f"Fetched {len(klines)} klines from Binance API.")

                    current_start_time = klines[-1][0] + 1  # Add 1 ms to avoid overlap

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
