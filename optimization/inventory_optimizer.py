"""
Inventory optimization module.
Determines the optimal replenishment cycle for a single city.
"""

from models import calculate_city_total_storage_cost
from .route_optimizer import optimize_city_routes


def calculate_city_total_cost(city_code: str, T: int, verbose: bool = False) -> dict:
    """
    Compute the total daily cost of a city under a given replenishment cycle.

    Args:
        city_code: City identifier
        T: Replenishment cycle
        verbose: Whether to print detailed output

    Returns:
        {
            'city_code': city identifier,
            'T': replenishment cycle,
            'storage_cost': daily holding cost,
            'transport_cost': daily transportation cost,
            'total_cost': total daily cost,
            'route_plan': route optimization details,
            'feasible': whether the plan is feasible
        }
    """
    # 1. Holding cost
    storage_cost = calculate_city_total_storage_cost(city_code, T)

    # 2. Transportation cost (via route optimization)
    route_result = optimize_city_routes(city_code, T, verbose=verbose)

    if not route_result['feasible']:
        return {
            'city_code': city_code,
            'T': T,
            'storage_cost': storage_cost,
            'transport_cost': float('inf'),
            'total_cost': float('inf'),
            'route_plan': route_result,
            'feasible': False
        }

    transport_cost = route_result['daily_transport_cost']
    total_cost = storage_cost + transport_cost

    return {
        'city_code': city_code,
        'T': T,
        'storage_cost': storage_cost,
        'transport_cost': transport_cost,
        'total_cost': total_cost,
        'route_plan': route_result,
        'feasible': True
    }


def optimize_city_inventory(city_code: str, verbose: bool = False) -> dict:
    """
    Find the optimal replenishment cycle of a single city.

    Sweeps T = 1..7, computes the total cost under each cycle, and returns the optimum.

    Args:
        city_code: City identifier
        verbose: Whether to print detailed output

    Returns:
        {
            'city_code': city identifier,
            'optimal_T': optimal replenishment cycle,
            'optimal_cost': optimal total daily cost,
            'storage_cost': holding cost,
            'transport_cost': transportation cost,
            'route_plan': optimal route plan,
            'all_results': [results for T = 1..7],
            'cost_breakdown': cost breakdown
        }
    """
    all_results = []
    best_result = None
    best_cost = float('inf')

    if verbose:
        print(f"\n{'='*70}")
        print(f"City {city_code} inventory optimization")
        print(f"{'='*70}")
        print(f"\n{'T(d)':<8} {'Holding':<15} {'Transport':<15} {'Total':<15} {'Vehicles':<8}")
        print("-" * 70)

    for T in range(1, 8):
        result = calculate_city_total_cost(city_code, T, verbose=False)
        all_results.append(result)

        if result['feasible'] and result['total_cost'] < best_cost:
            best_cost = result['total_cost']
            best_result = result

        if verbose:
            n_vehicles = result['route_plan']['n_vehicles'] if result['feasible'] else '-'
            cost_str = f"{result['total_cost']:,.1f}" if result['feasible'] else 'infeasible'
            print(f"{T:<8} {result['storage_cost']:<15,.1f} {result['transport_cost']:<15,.1f} "
                  f"{cost_str:<15} {n_vehicles}")

    if best_result is None:
        raise ValueError(f"City {city_code}: no feasible solution found")

    if verbose:
        print(f"\nOptimal plan: T={best_result['T']} days, total daily cost={best_result['total_cost']:,.1f} CNY")
        # Print the route details of the optimal plan
        optimize_city_routes(city_code, best_result['T'], verbose=True)

    return {
        'city_code': city_code,
        'optimal_T': best_result['T'],
        'optimal_cost': best_result['total_cost'],
        'storage_cost': best_result['storage_cost'],
        'transport_cost': best_result['transport_cost'],
        'route_plan': best_result['route_plan'],
        'all_results': all_results,
        'cost_breakdown': {
            'storage': best_result['storage_cost'],
            'transport': best_result['transport_cost'],
            'total': best_result['total_cost']
        }
    }


def analyze_cost_trend(city_code: str) -> dict:
    """
    Analyze the cost trend of a city across replenishment cycles.

    Returns data suitable for visualization.

    Args:
        city_code: City identifier

    Returns:
        {
            'T_values': [1, 2, 3, 4, 5, 6, 7],
            'storage_costs': [...],
            'transport_costs': [...],
            'total_costs': [...]
        }
    """
    T_values = list(range(1, 8))
    storage_costs = []
    transport_costs = []
    total_costs = []

    for T in T_values:
        result = calculate_city_total_cost(city_code, T)
        storage_costs.append(result['storage_cost'])
        transport_costs.append(result['transport_cost'])
        total_costs.append(result['total_cost'])

    return {
        'city_code': city_code,
        'T_values': T_values,
        'storage_costs': storage_costs,
        'transport_costs': transport_costs,
        'total_costs': total_costs
    }


def print_inventory_analysis(result: dict):
    """Print the inventory optimization analysis."""
    city = result['city_code']

    print(f"\n{'='*70}")
    print(f"City {city} inventory optimization report")
    print(f"{'='*70}")

    print(f"\n[Cost comparison]")
    print(f"{'T(d)':<8} {'Holding':<15} {'Transport':<15} {'Total':<15}")
    print("-" * 60)

    for r in result['all_results']:
        marker = " <- optimal" if r['T'] == result['optimal_T'] else ""
        print(f"{r['T']:<8} {r['storage_cost']:<15,.1f} {r['transport_cost']:<15,.1f} "
              f"{r['total_cost']:<15,.1f}{marker}")

    print(f"\n[Optimal plan details]")
    print(f"  Replenishment cycle T: {result['optimal_T']} days")
    print(f"  Daily holding cost: {result['storage_cost']:,.1f} CNY")
    print(f"  Daily transport cost: {result['transport_cost']:,.1f} CNY")
    print(f"  Total daily cost: {result['optimal_cost']:,.1f} CNY")
    print(f"{'='*70}\n")
