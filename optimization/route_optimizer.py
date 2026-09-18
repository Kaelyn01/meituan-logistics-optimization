"""
Route optimization module.
Handles station grouping and vehicle dispatch optimization.
"""

from itertools import combinations
from config import (
    get_daily_demand,
    get_city_parameters,
    get_vehicle_type,
    get_station_count,
    MAX_STATIONS_PER_TRIP,
)


def generate_all_groupings(n_stations: int, max_group_size: int = 3):
    """
    Generate all feasible station groupings (set partitions).

    Uses backtracking to enumerate every partition of n_stations stations into
    groups of at most max_group_size stations each.

    Args:
        n_stations: Number of stations
        max_group_size: Maximum number of stations per group

    Returns:
        Generator of grouping plans; each plan is a list of lists, e.g. [[0,1], [2,3], [4]]

    Example:
        >>> list(generate_all_groupings(3))
        [[[0], [1], [2]], [[0, 1], [2]], [[0, 2], [1]], [[0], [1, 2]], [[0, 1, 2]]]
    """
    stations = list(range(n_stations))

    def backtrack(remaining, current_groups):
        if not remaining:
            yield current_groups[:]
            return

        # Anchor the first remaining station
        first = remaining[0]
        rest = remaining[1:]

        # Try appending `first` to an existing group (if the group is not full)
        for i, group in enumerate(current_groups):
            if len(group) < max_group_size:
                current_groups[i] = group + [first]
                yield from backtrack(rest, current_groups)
                current_groups[i] = group  # Backtrack

        # Try starting a new group with `first`
        current_groups.append([first])
        yield from backtrack(rest, current_groups)
        current_groups.pop()  # Backtrack

    yield from backtrack(stations, [])


