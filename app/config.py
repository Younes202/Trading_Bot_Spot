import os

class Settings:
    def __init__(self, symbol):
        self.symbol = symbol
        # Directory path for volatility trained models for the symbol
        self.volatility_path = f'./app/volatility/trained_models/{symbol}'
        # Ensure the directory exists
        os.makedirs(self.volatility_path, exist_ok=True)
