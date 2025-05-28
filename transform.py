import math
import numpy as np
import pandas as pd
import xarray
from typing import Dict
from pysolar.radiation import get_radiation_direct
from pysolar.solar import get_altitude
from constants import (
    Constants, COORDINATE_ASSIGNMENTS, PREDICTION_FIELDS,
    PI, GAP, PREDICTIONS_STEPS, WATTS_TO_JOULES
)
from utils import to_datetime, nans, delta_time, add_timezone
from datetime import datetime
import datetime

def add_year_progress(secs: float, data: pd.DataFrame) -> pd.DataFrame:
    """Add year progress information (sin/cos) to DataFrame"""
    progress = secs / (365.25 * 24 * 3600)  # Convert seconds to year progress
    data['year_progress_sin'] = math.sin(2 * PI * progress)
    data['year_progress_cos'] = math.cos(2 * PI * progress)
    return data

def add_day_progress(secs: float, lon: str, data: pd.DataFrame) -> pd.DataFrame:
    """Add day progress information (sin/cos) by longitude to DataFrame"""
    lons = data.index.get_level_values(lon).unique()
    progress = np.array([(secs + lon * 3600) % (24 * 3600) / (24 * 3600) for lon in lons])
    prxlon = {lon: prog for lon, prog in zip(list(lons), progress.tolist())}
    data['day_progress_sin'] = data.index.get_level_values(lon).map(lambda x: math.sin(2 * PI * prxlon[x]))
    data['day_progress_cos'] = data.index.get_level_values(lon).map(lambda x: math.cos(2 * PI * prxlon[x]))
    return data

def integrate_progress(data: pd.DataFrame) -> pd.DataFrame:
    """Integrate day and year progress information into the entire dataset"""
    for dt in data.index.get_level_values(Constants.CDSConstants.TIME_FIELD.value).unique():
        seconds_since_epoch = to_datetime(dt).timestamp()
        data = add_year_progress(seconds_since_epoch, data)
        data = add_day_progress(seconds_since_epoch, 'longitude' if 'longitude' in data.index.names else 'lon', data)
    return data

def get_solar_radiation(longitude: float, latitude: float, dt: datetime.datetime) -> float:
    """Calculate solar radiation hitting the surface based on location and time"""
    altitude_degrees = get_altitude(latitude, longitude, add_timezone(dt))
    solar_radiation = get_radiation_direct(dt, altitude_degrees) if altitude_degrees > 0 else 0
    return solar_radiation * WATTS_TO_JOULES

def integrate_solar_radiation(data: pd.DataFrame, lat_range: np.ndarray, lon_range: np.ndarray) -> pd.DataFrame:
    """Integrate solar radiation values into DataFrame"""
    dates = list(data.index.get_level_values(Constants.CDSConstants.TIME_FIELD.value).unique())
    coords = [[lat, lon] for lat in lat_range for lon in lon_range]
    values = []

    for dt in dates:
        values.extend(list(map(lambda coord: {
            Constants.CDSConstants.TIME_FIELD.value: dt,
            Constants.CDSConstants.LON_FIELD.value: coord[1],
            Constants.CDSConstants.LAT_FIELD.value: coord[0],
            'toa_incident_solar_radiation': get_solar_radiation(coord[1], coord[0], dt)
        }, coords)))

    values = pd.DataFrame(values).set_index(
        keys=[Constants.CDSConstants.LAT_FIELD.value, Constants.CDSConstants.LON_FIELD.value, Constants.CDSConstants.TIME_FIELD.value]
    )

    return pd.merge(data, values, left_index=True, right_index=True, how='inner')

def modify_coordinates(data: xarray.Dataset) -> xarray.Dataset:
    """Adjust unnecessary coordinates in xarray.Dataset"""
    for var in list(data.data_vars):
        varArray = data[var]
        nonIndices = list(set(list(varArray.coords)).difference(set(COORDINATE_ASSIGNMENTS[var])))
        data[var] = varArray.isel(**{coord: 0 for coord in nonIndices})
    data = data.drop_vars(Constants.Graphcast.BATCH_FIELD.value)
    return data

def make_xarray(data: pd.DataFrame) -> xarray.Dataset:
    """Convert DataFrame to xarray.Dataset with standardized axis names"""
    data = data.rename_axis(index={
        Constants.CDSConstants.TIME_FIELD.value: Constants.Graphcast.TIME_FIELD.value,
        Constants.CDSConstants.PRESSURE_FIELD.value: Constants.Graphcast.PRESSURE_FIELD.value
    })
    data = data.to_xarray()
    data = modify_coordinates(data)
    return data

def format_data(data: pd.DataFrame) -> pd.DataFrame:
    """Standardize input data format with proper index names and add batch index if missing"""
    data = data.rename_axis(index={Constants.CDSConstants.LAT_FIELD.value: 'lat', Constants.CDSConstants.LON_FIELD.value: 'lon'})
    if Constants.Graphcast.BATCH_FIELD.value not in data.index.names:
        data[Constants.Graphcast.BATCH_FIELD.value] = 0
        data = data.set_index(Constants.Graphcast.BATCH_FIELD.value, append=True)
    return data

def get_targets(dt: datetime.datetime, data: pd.DataFrame) -> pd.DataFrame:
    """Create empty DataFrame containing target prediction fields"""
    lat = sorted(data.index.get_level_values('lat').unique().tolist())
    lon = sorted(data.index.get_level_values('lon').unique().tolist())
    levels = sorted(data.index.get_level_values('pressure_level').unique().tolist())
    batch = data.index.get_level_values(Constants.Graphcast.BATCH_FIELD.value).unique().tolist()
    time = [delta_time(dt, hours=days * GAP) for days in range(PREDICTIONS_STEPS)]

    target = xarray.Dataset({
        field: (['lat', 'lon', 'level', Constants.CDSConstants.TIME_FIELD.value], nans(len(lat), len(lon), len(levels), len(time)))
        for field in PREDICTION_FIELDS
    }, coords={
        'lat': lat,
        'lon': lon,
        'level': levels,
        Constants.CDSConstants.TIME_FIELD.value: time,
        Constants.Graphcast.BATCH_FIELD.value: batch
    })

    return target.to_dataframe()

def get_forcings(data: pd.DataFrame) -> pd.DataFrame:
    """Create forcing DataFrame from original data by removing prediction fields and adding time and radiation info"""
    forcingdf = data.reset_index(level='level', drop=True).drop(labels=PREDICTION_FIELDS, axis=1)
    forcingdf = pd.DataFrame(index=forcingdf.index.drop_duplicates(keep='first'))
    forcingdf = integrate_progress(forcingdf)
    forcingdf = integrate_solar_radiation(forcingdf, np.arange(20, 22, 1), np.arange(105, 107, 1))
    return forcingdf 