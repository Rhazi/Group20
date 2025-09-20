import pytest
import datetime
from models import MarketDataPoint, Order, OrderAction, OrderStatus, OrderError, ExecutionError
from engine import ExecutionEngine
from pathlib import Path
import csv

FIXTURES = Path(__file__).parent / "fixtures"

def test_csv_parses_into_frozen_dataclass():
    test_points = []
    csv_path = FIXTURES / "sample_data.csv"
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.datetime.fromisoformat(row['timestamp'])
            mdp = MarketDataPoint(timestamp=ts, symbol=row['symbol'], price=float(row['price']))
            test_points.append(mdp)

    assert len(test_points) == 2
    assert test_points[0].symbol == 'AAPL'
    assert isinstance(test_points[0].timestamp, datetime.datetime)

    # immutable attributes for MarketDataPoint
    with pytest.raises(Exception):
        test_points[0].price = 123.0
    with pytest.raises(Exception):
        test_points[0].symbol = 'GOOG'
    with pytest.raises(Exception):
        test_points[0].timestamp = datetime.datetime.now()


def test_order_mutable_behavior_and_validation():
    # valid order
    o = Order(symbol='AAPL', quantity=10, price=100.0, status=OrderStatus.UNFILLED.value, action=OrderAction.BUY.value)
    assert o.symbol == 'AAPL'
    assert o.quantity == 10

    # mutate attributes (Order is intentionally mutable)
    o.symbol = 'GOOG'
    assert o.symbol == 'GOOG'
    o.quantity = 5
    assert o.quantity == 5
    o.price = 150.0
    assert o.price == 150.0
    o.status = OrderStatus.FILLED.value
    assert o.status == OrderStatus.FILLED.value

    # Order validation tests
    # invalid quantity
    with pytest.raises(OrderError):
        Order(symbol='AAPL', quantity=0, price=100.0, status=OrderStatus.UNFILLED.value, action=OrderAction.BUY.value)

    # invalid price
    with pytest.raises(OrderError):
        Order(symbol='AAPL', quantity=1, price=0.0, status=OrderStatus.UNFILLED.value, action=OrderAction.BUY.value)

    # invalid symbol
    with pytest.raises(OrderError):
        Order(symbol='', quantity=1, price=10.0, status=OrderStatus.UNFILLED.value, action=OrderAction.BUY.value)

    # invalid status
    with pytest.raises(OrderError):
        Order(symbol='AAPL', quantity=1, price=10.0, status='BADSTATUS', action=OrderAction.BUY.value)

def test_order_execution_error():
    # Create sample market data
    market_data = [
        MarketDataPoint(timestamp=datetime.datetime.now(), symbol='AAPL', price=150.0),
        MarketDataPoint(timestamp=datetime.datetime.now(), symbol='AAPL', price=155.0),
    ]

    # Initialize execution engine with market data
    mock_engine = ExecutionEngine(market_data)
    
    # Attempt to buy with insufficient capital
    expensive_order = Order(symbol='AAPL', quantity=1000, price=200.0, status=OrderStatus.UNFILLED.value, action=OrderAction.BUY.value)
    with pytest.raises(ExecutionError):
        mock_engine.execute_order(expensive_order)

    # Attempt to without owning shares
    sell_order = Order(symbol='AAPL', quantity=200, price=155.0, status=OrderStatus.UNFILLED.value, action=OrderAction.SELL.value)
    with pytest.raises(ExecutionError):
        mock_engine.execute_order(sell_order)

    # Set up a position for mock engine
    mock_engine.portfolio['positions']['AAPL'] = {'quantity': 50, 'avg_price': 150.0}

    # Attempt to sell more than owned
    sell_order = Order(symbol='AAPL', quantity=200, price=155.0, status=OrderStatus.UNFILLED.value, action=OrderAction.SELL.value)
    with pytest.raises(ExecutionError):
        mock_engine.execute_order(sell_order)
    

    

    