from abc import ABC, abstractmethod
from models import MarketDataPoint

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
                signals.append(('BUY', tick.symbol, 100, tick.price))
            elif short_ma < long_ma:
                signals.append(('SELL', tick.symbol, 100, tick.price))
        
        return signals


class macd(Strategy): # moving average convergence divergence 
    def __init__(self, short_window: int = 15, large_window: int = 30, macd_window: int = 9): 
        self.short_window = short_window
        self.large_window = large_window
        self.macd_window = macd_window
        self.prices = []
    
    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []
    
        if len(self.prices) >= self.long_window:
            fast_ema = sum(ema(self.prices[-self.short_window:], self.short_window))/self.short_window
            slow_ema = sum(ema(self.prices[-self.large_window:], self.large_window))/self.long_window
            macd_line = fast_ema - slow_ema
            signal_line = sum(ema(macd_line, self.macd_window))/self.macd_window
    
            if macd_line > signal_line:
                signals.append((OrderAction.BUY, tick.symbol, 100, tick.price))
            else:
                signals.append((OrderAction.SELL, tick.symbol, 100, tick.price))
    
        return signals

def ema(prices, window): #exponential moving average
    alpha = 2 / (window + 1)
    v = []
    prev = prices[0]
    for p in prices:
        ema = alpha * p + (1 - alpha) * prev
        v.append(ema)
        prev = ema
    return v
