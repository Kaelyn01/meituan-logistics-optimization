"""
Configuration module.
Provides access to all fixed parameters and datasets (cities / stations / vehicles).
"""

from .parameters import (
    # Data structures
    VEHICLE_TYPES,
    CITIES,
    STATIONS_PER_CITY,
    CITY_PARAMETERS,
    STATION_DEMANDS,

    # Constraints
    MAX_STATIONS_PER_TRIP,
    LEAD_TIME,
    STORAGE_CONVERSION,

    # Accessor functions
    get_daily_demand,
    get_city_total_demand,
    get_station_count,
    get_city_parameters,
    get_vehicle_type,
    get_all_stations,
)

__all__ = [
    # Data structures
    'VEHICLE_TYPES',
    'CITIES',
    'STATIONS_PER_CITY',
    'CITY_PARAMETERS',
    'STATION_DEMANDS',

    # Constraints
    'MAX_STATIONS_PER_TRIP',
    'LEAD_TIME',
    'STORAGE_CONVERSION',

    # Accessor functions
    'get_daily_demand',
    'get_city_total_demand',
    'get_station_count',
    'get_city_parameters',
    'get_vehicle_type',
    'get_all_stations',
]
