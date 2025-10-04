import pandas as pd
from strategies import MAStrategy, Volatility, macd, RSI
from BenchmarkStrategy import LongOnlyOnce
from engine import ExecutionEngine
from PriceLoader_reporting import PriceLoader




def limited_period_total500(start_date, end_date,data_points): 
    # 1. load data
    print("sneak peek of data_points start ##########################################################################")
    print(data_points[0])  
    print("sneak peek of data_points end ##########################################################################")
    
    # 
    strategies = {'MA': MAStrategy(), 'LO' : LongOnlyOnce(), 'VOL':Volatility(), 'MACD' : macd(), 'RSI':RSI()}
    strategies = {'LO' : LongOnlyOnce()}    
    
    # 3. intilialize engine
    engine = ExecutionEngine(data_points, strategies)
    # 4. run engine
    engine.run()
    orders = engine.orders

    return orders



def build_portfolio_timeseries(orders, data_points, strategy_name, start_date, initial_capital=1_000_000):
    # orders_by_strategy filter
    orders = [o for o in orders if o.strategy == strategy_name]

    # sort by timestamp
    all_dates = sorted(pd.to_datetime(list(data_points.keys())))
    records = []

    # first row: initial capital, no positions
    first_record = {"date": pd.to_datetime(start_date), "total_value": initial_capital, "cash": initial_capital}
    # set 0 for rest of the tickers
    tickers = set(o.symbol for o in orders)
    for t in tickers:
        first_record[t] = 0.0
    records.append(first_record)

    # reset portfolio
    portfolio = {"cash": initial_capital}
    for t in tickers:
        portfolio[t] = 0.0

    for dt in all_dates:
        dt_records = {"date": dt}
        # execute orders for that date
        for o in orders:
            if o.timestamp == dt:
                if o.action == "BUY":
                    portfolio[o.symbol] += o.quantity
                    portfolio["cash"] -= o.quantity * o.price
                elif o.action == "SELL":
                    portfolio[o.symbol] -= o.quantity
                    portfolio["cash"] += o.quantity * o.price
        # compute total value
        total_value = portfolio["cash"]
        mp_list = {mp.symbol: mp.adj_close for mp in data_points[dt]}
        for sym in tickers:
            total_value += portfolio[sym] * mp_list.get(sym, 0.0)
            dt_records[sym] = portfolio[sym] * mp_list.get(sym, 0.0)
        dt_records["cash"] = portfolio["cash"]
        dt_records["total_value"] = total_value
        records.append(dt_records)

    df_ts = pd.DataFrame(records).set_index("date").sort_index()
    return df_ts


if __name__ == "__main__":
    # 1. load data
    price_loader = PriceLoader()
    start_date="2024-09-01"
    end_date="2024-09-06"
    data_points = price_loader.load_data(start_date = start_date, end_date=end_date)

    orders = limited_period_total500(start_date, end_date, data_points)
    print("Sneak peek of orders start ##########################################################################")
    print(orders[:5])  
    print("Sneak peek of orders end ##########################################################################")

    # 2. seperate by strategy and generate trade log
    df_ts = build_portfolio_timeseries(orders, data_points, "LO", start_date, initial_capital=1000000)
    df_ts = df_ts.iloc[1:]
    print(df_ts.head())

    # print("Logging...")
    # print(portfolio_log)
    # # 4. test print for each strategy and its portfolio log
    # for strategy, strat_orders in orders_by_strategy.items():
    #     print(f"\n--- {strategy.upper()} PORTFOLIO & ORDERS ---")
    #     for i, (order, state) in enumerate(zip(strat_orders, portfolio_log[strategy])):
    #         print(f"Step {i+1}: {order}")
    #         print(f"Capital={state['capital']:.2f}, Earnings={state['earnings']:.2f}, Positions={state['positions']}")

    # # 5. compute performance as dictionary 
    # performance = compute_performance(portfolio_log)
    # print(performance)
