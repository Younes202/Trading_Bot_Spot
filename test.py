from app.data.klines import BinanceKlines
import datetime
import asyncio
from loguru import logger
import pandas as pd
import os
from app.data.model import Kline
from app.data.connection import get_db, Database
from sqlalchemy.orm import Session
from app.data.connection import engine
from sqlalchemy.sql import text
from datetime import datetime
from calendar import monthrange
from fastapi import HTTPException
import numpy as np
from app.strategies.indicators import Strategy
from app.strategies.risk_management import RiskManagement
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
# Step 1: Load the data into a DataFrame
"""file_path = "klines_data/merged_klines_ordered.csv"  # Replace with your CSV file path
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
cleaned_file_path = "klines_data/10-months-btc-kliens.csv"  # Replace with the desired output path
cleaned_data.to_csv(cleaned_file_path, index=False)

print(f"Cleaned data saved to {cleaned_file_path}")"""

# merged kliens csv

"""
# Directory containing CSV files
csv_dir = 'klines_data'
output_file = 'merged_klines_ordered.csv'

# Define the order of months based on filenames
month_order = [
    "01-btc-january.csv",
    "02-btc-february.csv",
    "03-btc-march.csv",
    "04-btc-april.csv",
    "05-btc-may.csv",
    "06-btc-june.csv",
    "07-btc-july.csv",
    "08-btc-august.csv",
    "09-btc-september.csv",
    "10-btc-october.csv",
    # Add any additional months here if present.
]

# Initialize an empty DataFrame for the merged data
merged_data = pd.DataFrame()

# Iterate through the month_order list and merge files
for csv_file in month_order:
    file_path = os.path.join(csv_dir, csv_file)
    if os.path.exists(file_path):  # Check if file exists
        df = pd.read_csv(file_path)
        merged_data = pd.concat([merged_data, df], ignore_index=True)
    else:
        print(f"File not found: {csv_file}")

# Save the merged DataFrame to a new CSV file
merged_data.to_csv(output_file, index=False)

print(f"Merged CSV saved to {output_file} in order.")
"""

"""
# Reads the CSV file and saves each row to the Kline table in the database.
db_manager = Database()

def save_csv_to_db(csv_file: str, db: Session):

    # Step 1: Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Step 2: Iterate through each row and save it into the database
    for _, row in df.iterrows():
        # Create each Kline object and insert it into the database
        db_manager.create(
            db,
            Kline,
            open_time=row["open_time"],
            close_time=row["close_time"],
            open_price=row["open_price"],
            high_price=row["high_price"],
            low_price=row["low_price"],
            close_price=row["close_price"],
            volume=row["volume"],
        )

    # Step 3: Commit the transaction to save the data
    db.commit()

    # Step 4: Success message
    print(f"Successfully saved data from {csv_file} to the database!")

# Get a session directly using get_db()
db = get_db()

# CSV file to save
csv_file = 'app/klines_data/10-months-btc-kliens.csv'

# Save the CSV data to the database
save_csv_to_db(csv_file, db)

# Close the session after operations
db.close()


"""

