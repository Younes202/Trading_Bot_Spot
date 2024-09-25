import pandas as pd
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


class StrategyNames:
    """Defines valid strategy names."""
    VALID_STRATEGIES = [
        "RSI", "SMA", "EMA", "MACD", "BollingerBands",
        "Volume", "ATR", "Stochastic", "Fibonacci", "Trendline",
        "rsi_ma_macd", "rsi_bb_volume", "rsi_trendlines_pricepatterns",
        "rsi_bb_atr", "rsi_fib_ma", "rsi_stoch_bb", "rsi_volume_macd"
    ]
