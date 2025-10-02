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

### added on Oct 2nd
class MACD(Strategy):
    def __init__(self, short_window: int = 12, long_window: int = 26, signal_window: int = 9, qty: int = 1):
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.qty = qty
        self.prices = deque(maxlen = self.long_window)
        self.prev_action = OrderAction.HOLD.value             # to check cross over 
        
        # to calculate signal, using macd
        self.macd_history = deque(maxlen=self.signal_window)  # Signal line 
        self.fast_ema_prev = None
        self.slow_ema_prev = None
        self.signal_ema_prev = None

        
    def generate_signals(self, tick):
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) >= self.long_window:
            # MACD line, using EMA of price 
            # decide alpha : smoothing weight, typically set as '2'
            alpha_fast = 2 / (self.short_window + 1)
            alpha_slow = 2 / (self.long_window + 1)
            price = tick.price

            # calculate moving average and MACD line as definition 
            self.fast_ema_prev = alpha_fast * price + (1 - alpha_fast) * (self.fast_ema_prev or price)
            self.slow_ema_prev = alpha_slow * price + (1 - alpha_slow) * (self.slow_ema_prev or price)
            # save in macd_history to calculate signal line
            macd_line = self.fast_ema_prev - self.slow_ema_prev
            self.macd_history.append(macd_line)

            # EMA of Signal Line
            # decide alpha : smoothing weight typically set as '2'
            alpha_signal = 2 / (self.signal_window + 1)
            # calculate moving average and signal line as defintion
            self.signal_ema_prev = alpha_signal * macd_line + (1 - alpha_signal) * (self.signal_ema_prev or macd_line)

            # select signals 
            if macd_line > self.signal_ema_prev:
                if self.prev_action != OrderAction.BUY.value:  # signal must came from neutral status
                    signals.append((OrderAction.BUY.value, tick.symbol, self.qty, tick.price))
                    self.prev_action = OrderAction.BUY.value
                else:
                    signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))
            else:
                if self.prev_action != OrderAction.SELL.value: # signal must came from neutral status
                    signals.append((OrderAction.SELL.value, tick.symbol, self.qty, tick.price))
                    self.prev_action = OrderAction.SELL.value
                else:
                    signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))

        return signals


## ---------------------------------------------------------------------------------------------------------------------
class RSI(Strategy):
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70, qty: int = 1):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.qty = qty
        self.prices = []
        self.prev_action = OrderAction.HOLD.value

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.prices.append(tick.price)
        signals = []

        if len(self.prices) > self.period:
            delta = [self.prices[i] - self.prices[i-1] for i in range(1, len(self.prices))]
            ups = [d if d > 0 else 0 for d in delta]
            downs = [-d if d < 0 else 0 for d in delta]

            roll_up = self.ewm(ups, self.period)
            roll_down = self.ewm(downs, self.period)
            rs = [u / d if d != 0 else 0 for u, d in zip(roll_up, roll_down)]
            rsi = [100 - (100 / (1 + r)) for r in rs]

            current_rsi = rsi[-1]

            if current_rsi < self.oversold:
                if self.prev_action != OrderAction.BUY.value:
                    signals.append((OrderAction.BUY.value, tick.symbol, self.qty, tick.price))
                    self.prev_action = OrderAction.BUY.value
                else:
                    signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))
            elif current_rsi > self.overbought:
                if self.prev_action != OrderAction.SELL.value:
                    signals.append((OrderAction.SELL.value, tick.symbol, self.qty, tick.price))
                    self.prev_action = OrderAction.SELL.value
                else:
                    signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))
            else:
                signals.append((OrderAction.HOLD.value, tick.symbol, self.qty, tick.price))

        return signals

    @staticmethod
    def ewm(values, period):
        alpha = 1 / period
        out = []
        prev = values[0]
        for v in values:
            val = alpha * v + (1 - alpha) * prev
            out.append(val)
            prev = val
        return out

        
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
