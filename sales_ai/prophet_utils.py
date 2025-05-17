# sales_ai/prophet_utils.py

from prophet import Prophet
import pandas as pd
from io import StringIO

def train_and_forecast(df, periods=30):
    model = Prophet()
    model.fit(df)
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]