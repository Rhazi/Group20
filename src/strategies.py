from abc import ABC, abstractmethod
from models import MarketDataPoint
from models import OrderAction
from collections import deque, defaultdict
import statistics
import pandas as pd

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick) -> list:
        pass

class Volatility(Strategy):
    def __init__(self, k:float =0.1, atr: float = 1, equity: float = 10000, risk_pct: float = 0.01):
        self.__k=k
        self.__prior_high={str:float}
        self.__prior_low={str:float}
        self.__atr=atr
        self.__equity=equity
        self.__risk_pct=risk_pct

    def generate_signals(self, tick) -> list:
        signals = []

        long_threshold = self.__prior_high.get(tick.symbol,0) + self.__k * self.__atr
        short_threshold = self.__prior_low.get(tick.symbol,0) - self.__k * self.__atr

        self.__prior_high[tick.symbol] = tick.high
        self.__prior_low[tick.symbol] = tick.low

        # max capital at risk per trade
        max_risk = self.__equity * self.__risk_pct
        per_share_risk = self.__atr
        quantity = int(max_risk // per_share_risk)

        # check breakout conditions
        if tick.open >= long_threshold and quantity > 0:
            signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, 1, tick.open))

        elif tick.open <= short_threshold and quantity > 0:
            signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, 1, tick.open))

        else:
            signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, 1, tick.open))

        return signals

class MAStrategy(Strategy):  # moving average crossover
    def __init__(self, short_window: int = 20, long_window: int = 50):  # maybe? consider making qty(=100) as configurable later
        self.__short_window = short_window
        self.__long_window = long_window
        self.__historical_data = pd.DataFrame(columns=['timestamp', 'price, symbol', 'volume'])

    def update_historical_data(self, tick: MarketDataPoint):
        new_row = pd.DataFrame([{
            'timestamp': tick.timestamp,
            'price': tick.adj_close,
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
            # Adv = self.__historical_data['volume'].mean()
            MA_diff = latest_data['MA_short'] - latest_data['MA_long']
            # qty = int(min(Adv * 0.01, self.alpha * (abs(MA_diff)) / latest_data['MA_long']))

            if MA_diff > 0: # MA_short crosses above MA_long, Buy signal
                signals.append((tick.timestamp, OrderAction.BUY.value, latest_data['symbol'], 1, latest_data['price']))   
            elif MA_diff < 0: # MA_short crosses below MA_long, Sell signal
                signals.append((tick.timestamp, OrderAction.SELL.value, latest_data['symbol'], 1, latest_data['price']))

        return signals        

class macd(Strategy):  # moving average convergence divergence
    def __init__(self, short_window: int = 15, large_window: int = 30, macd_window: int = 9):
        self.__short_window = short_window
        self.__large_window = large_window
        self.__macd_window = macd_window
        self.__prev = {}
        self.__prices = defaultdict(list)

    def generate_signals(self, tick) -> list:
        self.__prices[tick.symbol].append(tick.close)
        if tick.symbol not in self.__prev:
            self.__prev[tick.symbol] = OrderAction.HOLD.value

        signals = []

        if len(self.__prices[tick.symbol]) >= self.__large_window:
            fast_ema = self.ema(self.__prices[tick.symbol][-self.__short_window:], self.__short_window)[-1]
            slow_ema = self.ema(self.__prices[tick.symbol][-self.__large_window:], self.__large_window)[-1]
            macd_line = fast_ema - slow_ema
            signal_diff = [f-s for f,s in zip(self.ema(self.__prices[tick.symbol], self.__short_window), self.ema(self.__prices[tick.symbol], self.__large_window))]
            signal_line = self.ema(signal_diff, self.__macd_window)[-1]
            if macd_line > signal_line:
                if self.__prev[tick.symbol] == OrderAction.BUY.value:
                    self.__prev[tick.symbol] = OrderAction.HOLD.value
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, 100, tick.close))
                else:
                    signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, 100, tick.close))
            else:
                if self.__prev[tick.symbol] == OrderAction.SELL.value:
                    self.__prev[tick.symbol] = OrderAction.HOLD.value
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, 100, tick.close))
                else:
                    signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, 100, tick.close))

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
        self.__prices.append(tick.close)

        signals = []

        if len(self.__prices) >= self.__window:
            ma = sum(self.__prices) / self.__window
            std = statistics.pstdev(self.__prices)

            upper_band = ma + self.__num_std * std
            lower_band = ma - self.__num_std * std

            if tick.close < lower_band:
                signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, self.__qty, tick.close))
            elif tick.close > upper_band:
                signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, self.__qty, tick.close))
            else:
                signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))

        return signals


