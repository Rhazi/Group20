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
        self.prices.append(tick)
        signals = []

        if len(self.prices) >= self.long_window:
            short_ma = sum(self.prices[-self.short_window:]) / self.short_window
            long_ma = sum(self.prices[-self.long_window:]) / self.long_window

            if short_ma > long_ma:
                signals.append((OrderAction.BUY, tick.symbol, 100, tick.price))
            elif short_ma < long_ma:
                signals.append(('SELL', tick.symbol, 100, tick.price))

        return signals


class macd(Strategy):  # moving average convergence divergence
    def __init__(self, short_window: int = 15, large_window: int = 30, macd_window: int = 9):
        self.short_window = short_window
        self.large_window = large_window
        self.macd_window = macd_window
        self.prices = []

    def generate_signals(self, tick) -> list:
        self.prices.append(tick)
        signals = []

        if len(self.prices) >= self.large_window:
            fast_ema = self.ema(self.prices[-self.short_window:], self.short_window)[-1]
            slow_ema = self.ema(self.prices[-self.large_window:], self.large_window)[-1]
            macd_line = fast_ema - slow_ema
            signal_diff = [f-s for f,s in zip(self.ema(self.prices, self.short_window), self.ema(self.prices, self.large_window))]
            signal_line = self.ema(signal_diff, self.macd_window)[-1]
            if macd_line > signal_line:
                signals.append(['BUY', tick.symbol, 100, tick.price])
            else:
                signals.append(['SELL', tick.symbol, 100, tick.price])

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

#data = pd.read_csv('/Users/simorhazi/Desktop/uchicago/python/market_data.csv')
#print(data)
#strategie = macd()
#r=[]
#data["execution"] = None
#print(data)
#for i in range(data.shape[0]):
#    signal = strategie.generate_signals(data.iloc[i]["price"])
#    if not signal:signal = [0]
#    data.loc[i,"execution"]=signal[0]
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
