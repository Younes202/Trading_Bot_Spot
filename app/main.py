import uvicorn
from app.data.klines import BinanceKlines
from loguru import logger
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from app.data.model import Kline
from app.data.connection import Database
from app.data.schemas import KlineSchema
from app.data.connection import get_db
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
import pandas as pd
from app.data.connection import engine
from sqlalchemy.sql import text
from calendar import monthrange
import numpy as np

from fastapi.templating import Jinja2Templates
import webbrowser

templates = Jinja2Templates(directory="templates")


# Initialize FastAPI app
app = FastAPI()

# Initialize Database instance
db_manager = Database()




# Function to fetch data from the database
def fetch_data_from_db(start_open_time=None, end_close_time=None, interval='1m'):
    """
    Fetch filtered data from the PostgreSQL database and return as a DataFrame.
    """
    # Base query
    base_query = """
    SELECT open_time, close_time, open_price, high_price, low_price, close_price
    FROM klines
    """

    filters = []
    params = {}

    # Add filters only if they are provided
    if start_open_time:
        filters.append("open_time >= :start_open_time")
        params["start_open_time"] = start_open_time
    if end_close_time:
        filters.append("close_time <= :end_close_time")
        params["end_close_time"] = end_close_time

    # Add WHERE clause dynamically
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

        # Ensure that open_time and close_time are in datetime format for resampling
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])

    # Set the open_time as the index

    # Resample the data based on the provided interval
    df_resampled = df.resample(interval).agg({
        'open_time': 'first',    # First open_time in the interval
        'close_time': 'last',    # Last close_time in the interval
        'open_price': 'first',   # First open price in the interval
        'high_price': 'max',     # Highest price in the interval
        'low_price': 'min',      # Lowest price in the interval
        'close_price': 'last'    # Last close price in the interval
    })

    return df_resampled


@app.get("/", response_class=HTMLResponse)
async def display_data(
    request: Request,
    interval: str = Query(None, description="Candlestick interval, e.g., 1m, 5m, 1h"),
    month: str = Query(None, description="Selected month in YYYY-MM format"),
):
    data = pd.DataFrame()  # Initialize with an empty DataFrame
    interval = interval or "1d"  # Default interval is 1 day
    month = month or ""  # Default month is empty for the first load

    if interval and month:
        try:
            # Parse the month input
            year, month_num = map(int, month.split("-"))
            _, last_day = monthrange(year, month_num)
            start_open_time_dt = pd.Timestamp(f"{year}-{month_num:02d}-01")
            end_close_time_dt = pd.Timestamp(f"{year}-{month_num:02d}-{last_day} 23:59:59")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM.")

        try:
            # Fetch raw data based on filters
            data = fetch_data_from_db(
                start_open_time=start_open_time_dt,
                end_close_time=end_close_time_dt,
                interval=interval
            )
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return templates.TemplateResponse(
        "candlestick.html",
        {
            "request": request,
            "data": data.to_dict(orient="records") if not data.empty else [],
            "interval": interval,
            "month": month,
        }
    )



# Launch browser on startup
@app.on_event("startup")
async def launch_browser():
    webbrowser.open("http://127.0.0.1:8000")

# Run the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

 
"""
@app.post("/klines/fetch")
async def fetch_and_store_klines(
    symbol: str,
    interval: str,
    start_time: int,
    end_time: int,
    db: Session = Depends(get_db),
):

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
    try:
        klines = db.query(Kline).all()
        return klines
    except Exception as e:
        logger.error(f"Error retrieving klines: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve klines.")
"""