from data_loader import load_data
from strategies import MovingAverageCrossoverStrategy
from models import Order


def main():
    # 1. load data
    data_points = load_data() # tick data points
    # 2. generate signals
    MAStrategy = MovingAverageCrossoverStrategy()
    signals = []
    for tick in data_points:
        signals.append(MAStrategy.generate_signals(tick))
        for signal in signals:
            print(signal)
    # 3. make signals to code
    orders = []
    for signal in signals:
        for action, symbol, quantity, price in signal:
            order = Order(symbol, quantity, price, 'PENDING')
            orders.append(order)

    # 4. execute orders


if __name__ == "__main__":
    main()