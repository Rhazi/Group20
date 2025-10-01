from data_loader import load_data
from strategies import macd, BollingerBandsStrategy, MAStrategy
from engine import ExecutionEngine
from PriceLoader import PriceLoader


def main():
    # 1. load data
    # data_points = load_data() # tick data points
    
    price_loader = PriceLoader()
    data_points = price_loader.load_data() # tick data points

    # 2. inialize strategies
    strategies = {
        # 'macd': macd(),
        # 'bollingerband': BollingerBandsStrategy(),
        'MA': MAStrategy()
    }

    # 3. intilialize engine
    engine = ExecutionEngine(data_points, strategies)
    
    # 4. run engine
    engine.run()

    # 5. print portfolio summary
    print("\n" + "="*40)
    print("FINAL PORTFOLIO SUMMARY")
    print("="*40 + "\n")    
    for strategy_name, portfolio in engine.portfolio.items():
        print(f"Strategy: {strategy_name}")
        print(f"  Capital: {portfolio['capital']:.2f}")
        print(f"  Positions: {portfolio['positions']}")
        print(f"  Earnings: {portfolio['earnings']:.2f}\n")

if __name__ == "__main__":
    main()