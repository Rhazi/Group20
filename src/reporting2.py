import pandas as pd
from strategies import MAStrategy, LongOnlyOnce, Volatility, macd, RSI
from engine import ExecutionEngine
from PriceLoader2 import PriceLoader




def limited_period_total500(start_date, end_date,data_points): 
    print("data_points 예시가 시작하는 곳##########################################################################")
    print(data_points[0])  
    print("data_points 예시가 종료되는 곳##########################################################################")
    
    # 2. 전략 가져오기 
    #strategies = {'MA': MAStrategy(), 'LO' : LongOnlyOnce(), 'VOL':Volatility(), 'MACD' : macd(), 'RSI':RSI()}
    strategies = {'LO' : LongOnlyOnce()}
    
    # 3. intilialize engine
    engine = ExecutionEngine(data_points, strategies)
    # 4. run engine
    engine.run()
    orders = engine.orders

    return orders



def build_portfolio_timeseries(orders, data_points, strategy_name, start_date, initial_capital=1_000_000):
    # orders_by_strategy 필터링
    orders = [o for o in orders if o.strategy == strategy_name]

    # 시간순 정렬
    all_dates = sorted(pd.to_datetime(list(data_points.keys())))
    
    # 첫 행 강제로 start_date
    records = []

    # 첫 행: 종목별 0, cash = 초기자본
    first_record = {"date": pd.to_datetime(start_date), "total_value": initial_capital, "cash": initial_capital}
    # 나머지 티커 컬럼은 0
    tickers = set(o.symbol for o in orders)
    for t in tickers:
        first_record[t] = 0.0
    records.append(first_record)

    # 나머지 날짜 처리
    portfolio = {"cash": initial_capital}
    for t in tickers:
        portfolio[t] = 0.0

    for dt in all_dates:
        dt_records = {"date": dt}
        # 그날 주문 처리
        for o in orders:
            if o.timestamp == dt:
                if o.action == "BUY":
                    portfolio[o.symbol] += o.quantity
                    portfolio["cash"] -= o.quantity * o.price
                elif o.action == "SELL":
                    portfolio[o.symbol] -= o.quantity
                    portfolio["cash"] += o.quantity * o.price
        # 그날 시가로 가치 계산
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
    # print("data_points 예시가 시작하는 곳##########################################################################")
    # for k in list(data_points.keys())[:10]:  # 상위 10개만
    #     print(k)
    # print("data_points 예시가 종료되는 곳##########################################################################")

    orders = limited_period_total500(start_date, end_date, data_points)
    # 여기까지 돌렷을때 오류나는건 매칭이 불가능할때 발생하는 오류를 의미함! raise된 에러니까 상관할 필요없음!(다만 포지션이 부족해서 팔 수 없음)
    print("order 예시가 시작하는 곳##########################################################################")
    print(orders[:5])  
    print("order 예시가 종료되는 곳##########################################################################")
        
    # 2. seperate by strategy and generate trade log
    df_ts = build_portfolio_timeseries(orders, data_points, "LO", start_date, initial_capital=1000000)
    df_ts = df_ts.iloc[1:]
    print(df_ts.head())

    # print("여기서 부터 로그입니다")
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