def calculate_vehicle_plan(city_code: str, station_indices: list, T: int) -> dict:
    """
    Compute the optimal vehicle configuration for a group of stations
    (supports multi-vehicle dispatch).

    The result includes the visit order and load evolution of every vehicle.
    """
    # Total demand
    total_demand = sum(get_daily_demand(city_code, i) * T for i in station_indices)

    # Vehicle parameters
    small = get_vehicle_type('small')
    large = get_vehicle_type('large')

    city_params = get_city_parameters(city_code)
    k = len(station_indices)

    # Distance of this group's route
    distance = calculate_group_distance(city_params['cdc_distance'],
                                        city_params['inter_station_distance'], k)

    # Per-station order quantities for one delivery round (T days)
    station_demands = []
    for i in station_indices:
        daily = get_daily_demand(city_code, i)
        station_demands.append({
            'station_index': i,
            'station_name': f"{city_code}_{i + 1}",
            'daily_demand': daily,
            'order_quantity': daily * T  # Load per delivery round
        })

    # Sort by station index (fixes the visit order)
    station_demands.sort(key=lambda x: x['station_index'])

    # Enumerate vehicle combinations and keep the cheapest
    max_vehicles = (total_demand + small['capacity'] - 1) // small['capacity']
    max_vehicles = min(max_vehicles, 10)

    best_plan = None
    best_cost = float('inf')

    # Enumerate the number of small vehicles; cover the remainder with large ones
    for n_small in range(max_vehicles + 1):
        n_large = 0
        capacity = n_small * small['capacity']

        remaining = total_demand - capacity
        if remaining > 0:
            n_large = (remaining + large['capacity'] - 1) // large['capacity']
            capacity += n_large * large['capacity']

        if capacity < total_demand:
            continue

        # Cost of this configuration
        small_cost = small['fixed_cost'] + small['variable_cost'] * distance
        large_cost = large['fixed_cost'] + large['variable_cost'] * distance

        total_cost = n_small * small_cost + n_large * large_cost

        if total_cost < best_cost:
            best_cost = total_cost

            # Build the detailed vehicle assignment (with load evolution)
            vehicles_detail = []
            remaining_demands = [s['order_quantity'] for s in station_demands]

            # Assign small vehicles
            for v_idx in range(n_small):
                vehicle_load_detail = []
                current_load = 0

                # Load in visit order (fixing the amount dropped at each station)
                for s_idx, s in enumerate(station_demands):
                    if remaining_demands[s_idx] > 0:
                        # Load as much as fits
                        can_load = min(remaining_demands[s_idx], small['capacity'] - current_load)
                        if can_load > 0:
                            vehicle_load_detail.append({
                                'station_name': s['station_name'],
                                'station_index': s['station_index'],
                                'load_amount': can_load,
                                'load_after_stop': current_load + can_load  # Load after pickup
                            })
                            current_load += can_load
                            remaining_demands[s_idx] -= can_load

                        if current_load >= small['capacity']:
                            break

                # Utilization on arrival at each station (before / after unloading)
                route_stops = []
                remaining_load = current_load
                for stop in vehicle_load_detail:
                    route_stops.append({
                        'station_name': stop['station_name'],
                        'action': 'unload',
                        'unload_amount': stop['load_amount'],
                        'load_before_unload': remaining_load,  # Load before unloading
                        'load_after_unload': remaining_load - stop['load_amount'],  # Load after unloading
                        'load_rate_before': remaining_load / small['capacity'] * 100,
                        'load_rate_after': (remaining_load - stop['load_amount']) / small['capacity'] * 100
                    })
                    remaining_load -= stop['load_amount']

                vehicles_detail.append({
                    'vehicle_id': f"S-{v_idx + 1}",
                    'type': 'small',
                    'capacity': small['capacity'],
                    'total_load': current_load,
                    'load_rate': current_load / small['capacity'] * 100,
                    'route_stops': route_stops,
                    'n_stops': len(route_stops)
                })

            # Assign large vehicles
            for v_idx in range(n_large):
                vehicle_load_detail = []
                current_load = 0

                for s_idx, s in enumerate(station_demands):
                    if remaining_demands[s_idx] > 0:
                        can_load = min(remaining_demands[s_idx], large['capacity'] - current_load)
                        if can_load > 0:
                            vehicle_load_detail.append({
                                'station_name': s['station_name'],
                                'station_index': s['station_index'],
                                'load_amount': can_load,
                                'load_after_stop': current_load + can_load
                            })
                            current_load += can_load
                            remaining_demands[s_idx] -= can_load

                        if current_load >= large['capacity']:
                            break

                # Utilization on arrival at each station
                route_stops = []
                remaining_load = current_load
                for stop in vehicle_load_detail:
                    route_stops.append({
                        'station_name': stop['station_name'],
                        'action': 'unload',
                        'unload_amount': stop['load_amount'],
                        'load_before_unload': remaining_load,
                        'load_after_unload': remaining_load - stop['load_amount'],
                        'load_rate_before': remaining_load / large['capacity'] * 100,
                        'load_rate_after': (remaining_load - stop['load_amount']) / large['capacity'] * 100
                    })
                    remaining_load -= stop['load_amount']

                vehicles_detail.append({
                    'vehicle_id': f"L-{v_idx + 1}",
                    'type': 'large',
                    'capacity': large['capacity'],
                    'total_load': current_load,
                    'load_rate': current_load / large['capacity'] * 100,
                    'route_stops': route_stops,
                    'n_stops': len(route_stops)
                })

            best_plan = {
                'vehicles': vehicles_detail,
                'n_small': n_small,
                'n_large': n_large,
                'total_trip_cost': total_cost,
                'total_capacity': capacity,
                'total_demand': total_demand,
                'distance': distance,
                'station_demands': station_demands,  # Per-station demand details
                'feasible': True
            }

    if best_plan is None:
        return {
            'vehicles': [],
            'n_small': 0,
            'n_large': 0,
            'total_trip_cost': float('inf'),
            'total_capacity': 0,
            'total_demand': total_demand,
            'feasible': False
        }

    return best_plan


def calculate_group_distance(cdc_distance: float, inter_station_distance: float, k: int) -> float:
    """
    Compute the total distance for delivering to a group of stations.

    Args:
        cdc_distance: Distance from the CDC to the city
        inter_station_distance: Inter-station distance
        k: Number of stations

    Returns:
        Total distance
    """
    return 2 * cdc_distance + (k - 1) * inter_station_distance


def calculate_group_transport_cost(city_code: str, station_indices: list, T: int) -> dict:
    """
    Compute the transportation cost of a station group (public interface).

    Args:
        city_code: City identifier
        station_indices: List of station indices
        T: Replenishment cycle

    Returns:
        {
            'single_trip_cost': cost of one delivery round,
            'daily_transport_cost': daily transportation cost,
            'vehicle_plan': detailed vehicle configuration
        }
    """
    plan = calculate_vehicle_plan(city_code, station_indices, T)

    return {
        'single_trip_cost': plan['total_trip_cost'],
        'daily_transport_cost': plan['total_trip_cost'] / T,
        'vehicle_plan': plan
    }


