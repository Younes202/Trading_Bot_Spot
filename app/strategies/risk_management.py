from loguru import logger
import time

class RiskManagement:
    def __init__(self, priceorder, currentprice, target_profit, stoploss, dollar_investment, atr, fees=0.1, time_limit=7200):
        self.priceorder = priceorder        # Entry price (buy price)
        self.currentprice = currentprice    # Current market price
        self.target_profit = target_profit  # Target profit percentage (entered manually)
        self.stoploss = stoploss            # Stop-loss percentage
        self.dollar_investment = dollar_investment  # Amount invested in dollars
        self.atr = atr                      # Average True Range (ATR)
        self.fees = fees / 100              # Trading fee as a decimal (e.g., 0.1% = 0.001)
        self.profit_or_loss = None          # Will be set when exit condition is triggered
        self.entry_time = time.time()       # Track entry time (in seconds)
        self.time_limit = time_limit       # Time limit in seconds (default is 2 hours = 7200 seconds)

    def calculate_price_from_target(self):
        """Calculates the target price based on the provided target profit."""
        target_price = self.priceorder * (1 + self.target_profit / 100)
        target_price_after_fees = target_price * (1 + self.fees)
        logger.info(f"Target price after including fees: {target_price_after_fees:.2f}")
        return target_price_after_fees

    def calculate_dollar_profit(self, target_price):
        """Calculates the dollar profit based on the target price."""
        units = self.dollar_investment / self.priceorder
        profit_per_unit = target_price - self.priceorder
        dollar_profit = profit_per_unit * units
        return dollar_profit

    def target_profit_exit(self):
        """Exit based on the target profit, adjusted by ATR."""
        target_price = self.calculate_price_from_target()
        adjusted_target_price = target_price + (self.atr * 0.5)
        logger.info(f"Checking target profit exit condition at adjusted price: {adjusted_target_price:.2f}")
        if self.currentprice >= adjusted_target_price:
            dollar_profit = self.calculate_dollar_profit(adjusted_target_price)
            total_dollars_after_profit = self.dollar_investment + dollar_profit
            self.profit_or_loss = dollar_profit
            logger.info(f"Adjusted target price reached: {self.currentprice:.2f}. Profit: ${dollar_profit:.2f}. Total after profit: ${total_dollars_after_profit:.2f}. Exiting position.")
            return dollar_profit, total_dollars_after_profit
        return None, None

    def stop_loss_exit(self):
        """Exit based on stop-loss level, adjusted by ATR."""
        stop_loss_price = self.priceorder - (self.priceorder * (self.stoploss / 100))
        adjusted_stop_loss_price = stop_loss_price - (self.atr * 0.5)
        if self.currentprice <= adjusted_stop_loss_price:
            units = self.dollar_investment / self.priceorder
            loss_per_unit = self.priceorder - self.currentprice
            dollar_loss = loss_per_unit * units
            total_dollars_after_loss = self.dollar_investment - dollar_loss
            self.profit_or_loss = -dollar_loss
            logger.info(f"Adjusted stop-loss price reached: {self.currentprice:.2f}. Loss: ${dollar_loss:.2f}. Total after loss: ${total_dollars_after_loss:.2f}. Exiting position.")
            return True
        return False

    def time_limit_exit(self):
        """Exit based on time limit (2 hours)."""
        elapsed_time = time.time() - self.entry_time
        if elapsed_time > self.time_limit:
            logger.info(f"Time limit of {self.time_limit / 3600} hours reached. Exiting position due to time constraint.")
            return True
        return False

    def should_exit(self):
        """Main function to determine if any exit condition is met."""
        if self.stop_loss_exit():
            logger.info("Exiting position due to stop-loss condition.")
            return True  # Exit due to stop-loss condition
        
        dollar_profit, total_dollars = self.target_profit_exit()
        if dollar_profit is not None:
            logger.info(f"Exiting position due to reaching target profit of {self.target_profit:.2f}%. Profit: ${dollar_profit:.2f}. Total: ${total_dollars:.2f}")
            return True  # Exit due to reaching target profit
        
        if self.time_limit_exit():
            return True  # Exit due to time limit

        return False  # No exit condition met, hold the position





# Instantiate the RiskManagement class
"""rm = RiskManagement(
    priceorder=100,           # Entry price (e.g., $100 per unit)
    currentprice=120,         # Current price (e.g., $110 per unit)
    target_profit=2,         # Target profit (10%)
    stoploss=5,               # Stop-loss (5%)
    dollar_investment=1000,   # Total dollar investment (e.g., $1000)
    fees=0.1                  # Trading fee as percentage (e.g., 0.1%)
)

# Check if we should exit
if rm.should_exit():
    if rm.stop_loss_exit():
        logger.info("Exited position based on stop loss.")
    elif rm.target_profit_exit: 
        logger.info("Exited position based on profit target.")
else:
    logger.info("No Exited position.")"""

# Print profit or loss
