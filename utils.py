from datetime import datetime
import datetime
import isodate
import pytz
import numpy as np
import pandas as pd
from typing import Union
from constants import Constants

def to_datetime(dt: Union[str, datetime.date, datetime.datetime]) -> datetime.datetime:
    """Convert date/time object or ISO string to datetime.datetime"""
    if isinstance(dt, datetime.date) and isinstance(dt, datetime.datetime):
        return dt
    elif isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        return datetime.datetime.combine(dt, datetime.datetime.min.time())
    elif isinstance(dt, str):
        if 'T' in dt:
            return isodate.parse_datetime(dt)
        else:
            return datetime.datetime.combine(isodate.parse_date(dt), datetime.datetime.min.time())

def nans(*args) -> list:
    """Create numpy array of given size filled with NaN values"""
    return np.full((args), np.nan)

def delta_time(dt: datetime.datetime, **delta) -> datetime.datetime:
    """Add time delta to datetime"""
    return dt + datetime.timedelta(**delta)

def add_timezone(dt: datetime.datetime, tz=pytz.UTC) -> datetime.datetime:
    """Add or convert timezone for datetime object"""
    dt = to_datetime(dt)
    if dt.tzinfo is None:
        return pytz.UTC.localize(dt).astimezone(tz)
    else:
        return dt.astimezone(tz)

def remove_junk_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove unnecessary columns from DataFrame"""
    for col in ['number', 'expver']:
        if col in df.columns.values.tolist():
            df.pop(col)
    return df 