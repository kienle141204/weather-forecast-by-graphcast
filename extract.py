import os
import zipfile
import xarray
import pandas as pd
import netCDF4
from typing import Tuple
from constants import SINGLE_LEVEL_FIELDS, PRESSURE_LEVEL_FIELDS, PRESSURE_LEVELS
from utils import remove_junk_columns
from datetime import datetime
import datetime

def get_single_level_values(filename: str) -> pd.DataFrame:
    """Read and process single-level files from NetCDF zip file"""
    extract_to = filename.split('.')[0]
    with zipfile.ZipFile(filename, 'r') as f:
        f.extractall(extract_to)

    dfs = []
    for i in os.listdir(extract_to):
        extension = i.split('.')[-1]
        if extension == 'nc':
            df = xarray.open_dataset('{}/{}'.format(extract_to, i), engine=netCDF4.__name__.lower()).to_dataframe()
            df = remove_junk_columns(df)
            dfs.append(df)

    single_level_df = pd.concat(dfs, axis=1)
    return single_level_df

def get_single_and_pressure_values(client, time: datetime.datetime) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Download and process ERA5 data including surface and pressure level data"""
    # Download single level data
    client.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': list(SINGLE_LEVEL_FIELDS.values()),
            # 'grid': '1.0/1.0',
            'year': [time.year],
            'month': [time.month],
            'day': [time.day],
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00'],
            "area": [22, 105, 20, 107],
            'data_format': 'netcdf',
            'download_format': 'zip'
        }
    ).download('single-level.zip')

    singlelevel = get_single_level_values('single-level.zip')
    singlelevel = singlelevel.rename(columns={col: SINGLE_LEVEL_FIELDS[col] for col in singlelevel.columns.values.tolist() if col in SINGLE_LEVEL_FIELDS})
    singlelevel = singlelevel.rename(columns={'geopotential': 'geopotential_at_surface'})

    # Calculate 6-hour total precipitation
    singlelevel = singlelevel.sort_index()
    singlelevel['total_precipitation_6hr'] = singlelevel.groupby(level=[0, 1])['total_precipitation'].rolling(window=6, min_periods=1).sum().reset_index(level=[0, 1], drop=True)
    singlelevel.pop('total_precipitation')

    # Download pressure level data
    client.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type': 'reanalysis',
            'variable': list(PRESSURE_LEVEL_FIELDS.values()),
            # 'grid': '1.0/1.0',
            'year': [time.year],
            'month': [time.month],
            'day': [time.day],
            'time': ['06:00', '12:00'],
            "area": [22, 105, 20, 107],
            'pressure_level': PRESSURE_LEVELS,
            'data_format': 'netcdf',
            'download_format': 'unarchived'
        }
    ).download('pressure-level.nc')

    pressurelevel = xarray.open_dataset('pressure-level.nc', engine=netCDF4.__name__.lower()).to_dataframe()
    pressurelevel = remove_junk_columns(pressurelevel)
    pressurelevel = pressurelevel.rename(columns={col: PRESSURE_LEVEL_FIELDS[col] for col in pressurelevel.columns.values.tolist() if col in PRESSURE_LEVEL_FIELDS})

    return singlelevel, pressurelevel 