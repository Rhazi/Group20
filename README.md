# Group20 Backtester

A small, educational backtesting framework developed for FINM325 — designed to run trading strategies over historical price data and produce performance reports.

## Overview

This repository implements a simple backtester. Current repo files of interest:

- `src/PriceLoader.py` — download all tickers for S&P 500 and save them into parquet.
- `src/models.py` — domain models: `MarketDataPoint`, `Order`, `OrderStatus`, `OrderAction` and custom Exceptions.
- `src/strategies.py` — strategy implementations (e.g., macd). Strategies expose `generate_signals` or a similar method.
- `src/BenchmarkStrategy.py` — contains benchmark or baseline strategies for comparison, such as `LongOnlyOnce` (simple buy-and-hold). Useful for evaluating your custom strategies against a passive approach.
- `src/engine.py` — execution engine that applies strategy signals to the portfolio and simulates fills.
- `notebooks/StrategyComparison.ipynb` — Jupyter notebook for comparing multiple strategies on the same dataset. It loads price data, runs each strategy, and visualizes performance metrics (returns, drawdowns, Sharpe ratio) side-by-side. Useful for analyzing which strategy performs best under different market conditions.
- `src/StrategyComparison.py` — reporting utilities to compute returns and compare performances for each strategy.
- `src/main.py` — entrypoint script that wires all components together and runs experiments.

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
- `adj_close` — float price (close or mid-price depending on your source)
- `open` — float, opening price for the period
- `close` — float, closing price for the period
- `high` — float, highest price for the period
- `low` — float, lowest price for the period
- `vol` — integer or float, trading volume for the period
**Updated CSV format example:**

The recommended CSV format for full OHLCV data is:

```csv
timestamp,symbol,open,high,low,close,adj_close,vol
2020-01-02T09:30:00,AAPL,299.80,300.50,299.60,300.35,300.35,120000
2020-01-02T09:31:00,AAPL,300.35,301.20,300.10,301.00,301.00,95000
```

- `timestamp`: ISO-8601 datetime string
- `symbol`: ticker symbol
- `open`, `high`, `low`, `close`, `adj_close`: float prices
- `vol`: integer or float volume

If you only have price data, use:

```csv
timestamp,symbol,price
2020-01-02T09:30:00,AAPL,300.35
2020-01-02T09:31:00,AAPL,301.00
```

## How to run a backtest

1. Prepare data in `data/price_symbol.parquet`.
2. Implement or pick a strategy in `src/strategies.py`.
3. Use `src/main.py` to run the backtest. A typical `main.py` does:
   - load data
   - create strategy instance
   - create engine with starting capital
   - run engine over data
   - produce a report

A minimal example (conceptual):

```python
from src.PriceLoader import PriceLoader

from src.strategies import MovingAverageCrossoverStrategy
from src.engine import ExecutionEngine
from src.reporting import Reporter

price_loader = PriceLoader()
data_points = price_loader.load_data() # tick data points

strategies = {
   'MA': MovingAverageCrossoverStrategy()
}
engine = ExecutionEngine(data,  strategies)
engine.run()

# run jupyter for repporting after this
```

### Running the repository example (`src/main.py`)

The repository contains a runnable example entrypoint at `src/main.py`. It uses a `PriceLoader` utility to find and load price files, wires a set of strategies, runs the `ExecutionEngine`, and prints final portfolio summaries per strategy.

From the repository root you can run:

```bash
python src/main.py
```

Notes:
- `src/main.py` imports local modules without `src.` package qualification. Launching `jupyter` or `python` from the repo root ensures the imports resolve. If you get ModuleNotFoundError when running cells, set PYTHONPATH to the repo root or add an import shim in the notebook (see Notebooks section).
- The example expects a `PriceLoader` implementation (file `PriceLoader.py`) and strategy implementations in `src/strategies.py` or a top-level `strategies.py` depending on your branch. Check `src/main.py` imports — typical names used in this repo are: `macd`, `BollingerBandsStrategy`, `MAStrategy`, `Volatility`, `MACD`, `RSI`.

## Key project components (focused)

Below are short descriptions and usage notes for the files you asked me to highlight.

- `PriceLoader.py` (or `src/PriceLoader.py`)
    - Responsibility: discover and load CSV/parquet price files from `data/` and return a time-series that the engine consumes.
    - Typical API: `PriceLoader().load_data()` returns a list of market datapoints or a pandas DataFrame depending on implementation.
    - Example usage (used by `src/main.py`):
        ```python
        from PriceLoader import PriceLoader
        price_loader = PriceLoader()
        data_points = price_loader.load_data()
        ```

