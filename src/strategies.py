from abc import ABC, abstractmethod
from models import MarketDataPoint, OrderAction

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick:MarketDataPoint) -> list:
        pass

class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, short_window:int=5, long_window:int=20):
        self.short_window = short_window
        self.long_window = long_window
        self.prices = []
    
    def generate_signals(self, tick:MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []
        
        if len(self.prices) >= self.long_window:
            short_ma = sum(self.prices[-self.short_window:]) / self.short_window
            long_ma = sum(self.prices[-self.long_window:]) / self.long_window
            
            if short_ma > long_ma:
                signals.append((OrderAction.BUY, tick.symbol, 100, tick.price))
            elif short_ma < long_ma:
                signals.append((OrderAction.SELL, tick.symbol, 100, tick.price))
        
        return signals