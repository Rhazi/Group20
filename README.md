# Group20 Backtester

A small, educational backtesting framework developed for FINM325 — designed to run trading strategies over historical price data and produce performance reports.

## Overview

This repository implements a simple backtester with the following responsibilities:

- `src/data_loader.py` — loads historical market data (CSV or similar) and yields time-series market events.
- `src/class.py` — core domain models: Market data points, Orders, Portfolio, and custom Exceptions.
- `src/strategies.py` — user-configurable strategies. Each strategy should expose a simple interface that the engine can call (e.g., `on_tick` or `generate_signals`).
- `src/engine.py` — the backtest engine: executes strategy signals against market data, simulates order execution, and updates the portfolio.
- `src/reporting.py` — produces summary statistics and visualizations (returns performance metrics and generates plots).
- `src/main.py` — entrypoint script that wires the components together and runs the backtest.

> Note: At the time of writing, most `src/*.py` files are empty except `src/class.py`. The README below assumes common backtester behavior — adjust examples if your project differs.

## Requirements

- Python 3.10+ recommended
- Create and activate a virtual environment before installing dependencies.

Example (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install commonly used packages:

```bash
pip install pandas numpy matplotlib
```

## Project structure

- `src/` — source code
- `data/` — (suggested) place CSV historical price files here
- `notebooks/` — (suggested) Jupyter notebooks for analysis
- `README.md` — this file

## Data format

The backtester expects historical data in a timeseries CSV with at least the following columns:

- `timestamp` — ISO-8601 datetime string (e.g. `2020-01-01T09:30:00`)
- `symbol` — ticker symbol (e.g. `AAPL`)
- `price` — float price (close or mid-price depending on your source)

Example CSV:

```csv
timestamp,symbol,price
2020-01-02T09:30:00,AAPL,300.35
2020-01-02T09:31:00,AAPL,301.00
```

If you have OHLCV data, modify `src/data_loader.py` to parse and yield the fields your strategies need.

## How to run a backtest

1. Prepare data in `data/your_symbol.csv`.
2. Implement or pick a strategy in `src/strategies.py`.
3. Use `src/main.py` to run the backtest. A typical `main.py` does:
   - load data
   - create strategy instance
   - create engine with starting capital
   - run engine over data
   - produce a report

A minimal example (conceptual):

```python
from src.data_loader import load_csv
from src.strategies import MyStrategy
from src.engine import BacktestEngine
from src.reporting import Reporter

data = load_csv('data/AAPL.csv')
strategy = MyStrategy()
engine = BacktestEngine(starting_cash=100000)
engine.run(data, strategy)

report = Reporter(engine.portfolio)
report.summary()
```

Adjust names to match your actual API.

## Writing strategies

Strategies should be simple, stateless or with explicit state, and expose a small interface the engine can call. Example pattern:

```python
class MyStrategy:
    def __init__(self, params):
        # store params/state

    def on_tick(self, market_data_point):
        # return action(s) like {'symbol': 'AAPL', 'side': 'buy', 'qty': 10}
        return None
```

The engine calls `on_tick` for each market datapoint and converts returned signals into orders.

## Extending the engine

- Add slippage, commissions, partial fills models to `src/engine.py`.
- Support portfolio-level risk checks (max position size, margin calls).
- Add event-based scheduling (entry/exit by time-of-day, trailing stops).

## Reporting and analysis

`src/reporting.py` should compute common metrics: total return, annualized return, max drawdown, Sharpe ratio, and generate a price/equity curve plot. Use `pandas` and `matplotlib` or `plotly` for visuals.

## Tests

Add unit tests covering:
- Strategy signal generation (given synthetic market series)
- Order execution logic in the engine
- Portfolio P&L accounting and edge cases (zero cash, negative position)

## Contributing

- Follow PEP8
- Add tests for new features
- Open an issue or PR describing the change

## Contact

For questions about this repository, ask your course group contributors or instructor. Include the file(s) you modified and a brief description of the expected vs actual behavior.

---

If you'd like, I can create a concrete `requirements.txt`, a starter `data/` CSV, and a simple example strategy and `main.py` runner that work end-to-end — tell me which you'd prefer and I will add them.