from data_loader import load_data
from strategies import macd, BollingerBandsStrategy
from engine import ExecutionEngine

def main():
    # 1. load data
    data_points = load_data() # tick data points

    # 2. inialize strategies
    strategies = {
        'macd': macd(),
        'bollingerband': BollingerBandsStrategy(),
    }

    # 3. intilialize engine
    engine = ExecutionEngine(data_points, strategies)
    
    # 4. run engine
    engine.run()

    print(engine.portfolio['macd'])
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(engine.portfolio['bollingerband'])


if __name__ == "__main__":
    main()