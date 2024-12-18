from binance.client import Client
from binance.exceptions import BinanceAPIException

# Replace with your actual API key and secret
api_key = 'F3ckZIGICJNVuIpB6Op4dWcOBpPnIVzAAHUYq4tasGTH6Qqvjted2oBW7vUGeUqL'
api_secret = 'q9kmxILK42ixinbKmQp6aU5bDGzJK27BLmbqNrZzdDAIFNEXi9GsAjvwU2OSYw1V'

# Initialize the Binance client with both API key and secret
client = Client(api_key, api_secret)

# Example: Get account information (balance) from your futures account
# Get funding wallet balance

# Function to buy BTC using USDT amount
def buy_bitcoin_with_usdt(usdt_amount):
    try:
        # Get the current balance of USDT in the spot account
        balance = client.get_asset_balance(asset='USDT')
        usdt_balance = float(balance['free'])
        
        # Check if the user has enough USDT balance
        if usdt_balance >= usdt_amount:
            # Get the current market price of Bitcoin in USDT
            btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
            market_price = float(btc_price['price'])
            
            # Calculate how much BTC can be bought with the given USDT amount
            btc_amount = usdt_amount / market_price
            
            # Place a market buy order
            order = client.order_market_buy(
                symbol="BTCUSDT",  # Symbol to trade (BTC/USDT)
                quantity=round(btc_amount, 6)  # Quantity of BTC to buy, rounded to 6 decimals
            )
            
            print(f"Market buy order placed for {round(btc_amount, 6)} BTC using {usdt_amount} USDT at a price of {market_price} USDT/BTC")
            return order
        else:
            print(f"Not enough USDT balance. You only have {usdt_balance} USDT, but you need {usdt_amount} USDT.")
            return None

    except BinanceAPIException as e:
        print(f"Binance API Exception: {e}")
    except Exception as e:
        print(f"Other Exception: {e}")

# Example usage
usdt_amount_to_invest = 1000  # Specify the amount of USDT you want to invest in Bitcoin
buy_bitcoin_with_usdt(usdt_amount_to_invest)