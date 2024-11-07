import requests
import pandas as pd
from config import API_KEY

def fetch_stock_data(symbol, time_series_function, start_date, end_date, interval='5min'):

    base_url = "https://www.alphavantage.co/query"
    

    params = {
        "function": time_series_function,
        "symbol": symbol,
        "apikey": API_KEY,
    }

    if time_series_function == "TIME_SERIES_INTRADAY":
        params["interval"] = interval


    print("Fetching data with the following parameters:", params)
    response = requests.get(base_url, params=params)


    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)


    if response.status_code != 200:
        print("Error: Unable to fetch data from API.")
        return None


    data = response.json()
    print("Raw API Data:", data)

    if "Error Message" in data:
        print("Error from API:", data["Error Message"])
        return None

    time_series_key = None
    if time_series_function == "TIME_SERIES_INTRADAY":
        time_series_key = f"Time Series ({interval})"
    elif time_series_function == "TIME_SERIES_DAILY":
        time_series_key = "Time Series (Daily)"
    elif time_series_function == "TIME_SERIES_WEEKLY":
        time_series_key = "Weekly Time Series"
    elif time_series_function == "TIME_SERIES_MONTHLY":
        time_series_key = "Monthly Time Series"

    if time_series_key not in data:
        print("Error: Expected time series data not found in response.")
        return None

    df = pd.DataFrame.from_dict(data[time_series_key], orient='index', columns=['1. open', '2. high', '3. low', '4. close', '5. volume'])
    df.index = pd.to_datetime(df.index)

    df['1. open'] = df['1. open'].astype(float)
    df['2. high'] = df['2. high'].astype(float)
    df['3. low'] = df['3. low'].astype(float)
    df['4. close'] = df['4. close'].astype(float)
    df['5. volume'] = df['5. volume'].astype(int)

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    df = df[(df.index >= start_date) & (df.index <= end_date)]

    return df
