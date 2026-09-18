"""
Cost model module.
Contains the cost functions for inventory holding and transportation.
"""

from config import (
    get_daily_demand,
    get_city_parameters,
    get_vehicle_type,
    get_all_stations,
    STORAGE_CONVERSION,
    LEAD_TIME,
    MAX_STATIONS_PER_TRIP,
)


# ==================== Inventory holding cost ====================

def calculate_peak_inventory(daily_demand: float, T: int) -> float:
    """
    Compute the peak inventory level of a station.

    Args:
        daily_demand: Average daily sales (pcs/day)
        T: Replenishment cycle (days)

    Returns:
        Peak inventory (pcs)

    Formula:
        peak inventory = daily demand x (cycle T + lead time 2)
    """
    return daily_demand * (T + LEAD_TIME)


def calculate_required_area(peak_inventory: float) -> float:
    """
    Compute the required warehouse area.

    Args:
        peak_inventory: Peak inventory level (pcs)

    Returns:
        Required area (m^2)

    Formula:
        required area = peak inventory / 1000 (pcs/m^2)
    """
    return peak_inventory / STORAGE_CONVERSION


def calculate_daily_storage_cost(city_code: str, station_index: int, T: int) -> float:
    """
    Compute the daily holding cost of a station.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        station_index: Station index (0-based)
        T: Replenishment cycle (days)

    Returns:
        Daily holding cost (CNY/day)

    Formula:
        daily cost = required area x rent per m^2
                   = (daily demand x (T + 2) / 1000) x rent_per_m2
    """
    # Fetch inputs
    daily_demand = get_daily_demand(city_code, station_index)
    city_params = get_city_parameters(city_code)
    rent_per_m2 = city_params['rent_per_m2']

    # Compute
    peak_inventory = calculate_peak_inventory(daily_demand, T)
    required_area = calculate_required_area(peak_inventory)
    daily_cost = required_area * rent_per_m2

    return daily_cost


def calculate_city_total_storage_cost(city_code: str, T: int) -> float:
    """
    Compute the total daily holding cost over all stations of a city.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        T: Replenishment cycle (days)

    Returns:
        Sum of daily holding costs over all stations (CNY/day)
    """
    stations = get_all_stations(city_code)
    total_cost = 0.0

    for i in range(len(stations)):
        station_cost = calculate_daily_storage_cost(city_code, i, T)
        total_cost += station_cost

    return total_cost


# ==================== Transportation cost ====================

def calculate_total_distance(city_code: str, k: int) -> float:
    """
    Compute the total distance of a single delivery trip.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        k: Number of stations served (1-3)

    Returns:
        Total distance (km)

    Formula:
        total distance = 2 x CDC distance + (k - 1) x inter-station distance

    Notes:
        - Leg 1: CDC -> first station
        - Leg 2: (k - 1) inter-station hops, 10 km each
        - Leg 3: last station -> CDC (same as leg 1)
    """
    if k < 1 or k > MAX_STATIONS_PER_TRIP:
        raise ValueError(f"Stations per trip must be between 1 and {MAX_STATIONS_PER_TRIP}, got {k}")

    city_params = get_city_parameters(city_code)
    cdc_distance = city_params['cdc_distance']
    inter_station_distance = city_params['inter_station_distance']

    # Total distance = 2 x CDC distance + (k-1) x inter-station distance
    total_distance = 2 * cdc_distance + (k - 1) * inter_station_distance

    return total_distance


def calculate_single_trip_cost(city_code: str, k: int, vehicle_type: str) -> float:
    """
    Compute the transportation cost of a single trip.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        k: Number of stations served (1-3)
        vehicle_type: Vehicle type ('large' or 'small')

    Returns:
        Transportation cost (CNY)

    Formula:
        trip cost = fixed dispatch cost + variable cost x total distance
                  = fixed_cost + variable_cost x total_distance
    """
    # Validate vehicle type
    if vehicle_type not in ['large', 'small']:
        raise ValueError("vehicle_type must be 'large' or 'small'")

    # Total distance
    total_distance = calculate_total_distance(city_code, k)

    # Vehicle parameters
    vehicle = get_vehicle_type(vehicle_type)
    fixed_cost = vehicle['fixed_cost']
    variable_cost_per_km = vehicle['variable_cost']

    # Total cost
    total_cost = fixed_cost + variable_cost_per_km * total_distance

    return total_cost


def check_capacity_constraint(station_demands: list, vehicle_type: str) -> bool:
    """
    Check the capacity constraint: whether the combined order quantity of the
    stations fits within the vehicle capacity.

    Args:
        station_demands: List of station order quantities (pcs)
        vehicle_type: Vehicle type ('large' or 'small')

    Returns:
        True if the constraint holds, False otherwise
    """
    vehicle = get_vehicle_type(vehicle_type)
    capacity = vehicle['capacity']
    total_demand = sum(station_demands)

    return total_demand <= capacity


