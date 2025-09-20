from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt
from models import MarketDataPoint, OrderAction

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick) -> list:
        pass


class MovingAverageCrossoverStrategy(Strategy):
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
        self.prices = []

    def generate_signals(self, tick) -> list:
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) >= self.long_window:
            short_ma = sum(self.prices[-self.short_window:]) / self.short_window
            long_ma = sum(self.prices[-self.long_window:]) / self.long_window

            if short_ma > long_ma:
                signals.append((OrderAction.BUY.value, tick.symbol, 100, tick.price))
            elif short_ma < long_ma:
                signals.append((OrderAction.SELL.value, tick.symbol, 100, tick.price))

        return signals


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
                    signals.append((OrderAction.HOLD.value, tick.price, 100, tick.price))
                else:
                    signals.append((OrderAction.BUY.value, tick.price, 100, tick.price))
            else:
                if self.prev == OrderAction.SELL.value:
                    self.prev = OrderAction.HOLD.value
                    signals.append((OrderAction.HOLD.value, tick.price, 100, tick.price))
                else:
                    signals.append((OrderAction.SELL.value, tick.price, 100, tick.price))

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
                signals.append((OrderAction.BUY.value, tick.symbol, self.qty, tick.price))
            elif tick.price > upper_band:
                signals.append((OrderAction.SELL.value, tick.symbol, self.qty, tick.price))
            else:
                signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))


        return signals
        
#data = pd.read_csv('/Users/simorhazi/Desktop/uchicago/python/market_data.csv')
#print(data)
#strategie = macd()
#r=[]
#data["execution"] = [0 for _ in range(data.shape[0])]
#print(data)
#for i in range(data.shape[0]):
#    signal = strategie.generate_signals(data.iloc[i]["price"])
#    if not signal:signal = [[0,0,0,0,0]]
#    data.loc[i,"execution"]=signal[0][4]
#data["delta"] = data["price"].diff().fillna(0)
#data["execution"] = data["execution"].shift(1).fillna(0)
#data["pnl"] = data["delta"] * data["execution"]
#data["cumpnl"] = data["pnl"].cumsum()

#cash = 10
#final_cash = cash+data["cumpnl"]

#print(final_cash)
#ticker = "AAPL"
#plt.figure(figsize = (10,5))
#plt.plot(data.index, data["cumpnl"])
#plt.title(f"Cumulative profit and loss of {ticker} with a 1 share per trade trading policy")
#plt.xlabel("Date")
#plt.ylabel("Cumulative pnl")
#plt.show()