class MACD(Strategy):
    def __init__(self, short_window: int = 12, long_window: int = 26, signal_window: int = 9, qty: int = 1):
        self.__short_window = short_window
        self.__long_window = long_window
        self.__signal_window = signal_window
        self.__qty = qty
        self.__prices = defaultdict(deque)
        self.__prev_action = {}  # to check cross over

        # to calculate signal, using macd
        self.__macd_history = defaultdict(deque)  # Signal line
        self.__fast_ema_prev = {}
        self.__slow_ema_prev = {}
        self.__signal_ema_prev = {}

    def generate_signals(self, tick):
        self.__prices[tick.symbol].append(tick.close)
        if tick.symbol not in self.__prev_action:
            self.__prev_action[tick.symbol] = OrderAction.HOLD.value
        if tick.symbol not in self.__fast_ema_prev:
            self.__fast_ema_prev[tick.symbol] = None
        if tick.symbol not in self.__slow_ema_prev:
            self.__slow_ema_prev[tick.symbol] = None
        if tick.symbol not in self.__signal_ema_prev:
            self.__signal_ema_prev[tick.symbol] = None

        signals = []

        if len(self.__prices[tick.symbol]) >= self.__long_window:
            # MACD line, using EMA of price
            # decide alpha : smoothing weight, typically set as '2'
            alpha_fast = 2 / (self.__short_window + 1)
            alpha_slow = 2 / (self.__long_window + 1)
            price = tick.close

            # calculate moving average and MACD line as definition
            self.__fast_ema_prev[tick.symbol] = alpha_fast * price + (1 - alpha_fast) * (self.__fast_ema_prev[tick.symbol] or price)
            self.__slow_ema_prev[tick.symbol] = alpha_slow * price + (1 - alpha_slow) * (self.__slow_ema_prev[tick.symbol] or price)
            # save in macd_history to calculate signal line
            macd_line = self.__fast_ema_prev[tick.symbol] - self.__slow_ema_prev[tick.symbol]
            self.__macd_history[tick.symbol].append(macd_line)

            # EMA of Signal Line
            # decide alpha : smoothing weight typically set as '2'
            alpha_signal = 2 / (self.__signal_window + 1)
            # calculate moving average and signal line as defintion
            self.__signal_ema_prev[tick.symbol] = alpha_signal * macd_line + (1 - alpha_signal) * (self.__signal_ema_prev[tick.symbol] or macd_line)

            # select signals
            if macd_line > self.__signal_ema_prev[tick.symbol]:
                if self.__prev_action[tick.symbol] != OrderAction.BUY.value:  # signal must came from neutral status
                    signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, self.__qty, tick.close))
                    self.__prev_action[tick.symbol] = OrderAction.BUY.value
                else:
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))
            else:
                if self.__prev_action[tick.symbol] != OrderAction.SELL.value:  # signal must came from neutral status
                    signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, self.__qty, tick.close))
                    self.__prev_action[tick.symbol] = OrderAction.SELL.value
                else:
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))

        return signals

class RSI(Strategy):
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70, qty: int = 1):
        self.__period = period
        self.__oversold = oversold
        self.__overbought = overbought
        self.__qty = qty
        self.__prices = defaultdict(list)
        self.__prev_action = {}

    def generate_signals(self, tick: MarketDataPoint) -> list:
        self.__prices[tick.symbol].append(tick.close)
        if tick.symbol not in self.__prev_action:
            self.__prev_action[tick.symbol] = OrderAction.HOLD.value
        signals = []

        if len(self.__prices[tick.symbol]) > self.__period:
            delta = [self.__prices[tick.symbol][i] - self.__prices[tick.symbol][i - 1] for i in range(1, len(self.__prices[tick.symbol]))]
            ups = [d if d > 0 else 0 for d in delta]
            downs = [-d if d < 0 else 0 for d in delta]

            roll_up = self.ewm(ups, self.__period)
            roll_down = self.ewm(downs, self.__period)
            rs = [u / d if d != 0 else 0 for u, d in zip(roll_up, roll_down)]
            rsi = [100 - (100 / (1 + r)) for r in rs]

            current_rsi = rsi[-1]

            if current_rsi < self.__oversold:
                if self.__prev_action[tick.symbol] != OrderAction.BUY.value:
                    signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, self.__qty, tick.close))
                    self.__prev_action[tick.symbol] = OrderAction.BUY.value
                else:
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))
            elif current_rsi > self.__overbought:
                if self.__prev_action[tick.symbol] != OrderAction.SELL.value:
                    signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, self.__qty, tick.close))
                    self.__prev_action[tick.symbol] = OrderAction.SELL.value
                else:
                    signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))
            else:
                signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, self.__qty, tick.close))

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
        
