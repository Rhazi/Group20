from strategies import MovingAverageCrossoverStrategy
from models import Order

class ExecutionEngine:
    def __init__(self, market_data: list):
        self.market_data = market_data
        self.MAStrategy = MovingAverageCrossoverStrategy()
        self.portfolio = {
            'positions': {}, # {'AAPL': {'quantity': 0, 'avg_price': 0.0}}
            'earnings': 0.0,
            'volatility': [] 
        }

    def generate_signals(self):
        signals = []
        for tick in self.market_data :
            signals.append(self.MAStrategy.generate_signals(tick))
        return signals

    def execute_order(self, order):
        # Simulate order execution
        order.status = "filled"
        self.orders.append(order)
        return order
    
    def run(self):
        self.orders = []
<<<<<<< Updated upstream
        signals = self.generate_signals()
        for signal in signals:
            for action, symbol, quantity, price in signal:
                order = Order(symbol, quantity, price, 'UNFILLED')
                executed_order = self.execute_order(order)
                print(f"Executed Order: {executed_order.symbol}, {executed_order.quantity}, {executed_order.price}, {executed_order.status}")
=======
        for strategy_name, strategy in self.strategies.items():
            print('\n' + '='*40)
            print(f'RUNNING STRATEGY: {strategy_name.upper()}')
            print('='*40 + '\n')
            
            signals = self.generate_signals(strategy)
            for signal in signals:
                for action, symbol, quantity, price in signal:
                    try:
                        order = Order(symbol, quantity, price, OrderStatus.UNFILLED.value, action, strategy_name)
                        executed_order = self.execute_order(order, self.portfolio[strategy_name])
                        # print(f"Executed Order: {executed_order.symbol}, {executed_order.quantity}, {executed_order.price}, {executed_order.status}, {executed_order.action}")
                        # print(f"Portfolio: {self.portfolio}")
                    except OrderError as e:
                        print(f"Order Creation Failed: {e}")
                    except ExecutionError as e:
                        print(f"Order Execution Failed: {e}")
>>>>>>> Stashed changes
