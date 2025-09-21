from abc import ABC, abstractmethod
from models import MarketDataPoint
from models import OrderAction
from collections import deque
import statistics

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick) -> list:
        pass

class macd(Strategy):  # moving average convergence divergence
    def __init__(self, short_window: int = 15, large_window: int = 30, macd_window: int = 9):
        self.short_window = short_window
        self.large_window = large_window
        self.macd_window = macd_window
        self.prev = OrderAction.HOLD.value
        self.prices = []

    def generate_signals(self, tick) -> list:
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) >= self.large_window:
            fast_ema = self.ema(self.prices[-self.short_window:], self.short_window)[-1]
            slow_ema = self.ema(self.prices[-self.large_window:], self.large_window)[-1]
            macd_line = fast_ema - slow_ema
            signal_diff = [f-s for f,s in zip(self.ema(self.prices, self.short_window), self.ema(self.prices, self.large_window))]
            signal_line = self.ema(signal_diff, self.macd_window)[-1]
            if macd_line > signal_line:
                if self.prev == OrderAction.BUY.value:
                    self.prev = OrderAction.HOLD.value
                    signals.append((OrderAction.HOLD.value, tick.symbol, 100, tick.price))
                else:
                    signals.append((OrderAction.BUY.value, tick.symbol, 100, tick.price))
            else:
                if self.prev == OrderAction.SELL.value:
                    self.prev = OrderAction.HOLD.value
                    signals.append((OrderAction.HOLD.value, tick.symbol, 100, tick.price))
                else:
                    signals.append((OrderAction.SELL.value, tick.symbol, 100, tick.price))

        return signals

    def ema(self, prices, window) -> list:  # exponential moving average
        alpha = 2 / (window + 1)
        v = []
        prev = prices[0]
        for p in prices:
            ema = alpha * p + (1 - alpha) * prev
            v.append(ema)
            prev = ema
        return v

class BollingerBandsStrategy(Strategy):
    def __init__(self, window: int = 20, num_std: float = 2.0, qty: int = 100):  # maybe? consider making qty(=100) as configurable later

        self.__window = window
        self.__num_std = num_std
        self.__qty = qty
        self.__prices = deque(maxlen=window)

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) >= self.window:
            ma = sum(self.prices) / self.window
            std = statistics.pstdev(self.prices)

            upper_band = ma + self.num_std * std
            lower_band = ma - self.num_std * std

            if tick.price < lower_band:
                signals.append((OrderAction.BUY.value, tick.symbol, self.qty, tick.price))
            elif tick.price > upper_band:
                signals.append((OrderAction.SELL.value, tick.symbol, self.qty, tick.price))
            else:
                signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))

        return signals
        
