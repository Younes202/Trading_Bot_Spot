from sqlalchemy import Column, Integer, Float, DateTime, String
from app.data.connection import Base

class Kline(Base):
    __tablename__ = "klines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)



class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buy_price = Column(Float, nullable=False)  # Buy price at the time of opportunity
    buy_date = Column(DateTime, nullable=False)  # Date and time of buy opportunity
    sell_price = Column(Float, nullable=True)  # Sell price (nullable)
    sell_date = Column(DateTime, nullable=True)  # Date and time of sell opportunity (nullable)
    status = Column(String(20), nullable=False, default="in_progress")  # Status: 'in_progress' or 'completed'
