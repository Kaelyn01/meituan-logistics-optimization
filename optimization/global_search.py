"""
Global search module.
Enumerates all replenishment-cycle combinations to find the system-wide optimum.
"""

from itertools import product
from typing import List, Dict, Tuple
from config import CITIES
from .inventory_optimizer import calculate_city_total_cost


def generate_all_T_combinations() -> List[Tuple[int, ...]]:
    """
    Generate all possible cycle combinations.

    Five cities, each with T in {1,...,7}, giving 7^5 = 16,807 combinations.

    Returns:
        List of combinations; each combination is a tuple (T_A, T_B, T_C, T_D, T_E)
    """
    return list(product(range(1, 8), repeat=5))


def evaluate_T_combination(T_combo: Tuple[int, ...], verbose: bool = False) -> Dict:
    """
    Evaluate the total cost of one cycle combination.

    Args:
        T_combo: (T_A, T_B, T_C, T_D, T_E)
        verbose: Whether to print detailed output

    Returns:
        {
            'T_combo': {'A': T_A, 'B': T_B, ...},
            'city_results': [detailed result per city],
            'total_cost': system total daily cost,
            'total_storage_cost': total holding cost,
            'total_transport_cost': total transportation cost,
            'feasible': whether all cities are feasible
        }
    """
    city_results = []
    total_cost = 0
    total_storage = 0
    total_transport = 0
    feasible = True

    T_dict = dict(zip(CITIES, T_combo))

    for city, T in zip(CITIES, T_combo):
        result = calculate_city_total_cost(city, T, verbose=False)
        city_results.append(result)

        if not result['feasible']:
            feasible = False
            total_cost = float('inf')
            break

        total_cost += result['total_cost']
        total_storage += result['storage_cost']
        total_transport += result['transport_cost']

    return {
        'T_combo': T_dict,
        'city_results': city_results,
        'total_cost': total_cost,
        'total_storage_cost': total_storage,
        'total_transport_cost': total_transport,
        'feasible': feasible
    }


def global_optimization(top_k: int = 10, verbose: bool = False) -> Dict:
    """
    Global optimization: enumerate all cycle combinations and find the optimum.

    Args:
        top_k: Number of top solutions to return
        verbose: Whether to print progress

    Returns:
        {
            'optimal_solution': details of the optimal solution,
            'top_solutions': list of the top-k solutions,
            'total_combinations': total number of combinations,
            'evaluated_combinations': number of feasible combinations evaluated
        }
    """
    all_combinations = generate_all_T_combinations()
    total = len(all_combinations)

    if verbose:
        print(f"\n{'='*70}")
        print(f"Global optimization search")
        print(f"{'='*70}")
        print(f"Total combinations: {total:,} (7^5 = 16,807)")
        print(f"Evaluating...")

    # Collect all feasible solutions
    feasible_solutions = []

    for i, T_combo in enumerate(all_combinations):
        if verbose and (i + 1) % 2000 == 0:
            print(f"  Progress: {i + 1}/{total} ({(i+1)/total*100:.1f}%)")

        result = evaluate_T_combination(T_combo)

        if result['feasible']:
            feasible_solutions.append(result)

    # Sort by total cost
    feasible_solutions.sort(key=lambda x: x['total_cost'])

    if not feasible_solutions:
        raise ValueError("No feasible solution found!")

    optimal = feasible_solutions[0]
    top_solutions = feasible_solutions[:top_k]

    if verbose:
        print(f"\nSearch complete!")
        print(f"   Feasible solutions: {len(feasible_solutions)}/{total}")
        print(f"   Optimal total daily cost: {optimal['total_cost']:,.1f} CNY")
        print_global_result(optimal, top_solutions)

    return {
        'optimal_solution': optimal,
        'top_solutions': top_solutions,
        'total_combinations': total,
        'evaluated_combinations': len(feasible_solutions)
    }


def print_global_result(optimal: Dict, top_solutions: List[Dict] = None):
    """Print the global optimization result."""
    print(f"\n{'='*70}")
    print(f"Global optimal solution")
    print(f"{'='*70}")

    print(f"\n[Per-city cycle configuration]")
    for city, T in optimal['T_combo'].items():
        city_result = next(r for r in optimal['city_results'] if r['city_code'] == city)
        print(f"  City {city}: T={T}d, "
              f"holding={city_result['storage_cost']:,.0f}, "
              f"transport={city_result['transport_cost']:,.0f}, "
              f"subtotal={city_result['total_cost']:,.0f}")

    print(f"\n[Cost summary]")
    print(f"  System total daily cost: {optimal['total_cost']:,.1f} CNY")
    print(f"    - Total holding cost: {optimal['total_storage_cost']:,.1f} CNY")
    print(f"    - Total transport cost: {optimal['total_transport_cost']:,.1f} CNY")

    if top_solutions and len(top_solutions) > 1:
        print(f"\n[Top {len(top_solutions)} solutions]")
        print(f"{'Rank':<6} {'A':<4} {'B':<4} {'C':<4} {'D':<4} {'E':<4} {'Total cost':<15}")
        print("-" * 50)
        for i, sol in enumerate(top_solutions[:10], 1):
            T = sol['T_combo']
            marker = " <- optimal" if i == 1 else ""
            print(f"{i:<6} {T['A']:<4} {T['B']:<4} {T['C']:<4} {T['D']:<4} {T['E']:<4} "
                  f"{sol['total_cost']:<15,.1f}{marker}")

    print(f"{'='*70}\n")


def sensitivity_analysis(city_code: str = None) -> Dict:
    """
    Sensitivity analysis: quantify the impact of each city's cycle on total cost.

    Args:
        city_code: If given, analyze only this city; otherwise analyze all cities

    Returns:
        Sensitivity analysis results
    """
    from .inventory_optimizer import optimize_city_inventory

    cities_to_analyze = [city_code] if city_code else CITIES

    results = {}
    for city in cities_to_analyze:
        result = optimize_city_inventory(city)

        # Cost variation statistics
        all_costs = [r['total_cost'] for r in result['all_results']]
        min_cost = min(all_costs)
        max_cost = max(all_costs)

        results[city] = {
            'optimal_T': result['optimal_T'],
            'optimal_cost': result['optimal_cost'],
            'cost_range': (min_cost, max_cost),
            'cost_savings': (max_cost - min_cost) / max_cost * 100,  # Savings from optimization (%)
            'all_results': result['all_results']
        }

    return results


def get_optimal_for_city(city_code: str) -> Dict:
    """
    Return the optimal solution of a single city (convenience interface).

    Args:
        city_code: City identifier

    Returns:
        City-level optimal solution details
    """
    from .inventory_optimizer import optimize_city_inventory
    return optimize_city_inventory(city_code, verbose=False)
