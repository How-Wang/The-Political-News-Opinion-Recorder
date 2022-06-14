from numpy import NaN
import pandas as pd
from datetime import datetime, timedelta

def timestamp_to_tw_datetime(timestamp):        
    try:
        time = datetime.fromtimestamp(timestamp) + timedelta(hours=8)
        return time.strftime('%Y-%m-%d %H:%M'), time.year, time.month, time.day, time.hour, time.minute
    except:
        return ('', '', '', '', '', '')

def timestemp_convert(df):
    df['datetime'], df['year'], df['month'], df['day'], df['hour'], df['minute'] = zip(*df['timestamp'].map(timestamp_to_tw_datetime))
    df = df.drop(columns=['timestamp'])
    return df