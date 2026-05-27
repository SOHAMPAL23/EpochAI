import sys
import os

try:
    import yfinance as yf
    print("yfinance is installed!")
    
    # Try fetching a small sample
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="5d")
    print("Successfully fetched AAPL history:")
    print(df.head())
    print("Row count:", len(df))
except Exception as e:
    print("Error:", e)
