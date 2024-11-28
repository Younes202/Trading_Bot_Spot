from pydantic import BaseModel, ConfigDict
import datetime
class KlineColumns:
    """Defines the columns for the Binance Klines DataFrame."""
    COLUMNS = [
        "open_time", "open_price", "high_price", "low_price", "close_price", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignored"
    ]


class KlineSchema(BaseModel):
    open_time: datetime
    close_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
