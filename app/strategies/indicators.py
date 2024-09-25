import pandas_ta as ta
from app.strategies.schemas import DataFrameUtils, StrategyNames
from  app.strategies.exceptions import StrategyError

class Strategy:
    def __init__(self, data):
        """
        Initialize the IndividualStrategy with a dataset.

        Parameters
        ----------
        data : pandas.DataFrame
            The dataset containing price and volume information.
        """
        self.original_data = data.copy()  # Store the original dataset

    def _apply_strategy(self, strategy_function):
        """Helper method to apply a strategy function and fill missing values."""
        try:
            data_copy = self.original_data.copy()  # Work on a copy of the original data
            data_copy = strategy_function(data_copy)
            data_copy = DataFrameUtils.fill_missing_values(data_copy)
            return data_copy
        except Exception as e:
            raise StrategyError(f"Failed to apply strategy: {e}")

    def RSI_Strategy(self):
        def rsi(data):
            data['RSI'] = ta.rsi(data['close_price'], length=7)  # Use a shorter length for more frequent signals
            data['opportunity_type'] = data['RSI'].apply(
                lambda rsi: "Buy" if rsi < 30 else "Sell" if rsi > 70 else "Neutral"
            )
            return data
        return self._apply_strategy(rsi)

    def SMA_Strategy(self):
        def sma(data):
            data['SMA'] = ta.sma(data['close_price'], length=14)
            sma_diff = data['SMA'].diff()
            data['opportunity_type'] = sma_diff.apply(
                lambda diff: "Buy" if diff > 0 else "Sell" if diff < 0 else "Neutral"
            )
            return data
        return self._apply_strategy(sma)

    def EMA_Strategy(self):
        def ema(data):
            data['EMA_12'] = ta.ema(data['close_price'], length=12)
            data['EMA_26'] = ta.ema(data['close_price'], length=26)
            data['EMA_12_prev'] = data['EMA_12'].shift(1)
            data['EMA_26_prev'] = data['EMA_26'].shift(1)
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['EMA_12'] > row['EMA_26'] and row['EMA_12_prev'] <= row['EMA_26_prev']
                else "Sell" if row['EMA_12'] < row['EMA_26'] and row['EMA_12_prev'] >= row['EMA_26_prev']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(ema)

    def MACD_Strategy(self):
        def macd(data):
            macd_values = ta.macd(data['close_price'])
            data['MACD'] = macd_values['MACD_12_26_9']
            data['MACD_signal'] = macd_values['MACDs_12_26_9']
            data['MACD_prev'] = data['MACD'].shift(1)
            data['MACD_signal_prev'] = data['MACD_signal'].shift(1)
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['MACD'] > row['MACD_signal'] and row['MACD_prev'] <= row['MACD_signal_prev']
                else "Sell" if row['MACD'] < row['MACD_signal'] and row['MACD_prev'] >= row['MACD_signal_prev']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(macd)

    def BollingerBands_Strategy(self):
        def bbands(data):
            bands = ta.bbands(data['close_price'], length=20)
            data['BB_upper'] = bands['BBU_20_2.0']
            data['BB_middle'] = bands['BBM_20_2.0']
            data['BB_lower'] = bands['BBL_20_2.0']
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['close_price'] <= row['BB_lower'] else "Sell" if row['close_price'] >= row['BB_upper'] else "Neutral", 
                axis=1
            )
            return data
        return self._apply_strategy(bbands)

    def Volume_Strategy(self):
        def volume(data):
            data['close_prev'] = data['close_price'].shift(1)
            data['volume_prev'] = data['volume'].shift(1)
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['close_price'] > row['close_prev'] and row['volume'] > row['volume_prev']
                else "Sell" if row['close_price'] < row['close_prev'] and row['volume'] > row['volume_prev']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(volume)

    def ATR_Strategy(self):
        def atr(data):
            data['ATR'] = ta.atr(data['high'], data['low'], data['close_price'], length=14)
            atr_diff = data['ATR'].diff()
            data['opportunity_type'] = atr_diff.apply(
                lambda diff: "Buy" if diff > 0 else "Sell" if diff < 0 else "Neutral"
            )
            return data
        return self._apply_strategy(atr)

    def Stochastic_Strategy(self):
        def stochastic(data):
            stoch = ta.stoch(data['high'], data['low'], data['close_price'])
            data['Stoch_K'] = stoch['STOCHk_14_3_3']
            data['Stoch_D'] = stoch['STOCHd_14_3_3']
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['Stoch_K'] < 20 else "Sell" if row['Stoch_K'] > 80 else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(stochastic)

    def Fibonacci_Strategy(self):
        def fibonacci(data):
            # Simplified Fibonacci retracement levels for demonstration
            high = data['high'].max()
            low = data['low'].min()
            levels = [0.236, 0.382, 0.618, 1.0]
            for level in levels:
                data[f'Fib_{level}'] = high - (high - low) * level
            data['opportunity_type'] = data['close_price'].apply(
                lambda price: "Buy" if price < data['Fib_0.618'] else "Sell" if price > data['Fib_0.236'] else "Neutral"
            )
            return data
        return self._apply_strategy(fibonacci)

    def Trendline_Strategy(self):
        def trendline(data):
            # For simplicity, using a linear regression slope as a trend indicator
            data['trend_slope'] = ta.linearreg_slope(data['close_price'], length=14)
            data['opportunity_type'] = data['trend_slope'].apply(
                lambda slope: "Buy" if slope > 0 else "Sell" if slope < 0 else "Neutral"
            )
            return data
        return self._apply_strategy(trendline)

    # Hybrid Strategies

    def rsi_ma_macd_strategy(self):
        def rsi_ma_macd(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply MA
            data['SMA'] = ta.sma(data['close_price'], length=14)
            # Apply MACD
            macd_values = ta.macd(data['close_price'])
            data['MACD'] = macd_values['MACD_12_26_9']
            data['MACD_signal'] = macd_values['MACDs_12_26_9']
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['MACD'] > row['MACD_signal'] and row['close_price'] > row['SMA']
                else "Sell" if row['RSI'] > 70 and row['MACD'] < row['MACD_signal'] and row['close_price'] < row['SMA']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_ma_macd)

    def rsi_bb_volume_strategy(self):
        def rsi_bb_volume(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Bollinger Bands
            bands = ta.bbands(data['close_price'], length=20)
            data['BB_lower'] = bands['BBL_20_2.0']
            data['BB_upper'] = bands['BBU_20_2.0']
            # Apply Volume
            data['volume_prev'] = data['volume'].shift(1)
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['close_price'] <= row['BB_lower'] and row['volume'] > row['volume_prev']
                else "Sell" if row['RSI'] > 70 and row['close_price'] >= row['BB_upper'] and row['volume'] > row['volume_prev']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_bb_volume)

    def rsi_trendlines_pricepatterns_strategy(self):
        def rsi_trendlines_pricepatterns(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Trendline (linear regression slope)
            data['trend_slope'] = ta.linearreg_slope(data['close_price'], length=14)
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['trend_slope'] > 0
                else "Sell" if row['RSI'] > 70 and row['trend_slope'] < 0
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_trendlines_pricepatterns)

    def rsi_bb_atr_strategy(self):
        def rsi_bb_atr(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Bollinger Bands
            bands = ta.bbands(data['close_price'], length=20)
            data['BB_lower'] = bands['BBL_20_2.0']
            data['BB_upper'] = bands['BBU_20_2.0']
            # Apply ATR
            data['ATR'] = ta.atr(data['high'], data['low'], data['close_price'], length=14)
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['close_price'] <= row['BB_lower'] and data['ATR'].diff() > 0
                else "Sell" if row['RSI'] > 70 and row['close_price'] >= row['BB_upper'] and data['ATR'].diff() < 0
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_bb_atr)

    def rsi_fib_ma_strategy(self):
        def rsi_fib_ma(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Fibonacci
            high = data['high'].max()
            low = data['low'].min()
            data['Fib_0.618'] = high - (high - low) * 0.618
            data['Fib_0.236'] = high - (high - low) * 0.236
            # Apply MA
            data['SMA'] = ta.sma(data['close_price'], length=14)
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['close_price'] < data['Fib_0.618'] and row['close_price'] > row['SMA']
                else "Sell" if row['RSI'] > 70 and row['close_price'] > data['Fib_0.236'] and row['close_price'] < row['SMA']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_fib_ma)

    def rsi_stoch_bb_strategy(self):
        def rsi_stoch_bb(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Stochastic
            stoch = ta.stoch(data['high'], data['low'], data['close_price'])
            data['Stoch_K'] = stoch['STOCHk_14_3_3']
            # Apply Bollinger Bands
            bands = ta.bbands(data['close_price'], length=20)
            data['BB_lower'] = bands['BBL_20_2.0']
            data['BB_upper'] = bands['BBU_20_2.0']
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['Stoch_K'] < 20 and row['close_price'] <= row['BB_lower']
                else "Sell" if row['RSI'] > 70 and row['Stoch_K'] > 80 and row['close_price'] >= row['BB_upper']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_stoch_bb)

    def rsi_volume_macd_strategy(self):
        def rsi_volume_macd(data):
            # Apply RSI
            data['RSI'] = ta.rsi(data['close_price'], length=7)
            # Apply Volume
            data['volume_prev'] = data['volume'].shift(1)
            # Apply MACD
            macd_values = ta.macd(data['close_price'])
            data['MACD'] = macd_values['MACD_12_26_9']
            data['MACD_signal'] = macd_values['MACDs_12_26_9']
            # Determine opportunities based on a combination of signals
            data['opportunity_type'] = data.apply(
                lambda row: "Buy" if row['RSI'] < 30 and row['MACD'] > row['MACD_signal'] and row['volume'] > row['volume_prev']
                else "Sell" if row['RSI'] > 70 and row['MACD'] < row['MACD_signal'] and row['volume'] > row['volume_prev']
                else "Neutral",
                axis=1
            )
            return data
        return self._apply_strategy(rsi_volume_macd)



