import uvicorn
from app.data.klines import BinanceKlines
from app.strategies.exceptions import SymbolChecking
from fastapi import HTTPException, FastAPI
from loguru import logger
from datetime import timedelta
from app.strategies.indicators import get_opportunity
from pydantic import BaseModel, validator, Field  # Import BaseModel
app = FastAPI()

# Define Pydantic models
class Order(BaseModel):
    symbol: str
    strategy: str




if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)