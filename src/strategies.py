from abc import ABC, abstractmethod
from models import MarketDataPoint
from models import OrderAction
from collections import deque
import statistics
import pandas as pd

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick) -> list:
        pass

class MAStrategy(Strategy):  # moving average crossover
    def __init__(self, short_window: int = 20, long_window: int = 50):  # maybe? consider making qty(=100) as configurable later
        self.__short_window = short_window
        self.__long_window = long_window
        self.__historical_data = pd.DataFrame(columns=['timestamp', 'price, symbol', 'volume'])

    def update_historical_data(self, tick: MarketDataPoint):
        new_row = pd.DataFrame([{
            'timestamp': tick.timestamp,
            'price': tick.price,
            'symbol': tick.symbol,
            'volume': tick.volume
        }])
        self.__historical_data = pd.concat([self.__historical_data, new_row], ignore_index=True)
        if len(self.__historical_data) > self.__long_window:
            self.__historical_data = self.__historical_data.iloc[-self.__long_window:]

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.update_historical_data(tick)
        signals = []

        if len(self.__historical_data) >= self.__long_window:
            # update moving averages
            self.__historical_data['MA_short'] = self.__historical_data['price'].rolling(window=self.__short_window).mean()
            self.__historical_data['MA_long'] = self.__historical_data['price'].rolling(window=self.__long_window).mean()

            # generate signals
            latest_data = self.__historical_data.iloc[-1]

            # determine quantity
            ADV = self.__historical_data['volume'].mean()
            MA_diff = latest_data['MA_short'] - latest_data['MA_long']
            


            if MA_diff > 0: # MA_short crosses above MA_long, Buy signal
                signals.append((OrderAction.BUY.value, tick.symbol, 100, tick.price))   
            elif MA_diff < 0: # MA_short crosses below MA_long, Sell signal
                signals.append((OrderAction.SELL.value, tick.symbol, 100, tick.price))
            else:
                signals.append((OrderAction.HOLD.value, tick.symbol, 100, tick.price))

        return signals        

class macd(Strategy):  # moving average convergence divergence
    def __init__(self, short_window: int = 15, large_window: int = 30, macd_window: int = 9):
        self.__short_window = short_window
        self.__large_window = large_window
        self.__macd_window = macd_window
        self.__prev = OrderAction.HOLD.value
        self.__prices = []

    def generate_signals(self, tick) -> list:
        self.__prices.append(tick.price)
        signals = []

        if len(self.__prices) >= self.__large_window:
            fast_ema = self.ema(self.__prices[-self.__short_window:], self.__short_window)[-1]
            slow_ema = self.ema(self.__prices[-self.__large_window:], self.__large_window)[-1]
            macd_line = fast_ema - slow_ema
            signal_diff = [f-s for f,s in zip(self.ema(self.__prices, self.__short_window), self.ema(self.__prices, self.__large_window))]
            signal_line = self.ema(signal_diff, self.__macd_window)[-1]
            if macd_line > signal_line:
                if self.__prev == OrderAction.BUY.value:
                    self.__prev = OrderAction.HOLD.value
                    signals.append((OrderAction.HOLD.value, tick.symbol, 100, tick.price))
                else:
                    signals.append((OrderAction.BUY.value, tick.symbol, 100, tick.price))
            else:
                if self.__prev == OrderAction.SELL.value:
                    self.__prev = OrderAction.HOLD.value
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
        self.__prices.append(tick.price)
        signals = []

        if len(self.__prices) >= self.__window:
            ma = sum(self.__prices) / self.__window
            std = statistics.pstdev(self.__prices)

            upper_band = ma + self.__num_std * std
            lower_band = ma - self.__num_std * std

            if tick.price < lower_band:
                signals.append((OrderAction.BUY.value, tick.symbol, self.__qty, tick.price))
            elif tick.price > upper_band:
                signals.append((OrderAction.SELL.value, tick.symbol, self.__qty, tick.price))
            else:
                signals.append((OrderAction.HOLD.value, tick.symbol, self.__qty, tick.price))

        return signals
        
