from dataclasses import dataclass
from enum import Enum
import datetime

@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime.datetime
    symbol: str
    price: float

class OrderStatus(Enum):
    UNFILLED = "UNFILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class OrderAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class OrderError(Exception):
    pass

class ExecutionError(Exception):
    pass    

class Order:
    def __init__(self, symbol: str, quantity: float, price: float, status: str, action: str = None):
        if quantity <= 0:
            raise OrderError("Quantity must be positive")
        if price <= 0:
            raise OrderError("Price must be positive")
        if not symbol or not isinstance(symbol, str):
            raise OrderError("Symbol must be a non-empty string")
        if status not in [ os.value for os in OrderStatus ]:
            raise OrderError("Invalid order status")

        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.status = status
        self.action = action