class TradingSystem:
    def __init__(self, **kwargs):
        # Initialize all the parameters here
        self.month = kwargs.get('month')
        self.rsi_length = kwargs.get('rsi_length', 14)
        self.bollinger_length = kwargs.get('bollinger_length', 20)
        self.bollinger_std_dev = kwargs.get('bollinger_std_dev', 2)
        self.atr_length = kwargs.get('atr_length', 14)
        self.adx_length = kwargs.get('adx_length', 30)
        self.sma_short_length = kwargs.get('sma_short_length', 50)
        self.sma_long_length = kwargs.get('sma_long_length', 200)
        self.target_profit = kwargs.get('target_profit', 5)  # Static target profit percentage (e.g., 5%)
        self.stoploss = kwargs.get('stoploss', 30)
        self.fees = kwargs.get('fees', 0.1)
        self.current_balance = kwargs.get('initial_investment', 100)  # Set the initial balance
        self.initial_investment = self.current_balance  # Store initial investment for ROI calculation
        self.trade_cycles = []
        self.in_position = False
        self.buy_price = 0
        self.buy_date = None

    def fetch_data_from_db(self):
        if self.month:
            try:
                # Parse month input
                year, month_num = map(int, self.month.split("-"))
                _, last_day = monthrange(year, month_num)
                start_open_time = pd.Timestamp(f"{year}-{month_num:02d}-01")
                end_close_time = pd.Timestamp(f"{year}-{month_num:02d}-{last_day} 23:59:59")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM.")

            try:
                # Initialize the base query
                base_query = """
                SELECT open_time, close_time, open_price, high_price, low_price, close_price
                FROM klines
                """
                filters = []
                params = {}

                # Add filters for start and end times
                if start_open_time:
                    filters.append("open_time >= :start_open_time")
                    params["start_open_time"] = start_open_time
                if end_close_time:
                    filters.append("close_time <= :end_close_time")
                    params["end_close_time"] = end_close_time

                # Add WHERE clause dynamically if filters exist
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
                return df
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



    def run_trading_cycle(self):
        data = self.fetch_data_from_db()

        if data.empty:
            logger.error("No data fetched from the database.")
            return

        # Calculate strategy indicators (RSI, Bollinger Bands)
        self.strategy = Strategy(data)
        data = self.strategy.logic_strategy()  # Add logic to calculate strategy indicators
        logger.info("Indicators calculated successfully")

        # Preprocess data to remove NaN values after applying indicators
        self.strategy.preprocessing()

        # Loop through the data for buy/sell signals
        for i in range(1, len(self.strategy.data)):
            current_row = self.strategy.data.iloc[i]

            # If in position, check if we should sell based on both static and dynamic profit
            if self.in_position:
                risk_management = RiskManagement(
                    priceorder=self.buy_price,
                    currentprice=current_row['close_price'],
                    target_profit=self.target_profit,
                    stoploss=self.stoploss,
                    dollar_investment=self.current_balance,
                    atr=current_row['ATR'],
                    fees=self.fees
                )

                # Check static profit and dynamic profit conditions
                # Check if we should exit
                if risk_management.should_exit():
                    if risk_management.stop_loss_exit():
                        logger.info("Exited position based on stop loss.")
                        dollar_profit = risk_management.profit_or_loss
                    elif risk_management.target_profit_exit():
                        dollar_profit = risk_management.profit_or_loss
                        logger.info("Exited position based on profit target.")
                    logger.info(
                        f"Sell at {current_row['close_price']} on {current_row['close_time']}, with the amount of : {dollar_profit:.2f}%"
                    )

                    # Record the trade cycle
                    self.trade_cycles.append({
                        'Buy Date': self.buy_date,
                        'Buy Price': self.buy_price,
                        'Buy Dollar': self.current_balance,
                        'Sell Date': current_row['close_time'],
                        'Sell Price': current_row['close_price'],
                        'Sell dollar': self.current_balance + dollar_profit,  # Account for fees
                        'Profit/Loss': dollar_profit,
                    })
                    self.current_balance += dollar_profit

                    self.in_position = False  # Exit position
                else:
                    logger.info("No Exited position.")

            # If not in position, check for buy signal using strategy
            if not self.in_position:
                self.strategy.data.loc[:, 'Signal'] = self.strategy.get_decision()  # Get buy signal
                
                if self.strategy.data['Signal'].iloc[i]:  # Buy condition detected
                    logger.info(f"Buy at {current_row['close_price']} on {current_row.name}")
                    self.buy_price = current_row['close_price']
                    self.buy_date = current_row['open_time']
                    self.in_position = True  # Enter position

    def calculate_metrics(self):
        """Calculate the requested performance and risk metrics."""
        if not self.trade_cycles:
            logger.error("No trades to analyze.")
            return {}

        trade_df = pd.DataFrame(self.trade_cycles)

        # Calculate profits and losses
        trade_df['Profit (%)'] = (
            (trade_df['Sell dollar'] - trade_df['Buy Dollar']) / trade_df['Buy Dollar'] * 100
        )
        trade_df['Cycle Time'] = (
            pd.to_datetime(trade_df['Sell Date']) - pd.to_datetime(trade_df['Buy Date'])
        ).dt.total_seconds() / 60

        # Sharpe Ratio
        daily_returns = trade_df['Profit (%)'] / 100
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() != 0 else np.nan

        # Volatility
        volatility = daily_returns.std()

        # Correlation and Covariance (dummy example with self.data as a DataFrame)
        if hasattr(self, 'strategy') and hasattr(self.strategy, 'data'):
            price_data = self.strategy.data[['close_price']]
            correlation = price_data.corr().iloc[0, 0] if not price_data.empty else np.nan
            covariance = price_data.cov().iloc[0, 0] if not price_data.empty else np.nan
        else:
            correlation = covariance = np.nan

        # Total Trades, Win Rate, Loss Rate
        total_trades = len(trade_df)
        wins = trade_df[trade_df['Profit (%)'] > 0]
        losses = trade_df[trade_df['Profit (%)'] <= 0]
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        loss_rate = len(losses) / total_trades * 100 if total_trades > 0 else 0

        # Average Profit, Average Loss
        avg_profit = wins['Profit (%)'].mean() if not wins.empty else 0
        avg_loss = losses['Profit (%)'].mean() if not losses.empty else 0

        # ROI, Net Profit
        roi = (self.current_balance - self.initial_investment) / self.initial_investment * 100
        net_profit = self.current_balance - self.initial_investment

        # Variance and Standard Deviation
        variance = daily_returns.var()
        std_deviation = daily_returns.std()

        # Average Time per Cycle
        avg_time_per_cycle = trade_df['Cycle Time'].mean() if not trade_df['Cycle Time'].empty else 0

        # Metrics Dictionary
        metrics = {
            'Sharpe Ratio': sharpe_ratio,
            'Volatility': volatility,
            'Correlation': correlation,
            'Covariance': covariance,
            'Total Trades': total_trades,
            'Win Rate (%)': win_rate,
            'Loss Rate (%)': loss_rate,
            'Average Profit (%)': avg_profit,
            'Average Loss (%)': avg_loss,
            'ROI (%)': roi,
            'Net Profit ($)': net_profit,
            'Variance': variance,
            'Standard Deviation': std_deviation,
            'Average Time per Cycle (minutes)': avg_time_per_cycle,
        }

        # Include profitable and loss trades for detailed display
        metrics['Profitable Trades'] = wins.to_dict(orient='records')
        metrics['Loss Trades'] = losses.to_dict(orient='records')
        metrics['Current Balance'] = self.current_balance

        return metrics

    def print_metrics(self):
        """Log and print the calculated metrics."""
        metrics = self.calculate_metrics()

        # Display metrics
        for key, value in metrics.items():
            if isinstance(value, (float, int)):
                logger.info(f"{key}: {value:.2f}")
            elif isinstance(value, list):
                logger.info(f"{key}: {len(value)} trades")
                for trade in value:
                    logger.info(trade)
            else:
                logger.info(f"{key}: {value}")




# Example parameters for TradingSystem
trading_params = {
    "month": "2024-01",
    "rsi_length": 14,
    "bollinger_length": 20,
    "bollinger_std_dev": 2,
    "atr_length": 14,
    "adx_length": 30,
    "sma_short_length": 50,
    "sma_long_length": 200,
    "target_profit": 2,
    "stoploss": 30,
    "fees": 0.1,
    "initial_investment": 150,
}

# Create a TradingSystem instance
trading_system = TradingSystem(**trading_params)

# Fetch data and run trading cycle
try:
    trading_system.fetch_data_from_db()  # Ensure data is fetched
    trading_system.run_trading_cycle()
    trading_system.print_metrics()      # Print calculated metrics
except Exception as e:
    logger.error(f"Error during execution: {e}")




"""
# Running the asynchronous code properly using asyncio.run() within the main guard
if __name__ == "__main__":

    #asyncio.run(run())
"""