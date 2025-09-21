from data_loader import load_data
from strategies import macd, BollingerBandsStrategy
from engine import ExecutionEngine
import numpy as np

def executed_orders() -> list:
    # 1. load data
    data_points = load_data()  # tick data points

    # 2. initialize strategies
    strategies = {
        'macd': macd(),
        'bollingerband': BollingerBandsStrategy(),
    }

    # 3. initialize engine
    engine = ExecutionEngine(data_points, strategies)

    # 4. run engine
    engine.run()

    return engine.orders


def trace_portfolio_log(orders_by_strategy, initial_capital=100000.0):
    portfolio_log = {}

    for strategy, orders in orders_by_strategy.items():
        portfolio_log[strategy] = []
        portfolio = {
            'capital': initial_capital,
            'positions': {},
            'earnings': 0.0
        }

        for o in orders:
            if o.action == 'BUY':
                cost = o.price * o.quantity
                portfolio['capital'] -= cost
                portfolio['earnings'] -= cost
                if o.symbol not in portfolio['positions']:
                    portfolio['positions'][o.symbol] = {'quantity': 0, 'avg_price': 0.0}
                pos = portfolio['positions'][o.symbol]
                total_cost = pos['avg_price'] * pos['quantity'] + cost
                pos['quantity'] += o.quantity
                pos['avg_price'] = total_cost / pos['quantity']

            elif o.action == 'SELL':
                revenue = o.price * o.quantity
                portfolio['capital'] += revenue
                portfolio['earnings'] += revenue
                pos = portfolio['positions'][o.symbol]
                pos['quantity'] -= o.quantity
                if pos['quantity'] == 0:
                    pos['avg_price'] = 0.0

            # log current state
            portfolio_log[strategy].append({
                'capital': portfolio['capital'],
                'positions': {k: v.copy() for k, v in portfolio['positions'].items()},
                'earnings': portfolio['earnings'],
                'last_order': o
            })

    return portfolio_log


def compute_performance(portfolio_log):
    performance = {}

    for strategy, logs in portfolio_log.items():

        # values contain time series of portfolio total value
        values = []
        for tick in logs:
            total_value = tick['capital'] + tick['positions']['AAPL']['quantity'] * tick['last_order'].price
            values.append(total_value)

        values = np.array(values)

        # return for each step : exception for last step
        returns = np.diff(values) / values[:-1] if len(values) > 1 else np.array([0])

        # return for total 
        total_return = (values[-1] - values[0]) / values[0]

        # Sharpe ratio(assume risk-free rate is 0)
        sharpe = 0.0
        if returns.std() != 0:
            sharpe = returns.mean() / returns.std()

        # MDD(max drawdown)
        roll_max = np.maximum.accumulate(values)
        drawdown = (values - roll_max) / roll_max
        max_dd = drawdown.min()

        performance[strategy] = {
            "Initial NPV": values[0],
            "Final NPV": values[-1],
            "Total Return": total_return,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_dd,
            "Time Series of NPV": values.tolist(),
        }

    return performance



if __name__ == "__main__":
    # 1. get executed orders
    orders = executed_orders()

    # 2. seperate by strategy
    orders_by_strategy = {}
    for order in orders:
        if order.strategy not in orders_by_strategy:
            orders_by_strategy[order.strategy] = []
        orders_by_strategy[order.strategy].append(order)

    # 3. generate trade log
    portfolio_log = trace_portfolio_log(orders_by_strategy, initial_capital=100000.0)

    # 4. test print for each strategy and its portfolio log
    for strategy, strat_orders in orders_by_strategy.items():
        print(f"\n--- {strategy.upper()} PORTFOLIO & ORDERS ---")
        for i, (order, state) in enumerate(zip(strat_orders, portfolio_log[strategy])):
            print(f"Step {i+1}: {order}")
            print(f"Capital={state['capital']:.2f}, Earnings={state['earnings']:.2f}, Positions={state['positions']}")

    # 5. compute performance as dictionary 
    performance = compute_performance(portfolio_log)
    print(performance)