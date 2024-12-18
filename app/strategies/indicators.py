import pandas_ta as ta
from loguru import logger

class Strategy:
    def __init__(self, data, rsi_length=14, bollinger_length=20, bollinger_std_dev=2, atr_length=14, adx_length=30, sma_short_length=50, sma_long_length=200):
        self.data = data  # DataFrame containing historical price data
        self.rsi_length = rsi_length  # RSI period
        self.bollinger_length = bollinger_length  # Bollinger Bands period
        self.bollinger_std_dev = bollinger_std_dev  # Bollinger Bands standard deviation
        self.atr_length = atr_length  # ATR period
        self.adx_length=adx_length
        self.sma_short_length=sma_short_length
        self.sma_long_length=sma_long_length
        self.window=10

    
    def logic_strategy(self):
        # Key indicators for the strategy
        self.data['RSI'] = ta.rsi(self.data['close_price'], length=self.rsi_length)

        # Calculate Bollinger Bands
        bbands = ta.bbands(self.data['close_price'], length=self.bollinger_length, std=self.bollinger_std_dev)
        self.data['upper_band'], self.data['middle_band'], self.data['lower_band'] = bbands.iloc[:, 0], bbands.iloc[:, 1], bbands.iloc[:, 2]

        # Calculate ATR for dynamic target profit
        self.data['ATR'] = ta.atr(self.data['high_price'], self.data['low_price'], self.data['close_price'], length=self.atr_length)

        # Calculate ADX
        adx_result = ta.adx(self.data['high_price'], self.data['low_price'], self.data['close_price'], length=self.adx_length)
        self.data['ADX'] = adx_result[f'ADX_{self.adx_length}']

        # Moving Averages
        logger.info(f"Using SMA lengths: short={self.sma_short_length}, long={self.sma_long_length}")
        self.data['SMA_short'] = ta.sma(self.data['close_price'], length=self.sma_short_length)
        self.data['SMA_long'] = ta.sma(self.data['close_price'], length=self.sma_long_length)

        # Calculates support and resistance levels using rolling min and max.
        return self.data

    def preprocessing(self):
        # Remove rows with NaN values after adding indicators
        self.data = self.data.dropna()
        return self.data

    def get_decision(self):
        # Default no action

        # Buy signal: RSI < 40 and close > lower Bollinger Band
        self.data.loc[
            (self.data['RSI'] < 30) & (self.data['close_price'] > self.data['lower_band']),
            'Signal'
        ] = 1  # Buy signal


        return self.data
