import uvicorn
from app.data.klines import BinanceKlines
from loguru import logger
from fastapi import FastAPI, Depends, HTTPException
from app.data.model import Kline
from app.data.connection import Database
from app.data.schemas import KlineSchema
from app.data.connection import get_db
from sqlalchemy.orm import Session

# Initialize FastAPI app
app = FastAPI()

# Initialize Database instance
db_manager = Database()

@app.post("/klines/fetch")
async def fetch_and_store_klines(
    symbol: str,
    interval: str,
    start_time: int,
    end_time: int,
    db: Session = Depends(get_db),
):
    """
    Fetch klines from Binance and save to the database.
    """
    try:
        # Fetch and process data
        binance_klines = BinanceKlines(symbol, interval, start_time, end_time)
        dataframe = await binance_klines.fetch_and_wrangle_klines()

        # Save data to the database
        for _, row in dataframe.iterrows():
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
        return {"message": f"Klines for {symbol} saved successfully!"}

    except Exception as e:
        logger.error(f"Error fetching or saving klines: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch or save klines.")

@app.get("/klines", response_model=list[KlineSchema])
def get_all_klines( 
    db: Session = Depends(get_db),
):
    """
    Retrieve all klines from the database.
    """
    try:
        klines = db.query(Kline).all()
        return klines
    except Exception as e:
        logger.error(f"Error retrieving klines: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve klines.")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)