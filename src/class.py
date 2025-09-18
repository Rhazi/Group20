from dataclasses import dataclass
import datetime

@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime.datetime
    symbol: str
    price: float

class Order:
    def __init__(self, symbol: str, quantity: float, price: float, status: str):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.status = status

class Portfolio:
    def __init__(self):
        self.positions = {} # {'AAPL': {'quantity': 0, 'avg_price': 0.0}}
        self.earnings = 0.0
        self.volatility = [] 

class OrderError(Exception):
    pass

class ExecutionError(Exception):
    pass