def optimize_city_routes(city_code: str, T: int, verbose: bool = False) -> dict:
    """
    Optimize the station grouping and vehicle dispatch of a city.

    Enumerates all feasible groupings and selects the minimum-cost one.

    Args:
        city_code: City identifier
        T: Replenishment cycle
        verbose: Whether to print detailed output

    Returns:
        {
            'city_code': city identifier,
            'T': replenishment cycle,
            'grouping_plan': optimal grouping plan,
            'vehicle_plans': vehicle configuration per group,
            'single_trip_cost': total cost of one delivery round,
            'daily_transport_cost': daily transportation cost,
            'n_vehicles': total number of vehicles,
            'feasible': whether a feasible plan exists
        }
    """
    n_stations = get_station_count(city_code)

    best_solution = None
    best_cost = float('inf')

    # Enumerate all grouping plans
    for grouping in generate_all_groupings(n_stations, MAX_STATIONS_PER_TRIP):
        total_trip_cost = 0
        vehicle_plans = []
        feasible = True

        for group in grouping:
            plan = calculate_vehicle_plan(city_code, group, T)

            if not plan['feasible']:
                feasible = False
                break

            total_trip_cost += plan['total_trip_cost']
            vehicle_plans.append({
                'group': group,
                'plan': plan
            })

        if not feasible:
            continue

        # Update the incumbent
        if total_trip_cost < best_cost:
            best_cost = total_trip_cost
            best_solution = {
                'city_code': city_code,
                'T': T,
                'grouping_plan': grouping,
                'vehicle_plans': vehicle_plans,
                'single_trip_cost': total_trip_cost,
                'daily_transport_cost': total_trip_cost / T,
                'n_vehicles': sum(p['plan']['n_small'] + p['plan']['n_large'] for p in vehicle_plans),
                'feasible': True
            }

    if best_solution is None:
        return {
            'city_code': city_code,
            'T': T,
            'grouping_plan': [],
            'vehicle_plans': [],
            'single_trip_cost': float('inf'),
            'daily_transport_cost': float('inf'),
            'n_vehicles': 0,
            'feasible': False
        }

    if verbose:
        print_route_plan(best_solution)

    return best_solution


def print_route_plan(solution: dict):
    """Print the route optimization result."""
    city = solution['city_code']
    T = solution['T']

    print(f"\n{'='*70}")
    print(f"City {city} route optimization (T={T} days)")
    print(f"{'='*70}")

    print(f"\nGrouping plan:")
    for i, vp in enumerate(solution['vehicle_plans']):
        group = vp['group']
        plan = vp['plan']
        stations_str = ', '.join([f"{city}_{s+1}" for s in group])

        print(f"  Group {i+1}: stations [{stations_str}]")
        print(f"    Total demand: {plan['total_demand']:,} pcs")
        print(f"    Route distance: {plan['distance']} km")
        print(f"    Vehicles: small x{plan['n_small']} + large x{plan['n_large']}")
        print(f"    Cost per delivery round: {plan['total_trip_cost']:,.1f} CNY")

    print(f"\nCost summary:")
    print(f"  Total cost per delivery round: {solution['single_trip_cost']:,.1f} CNY")
    print(f"  Daily transport cost: {solution['daily_transport_cost']:,.1f} CNY")
    print(f"  Total vehicles: {solution['n_vehicles']}")
    print(f"{'='*70}\n")


def quick_route_plan(city_code: str, T: int) -> list:
    """
    Quickly produce a reasonable grouping plan (not optimal; for testing).

    Strategy: greedy — sort stations by demand and fill each vehicle in turn.

    Args:
        city_code: City identifier
        T: Replenishment cycle

    Returns:
        Grouping plan, e.g. [[0,1], [2,3], [4,5]]
    """
    n_stations = get_station_count(city_code)
    stations = list(range(n_stations))

    # Sort by demand (descending)
    stations.sort(key=lambda i: get_daily_demand(city_code, i), reverse=True)

    groups = []
    current_group = []
    current_demand = 0
    large = get_vehicle_type('large')

    for s in stations:
        demand = get_daily_demand(city_code, s) * T

        # Check whether adding to the current group would overload
        if len(current_group) < MAX_STATIONS_PER_TRIP and current_demand + demand <= large['capacity']:
            current_group.append(s)
            current_demand += demand
        else:
            # Start a new group
            if current_group:
                groups.append(current_group)
            current_group = [s]
            current_demand = demand

    if current_group:
        groups.append(current_group)

    return groups
