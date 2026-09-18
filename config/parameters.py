# Vehicle fleet parameters
VEHICLE_TYPES = {
    'large': {
        'fixed_cost': 600,      # CNY per trip
        'variable_cost': 6.5,   # CNY per km
        'capacity': 200000      # pcs
    },
    # Type-L vehicle
    'small': {
        'fixed_cost': 300,
        'variable_cost': 4.0,
        'capacity': 80000
    }
    # Type-S vehicle
}

# City geography and warehousing costs (CDC distance + warehouse rent + fixed inter-station distance)
CITY_PARAMETERS = {
    'A': {
        'cdc_distance': 40,       # Distance from the CDC to the first station in City A (km)
        'rent_per_m2': 5.0,        # Warehouse rent in City A (CNY/m^2/day)
        'inter_station_distance': 10  # Inter-station distance (km), fixed at 10 km as a simplifying assumption
    },
    'B': {
        'cdc_distance': 70,
        'rent_per_m2': 4.0,
        'inter_station_distance': 10
    },
    'C': {
        'cdc_distance': 100,
        'rent_per_m2': 3.0,
        'inter_station_distance': 10
    },
    'D': {
        'cdc_distance': 140,
        'rent_per_m2': 2.0,
        'inter_station_distance': 10
    },
    'E': {
        'cdc_distance': 180,
        'rent_per_m2': 1.5,
        'inter_station_distance': 10
    }
}

# Station-level data
# Number of stations per city
CITIES = ['A', 'B', 'C', 'D', 'E']
STATIONS_PER_CITY = {
    'A': 6,
    'B': 5,
    'C': 5,
    'D': 5,
    'E': 4
}

# Average daily sales per station (pcs/day)
STATION_DEMANDS = {
    'A': [85000, 80000, 75000, 60000, 55000, 50000],      # City A: 6 stations, dense high-volume cluster
    'B': [60000, 55000, 50000, 45000, 40000],           # City B: 5 stations, upper-mid volume
    'C': [50000, 45000, 40000, 35000, 30000],           # City C: 5 stations, mid volume
    'D': [35000, 30000, 25000, 20000, 15000],           # City D: 5 stations, lower-mid volume
    'E': [20000, 15000, 12000, 10000]                 # City E: 4 stations, low volume, long haul
}

# Space conversion factor
STORAGE_CONVERSION = 1000  # pcs per m^2

# Constraints
MAX_STATIONS_PER_TRIP = 3  # A vehicle serves at most 3 stations per trip
LEAD_TIME = 2  # Replenishment lead time (days)

# ==================== Accessor functions ====================

def get_daily_demand(city_code, station_index):
    """
    Return the average daily sales of a given station.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        station_index: Station index (0-based; 0 denotes the first station)

    Returns:
        Average daily sales (pcs/day)

    Example:
        >>> get_daily_demand('A', 0)  # First station of City A
        85000
    """
    return STATION_DEMANDS[city_code][station_index]


def get_city_total_demand(city_code):
    """
    Return the total average daily sales of a city.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')

    Returns:
        Sum of average daily sales over all stations in the city (pcs/day)

    Example:
        >>> get_city_total_demand('A')  # All stations of City A
        405000
    """
    return sum(STATION_DEMANDS[city_code])


def get_station_count(city_code):
    """
    Return the number of stations in a city.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')

    Returns:
        Number of stations
    """
    return STATIONS_PER_CITY[city_code]


def get_city_parameters(city_code):
    """
    Return all parameters of a city (distances, rent, etc.).

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')

    Returns:
        Dict containing all parameters of the city
    """
    return CITY_PARAMETERS[city_code]


def get_vehicle_type(vehicle_code):
    """
    Return the parameters of a vehicle type.

    Args:
        vehicle_code: Vehicle identifier ('large' or 'small')

    Returns:
        Dict containing all parameters of the vehicle type
    """
    return VEHICLE_TYPES[vehicle_code]


def get_all_stations(city_code):
    """
    Return the list of all stations in a city (with indices).

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')

    Returns:
        Station list, e.g. ['A_1', 'A_2', ..., 'A_6']

    Example:
        >>> get_all_stations('A')
        ['A_1', 'A_2', 'A_3', 'A_4', 'A_5', 'A_6']
    """
    count = STATIONS_PER_CITY[city_code]
    return [f"{city_code}_{i+1}" for i in range(count)]
