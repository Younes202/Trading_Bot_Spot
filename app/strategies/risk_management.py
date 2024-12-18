from loguru import logger

class RiskManagement:
    def __init__(self, priceorder, currentprice, target_profit, stoploss, dollar_investment, atr, fees=0.1):
        self.priceorder = priceorder        # Entry price (buy price)
        self.currentprice = currentprice    # Current market price
        self.target_profit = target_profit  # Target profit percentage (entered manually)
        self.stoploss = stoploss            # Stop-loss percentage
        self.dollar_investment = dollar_investment  # Amount invested in dollars
        self.atr = atr                      # Average True Range (ATR)
        self.fees = fees / 100              # Trading fee as a decimal (e.g., 0.1% = 0.001)
        self.profit_or_loss = None          # Will be set when exit condition is triggered

    def calculate_price_from_target(self):
        """  
        Calculates the target price based on the provided target profit.
        Considers trading fees on both entry and exit.
        """
        # Target price adjusted for trading fees
        target_price = self.priceorder * (1 + self.target_profit / 100)
        target_price_after_fees = target_price * (1 + self.fees)  # Adjust for exit fees
        logger.info(f"Target price after including fees: {target_price_after_fees:.2f}")
        return target_price_after_fees

    def calculate_dollar_profit(self, target_price):
        """Calculates the dollar profit based on the target price."""
        # Number of units purchased
        units = self.dollar_investment / self.priceorder
        # Profit per unit
        profit_per_unit = target_price - self.priceorder
        # Total profit in dollars
        dollar_profit = profit_per_unit * units
        return dollar_profit

    def target_profit_exit(self):
        """Exit based on the target profit, adjusted by ATR."""
        target_price = self.calculate_price_from_target()  # Calculate target price after fees
        adjusted_target_price = target_price + (self.atr * 0.5)  # Adjust target based on ATR (can change multiplier)
        logger.info(f"Checking target profit exit condition at adjusted price: {adjusted_target_price:.2f}")

        if self.currentprice >= adjusted_target_price:
            # Calculate profit in dollars
            dollar_profit = self.calculate_dollar_profit(adjusted_target_price)
            total_dollars_after_profit = self.dollar_investment + dollar_profit
            self.profit_or_loss = dollar_profit  # Store the profit
            logger.info(f"Adjusted target price reached: {self.currentprice:.2f}. Profit: ${dollar_profit:.2f}. Total after profit: ${total_dollars_after_profit:.2f}. Exiting position.")
            return dollar_profit, total_dollars_after_profit
        return None, None

    def stop_loss_exit(self):
        """Exit based on stop-loss level, adjusted by ATR."""
        stop_loss_price = self.priceorder - (self.priceorder * (self.stoploss / 100))
        adjusted_stop_loss_price = stop_loss_price - (self.atr * 0.5)  # Adjust stop-loss based on ATR
        if self.currentprice <= adjusted_stop_loss_price:
            units = self.dollar_investment / self.priceorder
            loss_per_unit = self.priceorder - self.currentprice
            dollar_loss = loss_per_unit * units
            total_dollars_after_loss = self.dollar_investment - dollar_loss
            self.profit_or_loss = -dollar_loss  # Store the loss
            logger.info(f"Adjusted stop-loss price reached: {self.currentprice:.2f}. Loss: ${dollar_loss:.2f}. Total after loss: ${total_dollars_after_loss:.2f}. Exiting position.")
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
