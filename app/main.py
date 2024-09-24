import pandas as pd
from data.exceptions import BinanceAPIError
from strategies.exceptions import SymbolChecking
from fastapi import HTTPException
from loguru import logger
from datetime import timedelta
from data.klines import BinanceKlines
from fastapi import FastAPI

app = FastAPI

class Order():
    symbol: str
    message: str
class ResultOrder():
    opportunity: str
    close_price: str
    message: str

@app.post("/current_position")
@app.post("/current_position")
async def test_now(order: Order):
    try:
        # Validate the symbol
        SymbolChecking.check_symbol(order.symbol)
        
        # Define interval
        interval = "1m"
        
        # Set start_time as yesterday
        start_time = int((pd.Timestamp.now(tz="UTC") - timedelta(days=1)).timestamp() * 1000)
        
        # Set end_time as the current time (now)
        end_time = int(pd.Timestamp.now().timestamp() * 1000)
        
        # Instantiate the BinanceKlines class with symbol, interval, start_time, and end_time
        klines_instance = BinanceKlines(order.symbol, interval, start_time, end_time)
        
        # Fetch the klines data
        data = klines_instance.fetch_and_wrangle_klines()
        
        # Process and log the data
        logger.info(f"Data fetched successfully: {data[['close_time', 'open_time']]}")
        
        # Get the latest close price
        close_price = data.iloc[-1]['close']
        
        # Define Strategy
                    
        # Return the result
        return ResultOrder(opportunity=opportunity, close_price=close_price, message="Success")
    
    except SymbolChecking as e:
        logger.error(f"Invalid symbol: {e.symbol}")
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {e.symbol}")
    
    except BinanceAPIError as e:
        logger.error(f"An error occurred while fetching Binance data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching data from Binance")
    
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


interval = "1min"
# Set start_time as yesterday
start_time = int((pd.Timestamp.now(tz="UTC") - timedelta(days=1)).timestamp() * 1000)

# Set end_time as the current time (now)
end_time = int(pd.Timestamp.now().timestamp() * 1000)

# Instantiate the BinanceKlines class with updated time values
klines_instance = BinanceKlines(symbol, interval, start_time, end_time)

# Fetch the klines data from Binance
try:
    data = klines_instance.fetch_and_wrangle_klines()
    print(data[["close_time", "open_time"]])
    logger.info(f"Data fetched successfully.")

except (BinanceAPIError) as e:
    logger.error(f"An error occurred: {str(e)}")


