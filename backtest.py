import pandas as pd
from calendar import monthrange
from app.data.connection import engine
from sqlalchemy.sql import text
import backtrader as bt


# Define the Strategy
class TradingStrategy(bt.Strategy):
    # Define parameters that can be set when initializing the strategy
    params = (
        ("rsi_length", 14),
        ("bollinger_length", 20),
        ("bollinger_std_dev", 2),
        ("atr_length", 14),
        ("adx_length", 30),
        ("sma_short_length", 50),
        ("sma_long_length", 200),
        ("target_profit", 5),
        ("stoploss", 30),
        ("fees", 0.1),
        ("initial_investment", 100),
    )

    def __init__(self):
        # Define indicators
        self.rsi = bt.indicators.RSI(period=self.params.rsi_length)
        self.bollinger = bt.indicators.BollingerBands(period=self.params.bollinger_length, dev=self.params.bollinger_std_dev)
        self.atr = bt.indicators.AverageTrueRange(period=self.params.atr_length)
        self.adx = bt.indicators.ADX(period=self.params.adx_length)
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_short_length)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_long_length)

        self.in_position = False
        self.buy_price = 0
        self.buy_date = None
        self.trade_cycles = []
        self.current_balance = self.params.initial_investment

    def next(self):
        """Main logic for each bar"""
        # If in position, manage the trade (risk management)
        if self.in_position:
            # Calculate profit/loss based on strategy conditions (target profit, stop-loss, ATR, ADX)
            current_price = self.data.close[0]
            profit_loss = (current_price - self.buy_price) / self.buy_price * 100

            # Check target profit or stop-loss
            if profit_loss >= self.params.target_profit or profit_loss <= -self.params.stoploss:
                self.sell()
                self.in_position = False
                self.trade_cycles.append({
                    'Buy Date': self.buy_date,
                    'Sell Date': self.data.datetime.date(0),
                    'Buy Price': self.buy_price,
                    'Sell Price': current_price,
                    'Profit/Loss': profit_loss,
                    'Balance After Trade': self.current_balance
                })

        # If not in position, check for buy signal
        if not self.in_position:
            # Example entry signal: if RSI is low (buying condition)
            if self.rsi < 30 and self.data.close[0] > self.sma_short[0]:
                self.buy_price = self.data.close[0]
                self.buy_date = self.data.datetime.date(0)
                self.buy()
                self.in_position = True

    def stop(self):
        """Print summary at the end of the backtest"""
        print(f"Final Balance: {self.current_balance}")
        print(f"Total Trades: {len(self.trade_cycles)}")
        # Print profitable and losing trades
        positive_trades = [cycle for cycle in self.trade_cycles if cycle['Profit/Loss'] > 0]
        negative_trades = [cycle for cycle in self.trade_cycles if cycle['Profit/Loss'] < 0]

        print(f"Profitable Trades: {len(positive_trades)}")
        print(f"Losing Trades: {len(negative_trades)}")

        # Calculate and print other metrics such as ROI, win rate, etc.
        roi = (self.current_balance - self.params.initial_investment) / self.params.initial_investment * 100
        print(f"ROI: {roi:.2f}%")


# Create the Backtrader Engine (Cerebro)
def run_backtest(month=None):
    # Create an instance of Cerebro
    cerebro = bt.Cerebro()

    # Set up the data feed (you can replace this with real historical data from a database)
    data = bt.feeds.PandasData(dataname=fetch_data_from_db(month))  # Fetch data function

    # Add the data feed to the engine
    cerebro.adddata(data)

    # Set the initial cash in the broker (e.g., $100)
    cerebro.broker.set_cash(100)

    # Set the commission (e.g., 0.1%)
# Set the commission (e.g., 0.1%)
    cerebro.broker.setcommission(commission=0.001)

    # Set the size of each trade (e.g., 1 unit)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # Add the strategy to the engine
    cerebro.addstrategy(TradingStrategy)

    # Print starting cash
    print(f"Starting Portfolio Value: ${cerebro.broker.get_value()}")

    # Run the backtest
    cerebro.run()

    # Print final results
    print(f"Ending Portfolio Value: ${cerebro.broker.get_value()}")


def fetch_data_from_db(month=None):
    """
    Fetch data from the database or external source for the specified month
    and return it as a pandas DataFrame.
    """
    if month:
        try:
            # Parse month input (assumes 'YYYY-MM' format)
            year, month_num = map(int, month.split("-"))
            _, last_day = monthrange(year, month_num)
            start_open_time = pd.Timestamp(f"{year}-{month_num:02d}-01")
            end_close_time = pd.Timestamp(f"{year}-{month_num:02d}-{last_day} 23:59:59")
        except ValueError:
            raise Exception("Invalid month format. Use YYYY-MM.")

        base_query = """
        SELECT open_time, close_time, open_price, high_price, low_price, close_price
        FROM klines
        """

        filters = []
        params = {}

        # Add filters only if they are provided
        if start_open_time:
            filters.append("open_time >= :start_open_time")
            params["start_open_time"] = start_open_time
        if end_close_time:
            filters.append("close_time <= :end_close_time")
            params["end_close_time"] = end_close_time

        # Add WHERE clause dynamically
        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        
        # Add ordering
        base_query += " ORDER BY open_time ASC"

        # Fetch data
        with engine.connect() as connection:
            df = pd.read_sql_query(
                text(base_query),
                con=connection,
                params=params,
            )

        # Convert 'open_time' and 'close_time' to datetime
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')  # Adjust 'unit' as per database format
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')  # If applicable

        return df



# Example usage:
if __name__ == "__main__":
    # Run the backtest for a specific month
    run_backtest(month="2024-10")
