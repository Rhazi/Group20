from strategies import MovingAverageCrossoverStrategy
from models import Order, OrderStatus, OrderAction, ExecutionError, OrderError

class ExecutionEngine:
    def __init__(self, market_data: list):
        self.orders = []
        self.market_data = market_data
        self.MAStrategy = MovingAverageCrossoverStrategy()
        self.portfolio = {
            'capital': 100000.0, # starting capital in USD
            'positions': {}, # {'AAPL': {'quantity': 0, 'avg_price': 0.0}}
            'earnings': 0.0,
        }

    def generate_signals(self):
        signals = []
        for tick in self.market_data :
            signals.append(self.MAStrategy.generate_signals(tick))
        return signals

    def execute_order(self, order):
        # Assumption: All orders are filled immediately at the given price
        order.status = OrderStatus.FILLED.value
        self.orders.append(order)

        # Update portfolio
        if order.action == OrderAction.BUY.value:
            if self.portfolio['capital'] >= order.price * order.quantity:
                if order.symbol not in self.portfolio['positions']:
                    self.portfolio['positions'][order.symbol] = {'quantity': 0, 'avg_price': 0.0}

                pos = self.portfolio['positions'][order.symbol]
                total_cost = pos['avg_price'] * pos['quantity'] + order.price * order.quantity
                pos['quantity'] += order.quantity
                pos['avg_price'] = round(total_cost / pos['quantity'], 4)
                self.portfolio['capital'] -= order.price * order.quantity
            else:
                raise ExecutionError(f"Not enough capital to buy {order.symbol}")

        elif order.action == OrderAction.SELL.value:
            if order.symbol in self.portfolio['positions']:
                pos = self.portfolio['positions'][order.symbol]
                if pos['quantity'] >= order.quantity:
                    pos['quantity'] -= order.quantity
                    earnings = order.price * order.quantity
                    self.portfolio['capital'] += earnings
                    self.portfolio['earnings'] += earnings
                    if pos['quantity'] == 0:
                        pos['avg_price'] = 0.0
                else:
                    raise ExecutionError(f"Not enough quantity to sell for {order.symbol}")
            else:
                raise ExecutionError(f"No position to sell for {order.symbol}")
        
        return order
    
    def run(self):
        self.orders = []
        signals = self.generate_signals()
        for signal in signals:
            for action, symbol, quantity, price in signal:
                try:
                    order = Order(symbol, quantity, price, OrderStatus.UNFILLED.value, action)
                    executed_order = self.execute_order(order)
                    print(f"Executed Order: {executed_order.symbol}, {executed_order.quantity}, {executed_order.price}, {executed_order.status}, {executed_order.action}")
                    print(f"Portfolio: {self.portfolio}")
                except OrderError as e:
                    print(f"Order Creation Failed: {e}")
                except ExecutionError as e:
                    print(f"Order Execution Failed: {e}")
