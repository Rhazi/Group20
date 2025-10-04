from models import OrderAction
from strategies import Strategy

class LongOnlyOnce(Strategy):
    def __init__(self):
        self.__hasBought = {}

    def generate_signals(self, tick):
        signals = []
        quantity = 1
        if tick.symbol not in self.__hasBought:
            self.__hasBought[tick.symbol] = 1
            if quantity < 0.1*tick.volume:
                signals.append((tick.timestamp, OrderAction.BUY.value, tick.symbol, quantity, tick.close))
        else:
            signals.append((tick.timestamp, OrderAction.HOLD.value, tick.symbol, quantity, tick.close))
        #last_day = False unwind on last day?
        #if tick.symbol not in self.__hasSold and last_day:
        #    signals.append((tick.timestamp, OrderAction.SELL.value, tick.symbol, quantity, tick.open))
        return signals