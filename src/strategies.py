from abc import ABC, abstractmethod
from models_doohwan import MarketDataPoint
from collections import deque 
import statistics

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick:MarketDataPoint) -> list:
        pass

class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, short_window:int=5, long_window:int=20, qty:int=100):  # maybe? consider making qty(=100) as configurable later
        self.short_window = short_window
        self.long_window = long_window
        # self.prices = [] : not necessary to hold entire tick datas.
        self.prices = deque(maxlen=long_window)
        # notate qty 
        self.qty = qty
    
    def generate_signals(self, tick:MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []
        

        if len(self.prices) >= self.long_window:
            short_ma = sum(self.prices[-self.short_window:]) / self.short_window
            long_ma = sum(self.prices[-self.long_window:]) / self.long_window
            
            if short_ma > long_ma:
                signals.append(('BUY', tick.symbol, self.qty, tick.price))
            elif short_ma < long_ma:
                signals.append(('SELL', tick.symbol, self.qty, tick.price))
        
        return signals

class BollingerBandsStrategy(Strategy):
    def __init__(self, window: int = 20, num_std: float = 2.0, qty: int = 100):  # maybe? consider making qty(=100) as configurable later
    
        self.window = window
        self.num_std = num_std
        self.qty = qty
        self.prices = deque(maxlen=window)  

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) >= self.window:
            ma = sum(self.prices) / self.window
            std = statistics.pstdev(self.prices)

            upper_band = ma + self.num_std * std
            lower_band = ma - self.num_std * std

            if tick.price < lower_band:
                signals.append(('BUY', tick.symbol, self.qty, tick.price))
            elif tick.price > upper_band:
                signals.append(('SELL', tick.symbol, self.qty, tick.price))

        return signals