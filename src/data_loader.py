import pandas as pd
from models import MarketDataPoint

def load_data() -> list[MarketDataPoint]:
    data_path = "data/sample_data.csv"
    df = pd.read_csv(data_path)
    market_data_points = [
        MarketDataPoint(row['timestamp'], row['price'], row['volume'])
        for _, row in df.iterrows()
    ]
    return market_data_points
    