- `src/strategies.py` (or top-level `strategies.py` depending on branch)
    - Contains strategy implementations and helper signal generators.
    - Common pattern: each strategy exposes a `generate_signals(tick)` method that returns a list of signals of the form `(action, symbol, qty, price)` where `action` is one of `OrderAction.BUY`/`SELL` (or their `.value` strings in some implementations).
    - Example strategies present in this project (watch for exact function/class names in your branch): `macd`, `BollingerBandsStrategy`, `MAStrategy`, `Volatility`, `MACD`, `RSI`.
    - To add a new strategy: implement the class and return signals compatible with the engine's executor.

- `BenchmarkStrategy.py` (or `src/BenchmarkStrategy.py`)
    - Contains benchmark or baseline strategies used for comparison. A common helper is `LongOnlyOnce` which implements a simple buy-and-hold or single-entry long strategy.
    - Example usage in `src/main.py`:
        ```python
        from BenchmarkStrategy import LongOnlyOnce
        strategies['benchmark'] = LongOnlyOnce()
        ```

- `StrategyComparison.ipynb` (notebook)
    - Location: look for `notebooks/StrategyComparison.ipynb` or `src/StrategyComparison.ipynb` depending on branch.
    - Purpose: run multiple strategies over the same dataset and produce comparative performance charts and tables.
    - Notebook imports often use plain module names (e.g., `from data_loader import load_data`). To run the notebook successfully:
        - Launch Jupyter from the repository root so Python can import local modules by filename.
        - Or add this one-time shim at the top of the notebook before other imports:
            ```python
            import sys, os
            sys.path.insert(0, os.path.abspath(''))
            ```
        - Ensure the kernel you select has the same environment where your dependencies (pandas, numpy, matplotlib, pytest) are installed.

## Notebooks and kernel notes

If you can't open or run the notebook:

- Make sure you start Jupyter from the repository root directory. That ensures the notebook's local imports find the correct files (e.g., `PriceLoader.py` and `strategies.py`).
- If you prefer not to rely on the working directory, modify the notebook to import from the `src` package (e.g., `from src.data_loader import load_data`) and install the package in editable mode (`pip install -e .`) or add the repo root to `PYTHONPATH`.
- If the notebook fails to display (JSON parse errors), open it in VS Code (raw view) to inspect JSON validity. I inspected `src/performance.ipynb` earlier and it appears to be valid JSON.


## Writing strategies

Strategies should be simple, stateless or with explicit state, and expose a small interface the engine can call. Example pattern:

```python
class MyStrategy:
    def __init__(self, params):
        # store params/state

    def generate_signals(self, tick):
        # return signals(s) like (action, symbol, qty, price)
        return ('BUY', 'AAPL', 100, 145.0)
```

The engine calls `generate_singals` for each market datapoint and converts returned signals into orders.

## Extending the engine

- Add slippage, commissions, partial fills models to `src/engine.py`.
- Support portfolio-level risk checks (max position size, margin calls).

## Reporting and analysis

`src/reporting.py` should compute common metrics: total return, annualized return, max drawdown, Sharpe ratio, and generate a price/equity curve plot. Use `pandas` and `matplotlib` or `plotly` for visuals.

## Workflow

The workflow now reflects the updated logic in `main.py`:

```mermaid
flowchart TD
    A[Load price data<br>PriceLoader.load_data()] --> B[Initialize strategies<br>e.g. MovingAverageCrossoverStrategy()]
    B --> C[Create ExecutionEngine<br>with data & strategies]
    C --> D[Run engine<br>engine.run()]
    D --> E[Generate report<br>Reporter or notebook]
```

**Step-by-step:**
1. Load historical price data using `PriceLoader`.
2. Instantiate one or more strategy classes (e.g., `MovingAverageCrossoverStrategy`).
3. Pass data and strategies to `ExecutionEngine`.
4. Run the engine to simulate trades and update portfolio.
5. Generate performance reports and visualizations.

## Tests
Check tests/test_models.py file for the implementation

![Test result preview](./img/FINM325%20-%20test%20result.png)

```bash
pip install pytest
```

Then run all tests at root directory:

```bash
pytest
```

Make sure your test files are named with the `test_*.py` pattern.

Add unit tests covering:
- CSV parsing into frozen dataclass
- Mutable behavior of Order
- Exception raising and handling

## Contributing

- Follow PEP8
- Add tests for new features
- Open an issue or PR describing the change

## Contact

For questions about this repository, ask your course group contributors or instructor. Include the file(s) you modified and a brief description of the expected vs actual behavior.
