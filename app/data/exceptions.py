class BinanceKlinesError(Exception):
    """Base class for exceptions in the BinanceKlines module."""
    def __init__(self, message="An error occurred in the BinanceKlines module"):
        self.message = message
        super().__init__(self.message)
        
class BinanceAPIError(BinanceKlinesError):
    """Exception raised for errors in the Binance API."""
    def __init__(self, message="An error occurred with the Binance API"):
        super().__init__(message)