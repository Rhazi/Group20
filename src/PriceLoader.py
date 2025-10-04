from collections import defaultdict
import yfinance as yf
import pandas as pd
import os
from models import MarketDataPoint
from constants import *

class PriceLoader:
    def __init__(self):
        print('Initializing PriceLoader...')
        self.tickers = self.scrape_tickers()

    def scrape_tickers(self):
        url = "https://datahub.io/core/s-and-p-500-companies/r/0.csv"
        tickers = pd.read_csv(url)["Symbol"].tolist()
        return tickers

    def download_price(self, ticker:str, start_date, end_date, batch_size = 150):
        print("\n" + "="*80)
        print(f"""STARTING DOWNLOAD for {ticker} from {start_date} to {end_date}""")
        print("="*80 + "\n")   
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        all_dates = pd.date_range(start, end, freq='B')

        # Split the date range into batches
        batches = [all_dates[i:i + batch_size] for i in range(0, len(all_dates), batch_size)]
        dfs = []
        for batch in batches:
            batch_start = batch[0].strftime('%Y-%m-%d')
            batch_end = batch[-1].strftime('%Y-%m-%d')
            print("Downloading data for", ticker, "from", batch_start, "to", batch_end, "...")

            df_batch = yf.download(ticker, start=batch_start, end=(pd.to_datetime(batch_end) + pd.Timedelta(days=1)).strftime('%Y-%m-%d'), progress=False, auto_adjust=False)
            if not df_batch.empty:
                dfs.append(df_batch)
        print("Download complete for", ticker, "...!")

        df = pd.DataFrame()
        if dfs:        
            df = pd.concat(dfs)
            if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]

            if 'Adj Close' in df.columns:
                df = df[['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']].rename(columns={'Adj Close': 'adj_close', 'Close': 'close', 
                                                                                                'High': 'high', 'Low': 'low', 'Open': 'open',
                                                                                                'Volume': 'volume'})
            else:
                # fall back to Close (less ideal but robust)
                df = df[['Close', 'High', 'Low', 'Open', 'Volume']].rename(columns={'Close': 'close', 
                                                                                    'High': 'high', 'Low': 'low', 'Open': 'open',
                                                                                    'Volume': 'volume'})

            df = df[~df.index.duplicated(keep='first')]
            df.drop('Ticker', axis=1, inplace=True, errors='ignore')
            df['symbol'] = ticker

            df = df.rename_axis('timestamp')
            df.index = pd.to_datetime(df.index)
            df.reset_index(inplace=True)
            df = df.sort_index()
        else:
            print(f"No data found for {ticker} in the given date range.")

        return df

    def load_data(self, start_date = "2005-01-01",  end_date="2025-01-01") -> list[MarketDataPoint]:
        market_data_dict = defaultdict(list)
        for ticker in self.tickers:
            fn = f"price_{ticker.lower()}.parquet"
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
            data_path = os.path.join(data_dir, fn)
            if not os.path.exists(data_path):
                self.download_price(ticker, start_date=start_date, end_date=end_date).to_parquet(data_path, index=False)
            
            df = pd.read_parquet(data_path)
            # update market data dict based on timestamp
            for _, row in df.iterrows():
                market_data_dict[row['timestamp']].append(MarketDataPoint(row['timestamp'], row['symbol'], row['adj_close'], 
                                                            row['close'], row['high'], row['low'], row['open'],
                                                            row['volume']))
        
        # market_data_dict = dict(sorted(market_data_dict.items())[:50])
        return market_data_dict
        
if __name__ == "__main__":
    loader = PriceLoader()

    start_date = "2005-01-01"
    end_date = "2025-01-01"

    for ticker in loader.tickers:
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        parquet_name = f"price_{ticker.lower()}.parquet"
        fp = os.path.join(dir, parquet_name)
        if not os.path.exists(fp):
            price_spy_df = loader.download_price(ticker, start_date=start_date, end_date=end_date)
            if not price_spy_df.empty:
                price_spy_df.to_parquet(fp, index=False)

    