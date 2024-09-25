class StrategyError(Exception):
    """Base class for exceptions in the IndividualStrategy module."""
    def __init__(self, message="An error occurred in the IndividualStrategy module"):
        self.message = message
        super().__init__(self.message)

class SymbolChecking(Exception):
    """Exception raised for invalid symbols not paired with USDT."""
    def __init__(self, symbol):
        self.symbol = symbol
        self.message = f"Invalid symbol: {symbol}. Only USDT pairs are allowed."
        super().__init__(self.message)

    @staticmethod
    def check_symbol(symbol):
        # Define the valid USDT trading pairs
        VALID_SYMBOLS = [
            'BTCUSDT',
            'ETHUSDT',
            'BNBUSDT',
            'DOGSUSDT',  # Include your desired valid symbol
            'LTCUSDT',
            'XRPUSDT'
            ]
        
        if symbol not in VALID_SYMBOLS:
            raise SymbolChecking(symbol)