def select_optimal_vehicle(city_code: str, station_indices: list, T: int = 1) -> str:
    """
    Select the optimal vehicle type for a group of stations.

    Strategy:
        1. Prefer the small vehicle (lower cost)
        2. Fall back to the large vehicle if overloaded
        3. Return None if even the large vehicle overloads (multiple vehicles needed)

    Args:
        city_code: City identifier
        station_indices: List of station indices
        T: Replenishment cycle (days); load per trip = daily demand x T

    Returns:
        Optimal vehicle type ('large' or 'small'), or None if both overload
    """
    # Total demand per trip = daily demand x T
    demands = [get_daily_demand(city_code, i) * T for i in station_indices]
    total_demand = sum(demands)

    # Try the small vehicle first
    small_vehicle = get_vehicle_type('small')
    if total_demand <= small_vehicle['capacity']:
        return 'small'

    # Try the large vehicle
    large_vehicle = get_vehicle_type('large')
    if total_demand <= large_vehicle['capacity']:
        return 'large'

    # Both overload
    return None


# ==================== Combined cost ====================

def calculate_daily_total_cost(city_code: str, T: int, grouping_plan: list) -> float:
    """
    Compute the total daily cost of a city under a given cycle and grouping plan.

    Args:
        city_code: City identifier ('A', 'B', 'C', 'D', 'E')
        T: Replenishment cycle (days)
        grouping_plan: Grouping plan, e.g. [[0,1,2], [3,4], [5]] denotes three
                       vehicles serving stations {0,1,2}, {3,4}, and {5} respectively

    Returns:
        Total daily cost (CNY/day) = holding cost + transportation cost
    """
    # 1. Daily holding cost
    storage_cost = calculate_city_total_storage_cost(city_code, T)

    # 2. Transportation cost of a single delivery round
    single_delivery_cost = 0.0
    for group in grouping_plan:
        # Select the optimal vehicle for each group (capacity checked at T-day load)
        vehicle_type = select_optimal_vehicle(city_code, group, T)
        if vehicle_type is None:
            station_names = [f"{city_code}_{i+1}" for i in group]
            raise ValueError(
                f"Order quantity of station group {station_names} (daily x {T}) exceeds the "
                f"largest vehicle capacity; the group must be split"
            )

        # Transportation cost of this group
        k = len(group)
        trip_cost = calculate_single_trip_cost(city_code, k, vehicle_type)
        single_delivery_cost += trip_cost

    # 3. Daily transportation cost = per-round cost / T
    daily_transport_cost = single_delivery_cost / T

    # 4. Total daily cost = holding + transportation
    total_cost = storage_cost + daily_transport_cost

    return total_cost


# ==================== Utilities ====================

def print_cost_breakdown(city_code: str, T: int, grouping_plan: list):
    """
    Print a detailed cost breakdown (for debugging and presentation).

    Args:
        city_code: City identifier
        T: Replenishment cycle
        grouping_plan: Grouping plan
    """
    print(f"\n{'='*60}")
    print(f"City {city_code} cost breakdown (T={T} days)")
    print(f"{'='*60}")

    # Holding cost details
    print(f"\n[Holding cost]")
    stations = get_all_stations(city_code)
    total_storage = 0
    for i, station in enumerate(stations):
        demand = get_daily_demand(city_code, i)
        peak = calculate_peak_inventory(demand, T)
        area = calculate_required_area(peak)
        rent = get_city_parameters(city_code)['rent_per_m2']
        cost = calculate_daily_storage_cost(city_code, i, T)
        total_storage += cost
        print(f"  {station}: demand={demand:,} pcs -> peak={peak:,} pcs -> area={area:.1f} m^2 -> rent={cost:.1f} CNY/day")
    print(f"  Holding cost subtotal: {total_storage:,.1f} CNY/day")

    # Transportation cost details
    print(f"\n[Transportation cost] (one delivery round every {T} days)")
    total_transport = 0
    for idx, group in enumerate(grouping_plan):
        vehicle_type = select_optimal_vehicle(city_code, group, T)
        if vehicle_type is None:
            station_names = [stations[i] for i in group]
            demands_info = [f"{get_daily_demand(city_code, i)*T:,}" for i in group]
            print(f"  Vehicle {idx+1}: serves {station_names} -> load {demands_info} pcs -> OVERLOAD, must split")
            continue

        k = len(group)
        distance = calculate_total_distance(city_code, k)
        trip_cost = calculate_single_trip_cost(city_code, k, vehicle_type)
        total_transport += trip_cost

        station_names = [stations[i] for i in group]
        group_demand = sum(get_daily_demand(city_code, i) * T for i in group)
        vehicle_cap = get_vehicle_type(vehicle_type)['capacity']
        print(f"  Vehicle {idx+1}: serves {station_names} -> load={group_demand:,}/{vehicle_cap:,} pcs -> distance={distance} km -> type={vehicle_type} -> trip cost={trip_cost:.1f} CNY")

    daily_transport = total_transport / T
    print(f"  Per-round transport total: {total_transport:,.1f} CNY")
    print(f"  Daily transport cost: {total_transport:,.1f} / {T} = {daily_transport:,.1f} CNY/day")

    # Total
    daily_transport = total_transport / T
    total_cost = total_storage + daily_transport
    print(f"\n[Total daily cost]")
    print(f"  Total = holding {total_storage:,.1f} + transport {daily_transport:,.1f} = {total_cost:,.1f} CNY/day")
    print(f"{'='*60}\n")
