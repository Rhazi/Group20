import yfinance as yf
import pandas as pd
from constants import *

class PriceLoader:
    def __init__(self):
        pass

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

        if not dfs:
            raise RuntimeError(f"No data downloaded for {ticker} between {start_date} and {end_date}")
        
        df = pd.concat(dfs)
        if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

        if 'Adj Close' in df.columns:
            df = df[['Adj Close', 'Volume']].rename(columns={'Adj Close': 'adj_close', 'Volume': 'volume'})
        else:
            # fall back to Close (less ideal but robust)
            df = df[['Close', 'Volume']].rename(columns={'Close': 'adj_close', 'Volume': 'volume'})

        df = df[~df.index.duplicated(keep='first')]
        df.drop('Ticker', axis=1, inplace=True, errors='ignore')
        df['symbol'] = ticker

        df = df.rename_axis('timestamp')
        df.index = pd.to_datetime(df.index)
        df.reset_index(inplace=True)
        df = df.sort_index()

        return df

    def get_price(self, item_id):
        return self.price_data.get(item_id, None)

if __name__ == "__main__":
    loader = PriceLoader()

    start_date = "2005-01-01"
    end_date = "2025-01-01"

    price_spy_df = loader.download_price(SPY, start_date=start_date, end_date=end_date)
    # price_voo_df = loader.download_price(VOO, start_date=start_date, end_date=end_date)
    # price_ivv_df = loader.download_price(IVV, start_date=start_date, end_date=end_date)

    price_spy_df.to_csv("data/price_spy.parquet", index=False)
    # price_voo_df.to_csv("data/price_voo.parquet", index=False)
    # price_ivv_df.to_csv("data/price_ivv.parquet", index=False)
    