def get_opportunity(data, strategy_name):
    """
    Applies a strategy to the data and returns the close price and opportunity type in a dictionary.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataset containing price and volume information.
    strategy_name : str
        The name of the strategy to apply (e.g., 'RSI', 'SMA', etc.).

    Returns
    -------
    dict
        A dictionary with 'close_price' and 'opportunity_type' for each entry.
    """
    # Initialize the strategy with the given data
    strategy = Strategy(data)

    # Map the valid strategy names from StrategyNames to corresponding methods
    strategy_map = {
        'RSI': strategy.RSI_Strategy,
        'SMA': strategy.SMA_Strategy,
        'EMA': strategy.EMA_Strategy,
        'MACD': strategy.MACD_Strategy,
        'BollingerBands': strategy.BollingerBands_Strategy,
        'Volume': strategy.Volume_Strategy,
        'ATR': strategy.ATR_Strategy,
        'Stochastic': strategy.Stochastic_Strategy,
        'Fibonacci': strategy.Fibonacci_Strategy,
        'Trendline': strategy.Trendline_Strategy,
        'rsi_ma_macd': strategy.rsi_ma_macd_strategy,
        'rsi_bb_volume': strategy.rsi_bb_volume_strategy,
        'rsi_trendlines_pricepatterns': strategy.rsi_trendlines_pricepatterns_strategy,
        'rsi_bb_atr': strategy.rsi_bb_atr_strategy,
        'rsi_fib_ma': strategy.rsi_fib_ma_strategy,
        'rsi_stoch_bb': strategy.rsi_stoch_bb_strategy,
        'rsi_volume_macd': strategy.rsi_volume_macd_strategy,
    }

    # Check if the provided strategy_name is valid using StrategyNames schema
    if strategy_name not in StrategyNames.VALID_STRATEGIES:
        raise StrategyError(f"Invalid strategy name: {strategy_name}. Valid strategies are: {', '.join(StrategyNames.VALID_STRATEGIES)}")

    # Apply the chosen strategy to the data
    result_data = strategy_map[strategy_name]()

    # Return a dictionary with close_price and opportunity_type
    return result_data