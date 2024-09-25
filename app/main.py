import uvicorn
from app.data.klines import BinanceKlines
from app.strategies.exceptions import SymbolChecking
from fastapi import HTTPException, FastAPI
from loguru import logger
from datetime import timedelta
from app.strategies.indicators import get_opportunity
from pydantic import BaseModel  # Import BaseModel
from app.volatility.egarch_model import VolatilityPredictor
app = FastAPI()

# Update Order and ResultOrder to inherit from BaseModel
class Order(BaseModel):  # Inherit from BaseModel
    symbol: str
    strategy: str

class ResultOrder(BaseModel):  # Inherit from BaseModel
    opportunity: str
    close_price: float  # Change from str to float
    message: str

import pandas as pd
@app.post("/now", response_model=ResultOrder)  # Specify the response model
async def test_now(order: Order):
    try:
        # Validate the symbol
        SymbolChecking.check_symbol(order.symbol)

        # Define interval
        interval = "1m"

        # Set start_time as yesterday
        start_time = int((pd.Timestamp.now(tz="UTC") - timedelta(days=2)).timestamp() * 1000)

        # Set end_time as the current time (now)
        end_time = int(pd.Timestamp.now().timestamp() * 1000)

        # Instantiate the BinanceKlines class with symbol, interval, start_time, and end_time
        klines_instance = BinanceKlines(order.symbol, interval, start_time, end_time)

        # Fetch the klines data
        data = klines_instance.fetch_and_wrangle_klines()
        print(data)
        logger.info(f"Data fetched successfully")

        # Define Strategy
        close_price, opportunity = get_opportunity(data, order.strategy)
        logger.info(f"Strategy of {order.strategy} applied successfully with Close price ({close_price}) and opportunity ({opportunity})")

        # Return the result
        return ResultOrder(opportunity=opportunity, close_price=close_price, message="Success")

    except SymbolChecking as e:
        logger.error(f"Invalid symbol: {e.symbol}")
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {e.symbol}")


class FitIn:
    symbol: str
    horizon: int

class FitOut:
    data_predicted : pd.DataFrame
    message: str



@app.post("/predict", response_model=FitOut)  # Specify the response model
async def test_future(order: Order):
    try:
        # Validate the symbol
        SymbolChecking.check_symbol(order.symbol)

        # Define interval
        interval = "1m"

        # Set start_time as yesterday
        start_time = int((pd.Timestamp.now(tz="UTC") - timedelta(days=2)).timestamp() * 1000)

        # Set end_time as the current time (now)
        end_time = int(pd.Timestamp.now().timestamp() * 1000)

        # Instantiate the BinanceKlines class with symbol, interval, start_time, and end_time
        klines_instance = BinanceKlines(order.symbol, interval, start_time, end_time)

        # Fetch the klines data
        data = klines_instance.fetch_and_wrangle_klines()
        print(data)
        logger.info(f"Data fetched successfully")

        # Define Strategy
        predictor = VolatilityPredictor(data)
        last_close_time = data["close_time"].iloc[-1]
        specific_time = last_close_time.replace(microsecond=0) + timedelta(seconds=1)
        predicted_df = predictor.run(horizon=horizon, resample_interval=resample_interval, user_specified_time=specific_time)
        logger.info(f"Predicted DataFrame {predicted_df.info}")

        # Return the result
        return ResultOrder(opportunity=opportunity, close_price=close_price, message="Success")

    except SymbolChecking as e:
        logger.error(f"Invalid symbol: {e.symbol}")
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {e.symbol}")
    


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
