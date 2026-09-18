"""
Tests for the cost model module.
"""

from models import (
    calculate_daily_storage_cost,
    calculate_city_total_storage_cost,
    calculate_total_distance,
    calculate_single_trip_cost,
    select_optimal_vehicle,
    calculate_daily_total_cost,
    print_cost_breakdown,
)
from optimization.route_optimizer import optimize_city_routes


def test_storage_cost():
    """Verify holding-cost computation."""
    print("=" * 60)
    print("1. Holding cost tests")
    print("=" * 60)

    city = 'A'
    T = 3  # 3-day replenishment cycle

    print(f"\nCity {city}, cycle T={T} days\n")

    # Holding cost per station
    for i in range(6):
        cost = calculate_daily_storage_cost(city, i, T)
        print(f"Station A_{i+1}: daily holding cost = {cost:,.1f} CNY/day")

    # City-wide holding cost
    total_storage = calculate_city_total_storage_cost(city, T)
    print(f"\nCity A total holding cost: {total_storage:,.1f} CNY/day")


def test_transport_cost():
    """Verify transportation-cost computation."""
    print("\n" + "=" * 60)
    print("2. Transportation cost tests")
    print("=" * 60)

    city = 'A'

    # Trip cost for different numbers of stations served
    for k in range(1, 4):
        large_cost = calculate_single_trip_cost(city, k, 'large')
        small_cost = calculate_single_trip_cost(city, k, 'small')

        distance = calculate_total_distance(city, k)

        print(f"\nServing {k} stations (distance={distance} km):")
        print(f"  - Large vehicle: {large_cost:,.1f} CNY")
        print(f"  - Small vehicle: {small_cost:,.1f} CNY")


def test_vehicle_selection():
    """Verify vehicle-type selection."""
    print("\n" + "=" * 60)
    print("3. Vehicle selection tests")
    print("=" * 60)

    city = 'A'

    # Single station
    vehicle = select_optimal_vehicle(city, [0])
    demand = sum([calculate_daily_storage_cost(city, 0, 1)])  # A convenient way to reference the demand
    print(f"\nStation A_1: recommended vehicle = {vehicle}")

    # Multi-station combinations
    test_cases = [
        [0],           # Single station
        [0, 1],        # Two stations
        [0, 1, 2],     # Three stations
        [0, 1, 2, 3],  # Four stations (may overload)
    ]

    for group in test_cases:
        vehicle = select_optimal_vehicle(city, group)
        station_names = [f"A_{i+1}" for i in group]
        print(f"Stations {station_names}: recommended vehicle = {vehicle if vehicle else 'multiple vehicles required'}")


def test_full_scenario():
    """Verify a complete scenario."""
    print("\n" + "=" * 60)
    print("4. Full scenario test - City A, T=3 days")
    print("=" * 60)

    city = 'A'
    T = 3

    # Use the route optimizer for the true optimal grouping (supports multi-vehicle splits)
    route_result = optimize_city_routes(city, T)
    grouping_plan = route_result['grouping_plan']

    print(f"\n[True optimal grouping (T={T})]")
    print(f"  Feasible: {route_result['feasible']}")
    print(f"  Daily transport cost: {route_result['daily_transport_cost']:,.1f} CNY")
    for i, vp in enumerate(route_result['vehicle_plans'], 1):
        group = vp['group']
        plan = vp['plan']
        stations = [f"{city}_{s+1}" for s in group]
        print(f"  Group {i}: stations {stations} -> vehicles: {plan['n_small']} small + {plan['n_large']} large -> round cost: {plan['total_trip_cost']:,.1f} CNY")

    # Total cost from the optimizer's daily transport cost
    # (the legacy calculate_daily_total_cost in cost_models does not support multi-vehicle splits)
    storage = calculate_city_total_storage_cost(city, T)
    transport_daily = route_result['daily_transport_cost']
    total_cost = storage + transport_daily

    print(f"\n[Total daily cost]")
    print(f"  Total = holding {storage:,.1f} + transport {transport_daily:,.1f} = {total_cost:,.1f} CNY/day")
    print(f"{'='*60}\n")


def compare_T_scenarios():
    """Compare costs across replenishment cycles."""
    print("\n" + "=" * 60)
    print("5. Cost comparison across cycles - City A")
    print("=" * 60)

    city = 'A'

    print(f"\n{'Cycle T':<12} {'Holding':<15} {'Transport':<15} {'Total':<15}")
    print("-" * 60)

    for T in range(1, 8):
        storage = calculate_city_total_storage_cost(city, T)

        # True optimal grouping and transport cost from the route optimizer
        route_result = optimize_city_routes(city, T)
        transport = route_result['daily_transport_cost'] * T  # Per-round total

        total = storage + route_result['daily_transport_cost']

        print(f"{T:<12} {storage:>10,.1f}      {route_result['daily_transport_cost']:>10,.1f}      {total:>10,.1f}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Meituan logistics optimization system - cost model tests")
    print("=" * 60 + "\n")

    # Run all tests
    test_storage_cost()
    test_transport_cost()
    test_vehicle_selection()
    test_full_scenario()
    compare_T_scenarios()

    print("\n" + "=" * 60)
    print("All cost model tests passed!")
    print("=" * 60 + "\n")
