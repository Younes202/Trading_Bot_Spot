import pandas as pd
from enum import Enum
class DataFrameUtils:
    """Utility methods for working with DataFrames."""

    @staticmethod
    def fill_missing_values(data, strategy='mean'):
        """Fill missing values in a DataFrame."""
        if strategy == 'mean':
            # Apply only to numeric columns
            numeric_data = data.select_dtypes(include=['number'])
            filled_numeric_data = numeric_data.fillna(numeric_data.mean())
            # Combine with non-numeric columns
            non_numeric_data = data.select_dtypes(exclude=['number'])
            return pd.concat([filled_numeric_data, non_numeric_data], axis=1)
        elif strategy == 'zero':
            # Apply filling zeros to all columns
            return data.fillna(0)
        else:
            raise ValueError("Unsupported strategy for filling missing values.")


# Define the Enum for Strategy Indicators
class StrategyIndicator(Enum):
    RSI = 'RSI'
    SMA = 'SMA'
    EMA = 'EMA'
    MACD = 'MACD'
    BOLLINGER_BANDS = 'BollingerBands'
    VOLUME = 'Volume'
    ATR = 'ATR'
    STOCHASTIC = 'Stochastic'
    FIBONACCI = 'Fibonacci'
    TRENDLINE = 'Trendline'
    RSI_MA_MACD = 'rsi_ma_macd'
    RSI_BB_VOLUME = 'rsi_bb_volume'
    RSI_TRENDLINES_PRICEPATTERNS = 'rsi_trendlines_pricepatterns'
    RSI_BB_ATR = 'rsi_bb_atr'
    RSI_FIB_MA = 'rsi_fib_ma'
    RSI_STOCH_BB = 'rsi_stoch_bb'
    RSI_VOLUME_MACD = 'rsi_volume_macd'



