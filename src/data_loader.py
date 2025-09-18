import pandas as pd
import os
from models import MarketDataPoint

# Adjust data directory to be one level above 'src'
def load_data() -> list[MarketDataPoint]:
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    data_path = os.path.join(data_dir, "market_data.csv")

    df = pd.read_csv(data_path)
    market_data_points = [
        MarketDataPoint(row['timestamp'], row['symbol'], row['price'])
        for _, row in df.iterrows()
    ]
    return market_data_points
    
