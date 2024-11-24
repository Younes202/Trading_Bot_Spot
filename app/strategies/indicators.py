import pandas_ta as ta
from loguru import logger

class Strategy:
    def __init__(self, data, rsi_length=14, bollinger_length=20, bollinger_std_dev=2):
        self.data = data  # DataFrame containing historical price data
        self.rsi_length = rsi_length  # RSI period
        self.bollinger_length = bollinger_length  # Bollinger Bands period
        self.bollinger_std_dev = bollinger_std_dev  # Bollinger Bands standard deviation

    def logic_strategy(self):
        # Key indicators for the strategy
        self.data['RSI'] = ta.rsi(self.data['close'], length=self.rsi_length)

        # Calculate Bollinger Bands
        bbands = ta.bbands(self.data['close'], length=self.bollinger_length, std=self.bollinger_std_dev)

        # Dynamically map the correct columns for upper, middle, and lower bands
        upper_band_col = bbands.columns[0]  # First column: Upper Band
        middle_band_col = bbands.columns[1]  # Second column: Middle Band
        lower_band_col = bbands.columns[2]  # Third column: Lower Band

        self.data['upper_band'] = bbands[upper_band_col]
        self.data['middle_band'] = bbands[middle_band_col]
        self.data['lower_band'] = bbands[lower_band_col]
        return self.data

    def preprocessing(self):
        # Remove rows with NaN values after adding indicators
        self.data = self.data.dropna()
        return self.data

    def get_decision(self):
        # Ensure there's enough data to process
        if len(self.data) == 0:
            return False  # No data to evaluate

        # Access the last row for decision-making
        last_row = self.data.iloc[-1]  # Extract the last row
        last_rsi = last_row['RSI']
        last_close = last_row['close']
        last_lower_band = last_row['lower_band']

        # Decision-making based on strategy
        if last_rsi < 45 and last_close > last_lower_band:
            return True
        return False

    def run_strategy(self):
        self.logic_strategy()
        logger.info("indicators calculated successfully")
        self.preprocessing()
        logger.info("Preprocessing start")
        return self.get_decision()
