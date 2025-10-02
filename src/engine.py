from datetime import datetime
from typing import Dict, List
from models import MarketDataPoint, Order, OrderStatus, OrderAction, ExecutionError, OrderError, TickerBook
from strategies import Strategy


class ExecutionEngine:
    def __init__(self, market_data: Dict[any, List[MarketDataPoint]], strategies: dict):
        self.ticker_book: Dict[any, TickerBook] = {} # key: timestamp, value: TickerBook
        self.strategies: Dict[str, Strategy] = strategies
        self.portfolio: Dict[str, dict] = {} # key: strategy name, value: portfolio dict
        self.update_ticker_book(market_data)
        self.initalize_portfolio()
    
    def initalize_portfolio(self, initial_capital=1000000.0):
        # maintain separate portfolio for each strategy
        for strategy_name in self.strategies.keys():
            self.portfolio[strategy_name] = {
                'capital': initial_capital,
                'positions': {},
                'earnings': 0.0,
            }

    def update_ticker_book(self, market_data: Dict[str, List[MarketDataPoint]]):
        for timestamp, data_points in market_data.items():
            for data_point in data_points:
                if timestamp not in self.ticker_book:
                    self.ticker_book[timestamp] = TickerBook(orders=[], market_data=[])
                self.ticker_book[timestamp].market_data.append(data_point)

    def generate_signals(self, strategy):
        signals = []
        for t in sorted(self.ticker_book.keys()):
            tick_list = self.ticker_book[t].market_data
            for tick in tick_list:
                signals.append(strategy.generate_signals(tick))
        return signals

    def execute_order(self, order, portfolio):
        # Update portfolio
        if order.action == OrderAction.BUY.value:
            if portfolio['capital'] >= order.price * order.quantity:
                if order.symbol not in portfolio['positions']:
                    portfolio['positions'][order.symbol] = {'quantity': 0, 'avg_price': 0.0}

                earnings = order.price * order.quantity
                pos = portfolio['positions'][order.symbol]
                total_cost = pos['avg_price'] * pos['quantity'] + earnings
                pos['quantity'] += order.quantity
                pos['avg_price'] = round(total_cost / pos['quantity'], 4)
                portfolio['capital'] -= earnings
                portfolio['earnings'] -= earnings

                # fill order
                order.status = OrderStatus.FILLED.value

                # update ticker book
                self.ticker_book[order.timestamp].orders.append(order)
                self.orders.append(order)
            else:
                raise ExecutionError(f"Not enough capital to buy {order.symbol}. Current capital: {portfolio['capital']}, Required: {order.price * order.quantity}")
        elif order.action == OrderAction.SELL.value:
            if order.symbol in portfolio['positions']:
                pos = portfolio['positions'][order.symbol]
                if pos['quantity'] >= order.quantity:
                    pos['quantity'] -= order.quantity
                    earnings = order.price * order.quantity
                    portfolio['capital'] += earnings
                    portfolio['earnings'] += earnings
                    if pos['quantity'] == 0:
                        pos['avg_price'] = 0.0
                    
                    # fill order
                    order.status = OrderStatus.FILLED.value

                    # update ticker book
                    self.ticker_book[order.timestamp].orders.append(order)
                    self.orders.append(order)
                else:
                    raise ExecutionError(f"Not enough quantity to sell for {order.symbol}. Requested: {order.quantity}, Available: {pos['quantity']}")
            else:
                raise ExecutionError(f"No position to sell for {order.symbol}. Current positions: {portfolio['positions']}")
        
        return order
    
    def run(self):
        self.orders = []
        for strategy_name, strategy in self.strategies.items():
            print('\n' + '='*40)
            print(f'RUNNING STRATEGY: {strategy_name.upper()}')
            print('='*40 + '\n')
            
            signals = self.generate_signals(strategy)
            for signal in signals:
                for t, action, symbol, quantity, price in signal:
                    try:
                        order = Order(t, symbol, quantity, price, OrderStatus.UNFILLED.value, action, strategy_name)
                        executed_order = self.execute_order(order, self.portfolio[strategy_name])
                        # print(f"Executed Order: {executed_order.symbol}, {executed_order.quantity}, {executed_order.price}, {executed_order.status}, {executed_order.action}")
                        # print(f"Portfolio: {self.portfolio}")
                    except OrderError as e:
                        print(f"Order Creation Failed: {e}")
                    except ExecutionError as e:
                        print(f"Order Execution Failed: {e}")
