from enum import Enum
import math
from datetime import datetime
import datetime

class Constants:
    class CDSConstants(Enum):
        TIME_FIELD = 'valid_time'
        LAT_FIELD = 'latitude'
        LON_FIELD = 'longitude'
        PRESSURE_FIELD = 'pressure_level'
    
    class Graphcast(Enum):
        TIME_FIELD = 'time'
        LAT_FIELD = 'latitude'
        LON_FIELD = 'longitude'
        PRESSURE_FIELD = 'level'
        BATCH_FIELD = 'batch'

# Weather field mappings
SINGLE_LEVEL_FIELDS = {
    'u10': '10m_u_component_of_wind',
    'v10': '10m_v_component_of_wind',
    't2m': '2m_temperature',
    'z': 'geopotential',
    'lsm': 'land_sea_mask',
    'msl': 'mean_sea_level_pressure',
    'tisr': 'toa_incident_solar_radiation',
    'tp': 'total_precipitation'
}

PRESSURE_LEVEL_FIELDS = {
    'u': 'u_component_of_wind',
    'v': 'v_component_of_wind',
    'z': 'geopotential',
    'q': 'specific_humidity',
    't': 'temperature',
    'w': 'vertical_velocity'
}

PREDICTION_FIELDS = [
    'u_component_of_wind',
    'v_component_of_wind',
    'geopotential',
    'specific_humidity',
    'temperature',
    'vertical_velocity',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '2m_temperature',
    'mean_sea_level_pressure',
    'total_precipitation_6hr'
]

PRESSURE_LEVELS = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]

# Constants for calculations
PI = math.pi
GAP = 1
PREDICTIONS_STEPS = 240
WATTS_TO_JOULES = 3600

# Coordinate assignments for different fields
COORDINATE_ASSIGNMENTS = {
    '2m_temperature': ['batch', 'lon', 'lat', 'time'],
    'mean_sea_level_pressure': ['batch', 'lon', 'lat', 'time'],
    '10m_v_component_of_wind': ['batch', 'lon', 'lat', 'time'],
    '10m_u_component_of_wind': ['batch', 'lon', 'lat', 'time'],
    'total_precipitation_6hr': ['batch', 'lon', 'lat', 'time'],
    'temperature': ['batch', 'lon', 'lat', 'level', 'time'],
    'geopotential': ['batch', 'lon', 'lat', 'level', 'time'],
    'u_component_of_wind': ['batch', 'lon', 'lat', 'level', 'time'],
    'v_component_of_wind': ['batch', 'lon', 'lat', 'level', 'time'],
    'vertical_velocity': ['batch', 'lon', 'lat', 'level', 'time'],
    'specific_humidity': ['batch', 'lon', 'lat', 'level', 'time'],
    'toa_incident_solar_radiation': ['batch', 'lon', 'lat', 'time'],
    'year_progress_cos': ['batch', 'time'],
    'year_progress_sin': ['batch', 'time'],
    'day_progress_cos': ['batch', 'lon', 'time'],
    'day_progress_sin': ['batch', 'lon', 'time'],
    'geopotential_at_surface': ['lon', 'lat'],
    'land_sea_mask': ['lon', 'lat'],
} 