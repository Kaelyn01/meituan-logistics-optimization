#!/usr/bin/env python3
"""
Meituan logistics optimization system — main entry point.

Joint inventory and routing optimization for a multi-city retail network.
"""

import json
from datetime import datetime
from pathlib import Path

from config import CITIES
from optimization import (
    optimize_city_inventory,
    global_optimization,
    optimize_city_routes,
)


def run_single_city_analysis(city_code: str, verbose: bool = True):
    """Run the analysis for a single city."""
    if verbose:
        print(f"\n{'='*70}")
        print(f"City {city_code} standalone optimization")
        print(f"{'='*70}")

    result = optimize_city_inventory(city_code, verbose=verbose)
    return result


def run_all_cities_analysis(verbose: bool = True):
    """Run standalone optimization for every city."""
    if verbose:
        print(f"\n{'='*70}")
        print(f"Standalone optimization results per city")
        print(f"{'='*70}")
        print(f"\n{'City':<6} {'Opt. T':<8} {'Holding':<15} {'Transport':<15} {'Daily total':<15}")
        print("-" * 70)

    results = {}
    total_cost = 0

    for city in CITIES:
        result = optimize_city_inventory(city, verbose=False)
        results[city] = result
        total_cost += result['optimal_cost']

        if verbose:
            print(f"{city:<6} {result['optimal_T']:<8} {result['storage_cost']:<15,.1f} "
                  f"{result['transport_cost']:<15,.1f} {result['optimal_cost']:<15,.1f}")

    if verbose:
        print(f"\n{'':<6} {'':<8} {'':<15} {'Standalone sum:':<15} {total_cost:<15,.1f}")

    return results, total_cost


def run_global_optimization(top_k: int = 10, verbose: bool = True):
    """Run the global optimization."""
    result = global_optimization(top_k=top_k, verbose=verbose)
    return result


def generate_detailed_report(global_result: dict, output_dir: Path):
    """Write the detailed report files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Save the global optimal solution (JSON)
    optimal_file = output_dir / f"optimal_solution_{timestamp}.json"
    with open(optimal_file, 'w', encoding='utf-8') as f:
        json.dump(global_result['optimal_solution'], f, ensure_ascii=False, indent=2)

    # 2. Save the top solutions (JSON)
    top_file = output_dir / f"top_solutions_{timestamp}.json"
    with open(top_file, 'w', encoding='utf-8') as f:
        json.dump(global_result['top_solutions'], f, ensure_ascii=False, indent=2)

    # 3. Write the text report
    report_file = output_dir / f"optimization_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("Meituan Logistics Optimization System — Optimization Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        # Optimal solution
        optimal = global_result['optimal_solution']
        f.write("[Global optimal solution]\n\n")
        f.write(f"Minimum system total daily cost: {optimal['total_cost']:,.2f} CNY\n")
        f.write(f"  - Total holding cost: {optimal['total_storage_cost']:,.2f} CNY\n")
        f.write(f"  - Total transport cost: {optimal['total_transport_cost']:,.2f} CNY\n\n")

        f.write("Per-city configuration:\n")
        for city, T in optimal['T_combo'].items():
            city_result = next(r for r in optimal['city_results'] if r['city_code'] == city)
            route_plan = city_result['route_plan']

            f.write(f"  City {city}: T={T} days\n")
            f.write(f"    Holding cost: {city_result['storage_cost']:,.2f} CNY/day\n")
            f.write(f"    Transport cost: {city_result['transport_cost']:,.2f} CNY/day\n")
            f.write(f"    Total daily cost: {city_result['total_cost']:,.2f} CNY/day\n")

            # Vehicle dispatch details
            f.write(f"    Vehicle dispatch:\n")
            for i, vp in enumerate(route_plan['vehicle_plans'], 1):
                group = vp['group']
                plan = vp['plan']
                stations_str = ', '.join([f"{city}_{s + 1}" for s in group])
                f.write(f"      Group {i}: stations [{stations_str}]\n")
                f.write(f"        Vehicles: small x{plan['n_small']} + large x{plan['n_large']}\n")
                f.write(f"        Total demand: {plan['total_demand']:,} pcs\n")
                f.write(f"        Route distance: {plan['distance']} km\n")

                for v in plan['vehicles']:
                    if 'vehicle_id' in v:
                        f.write(
                            f"        |- {v['vehicle_id']} ({v['type']}): load {v['total_load']:,} pcs ({v['load_rate']:.1f}%)\n")
                        for stop in v['route_stops']:
                            f.write(
                                f"        |    \\- {stop['station_name']}: unload {stop['unload_amount']:,} pcs, utilization {stop['load_rate_before']:.1f}%->{stop['load_rate_after']:.1f}%\n")
                    else:
                        # Backward compatibility with the legacy JSON format
                        f.write(f"        |- {v['type']}: load {v.get('load', 0):,} pcs\n")

                f.write(f"        Cost per delivery round: {plan['total_trip_cost']:,.2f} CNY\n")
            f.write("\n")

        # Top-solution comparison
        f.write("\n[Top 10 solutions]\n\n")
        f.write(f"{'Rank':<6} {'A':<4} {'B':<4} {'C':<4} {'D':<4} {'E':<4} {'Total cost':<15}\n")
        f.write("-" * 50 + "\n")
        for i, sol in enumerate(global_result['top_solutions'][:10], 1):
            T = sol['T_combo']
            marker = " <- optimal" if i == 1 else ""
            f.write(f"{i:<6} {T['A']:<4} {T['B']:<4} {T['C']:<4} {T['D']:<4} {T['E']:<4} "
                    f"{sol['total_cost']:<15,.2f}{marker}\n")

    return {
        'optimal_json': optimal_file,
        'top_json': top_file,
        'report': report_file
    }

def print_final_summary(global_result: dict):
    """Print the final summary (including detailed vehicle dispatch)."""
    optimal = global_result['optimal_solution']

    print("\n" + "=" * 70)
    print("Meituan logistics optimization system — final results")
    print("=" * 70)

    print(f"\nMinimum system total daily cost: {optimal['total_cost']:,.2f} CNY")
    print(f"\nCost composition:")
    print(
        f"   Total holding cost: {optimal['total_storage_cost']:,.2f} CNY ({optimal['total_storage_cost'] / optimal['total_cost'] * 100:.1f}%)")
    print(
        f"   Total transport cost: {optimal['total_transport_cost']:,.2f} CNY ({optimal['total_transport_cost'] / optimal['total_cost'] * 100:.1f}%)")

    print(f"\nOptimal configuration per city:")
    print(f"{'City':<6} {'Cycle T':<12} {'Daily total':<15} {'Vehicles':<8}")
    print("-" * 50)
    for city, T in optimal['T_combo'].items():
        city_result = next(r for r in optimal['city_results'] if r['city_code'] == city)
        n_vehicles = city_result['route_plan']['n_vehicles']
        print(f"City {city:<3} {T:<12} {city_result['total_cost']:<15,.1f} {n_vehicles}")

    # Detailed vehicle dispatch plan
    print(f"\nDetailed vehicle dispatch plan:")
    print("=" * 70)

    for city, T in optimal['T_combo'].items():
        city_result = next(r for r in optimal['city_results'] if r['city_code'] == city)
        route_plan = city_result['route_plan']

        print(f"\nCity {city} (T={T} days, one delivery round every {T} days)")
        print(f"   Daily transport cost: {city_result['transport_cost']:,.1f} CNY")
        print(f"   Cost per delivery round: {route_plan['single_trip_cost']:,.1f} CNY")
        print(
            f"   Vehicles in use: small x{sum(p['plan']['n_small'] for p in route_plan['vehicle_plans'])} + large x{sum(p['plan']['n_large'] for p in route_plan['vehicle_plans'])}")
        print()

        for group_idx, vp in enumerate(route_plan['vehicle_plans'], 1):
            group = vp['group']
            plan = vp['plan']
            stations_str = ', '.join([f"{city}_{s + 1}" for s in group])

            print(f"   Group {group_idx}: stations [{stations_str}]")
            print(f"      Total demand: {plan['total_demand']:,} pcs")
            print(f"      Route distance: {plan['distance']} km (CDC->{city} {plan['distance'] / 2:.0f}km + return)")
            print(f"      Vehicles: small x{plan['n_small']} + large x{plan['n_large']}")

            # Detailed route of every vehicle
            for vehicle in plan['vehicles']:
                if 'vehicle_id' in vehicle:
                    print(f"\n      {vehicle['vehicle_id']} ({vehicle['type']})")
                    print(
                        f"         Load: {vehicle['total_load']:,} / {vehicle['capacity']:,} pcs ({vehicle['load_rate']:.1f}%)")
                    print(f"         Stations visited: {vehicle['n_stops']}")
                    print(f"         Route details:")

                    for stop_idx, stop in enumerate(vehicle['route_stops'], 1):
                        print(f"           {stop_idx}. {stop['station_name']}")
                        print(f"              Unload: {stop['unload_amount']:,} pcs")
                        print(
                            f"              Load before unloading: {stop['load_before_unload']:,} pcs ({stop['load_rate_before']:.1f}%)")
                        print(
                            f"              Load after unloading: {stop['load_after_unload']:,} pcs ({stop['load_rate_after']:.1f}%)")
                else:
                    # Backward compatibility with the legacy JSON format
                    print(f"\n      {vehicle['type']}")
                    print(f"         Load: {vehicle.get('load', 0):,} pcs")

            print(f"      Cost per delivery round: {plan['total_trip_cost']:,.1f} CNY")
            print()

    print("=" * 70)
    print("Optimization complete! Detailed reports saved to output/")
    print("=" * 70 + "\n")


def main():
    """Main program."""
    print("\n" + "=" * 70)
    print("Meituan Logistics Optimization System")
    print("Joint inventory and routing optimization for a multi-city retail network")
    print("=" * 70 + "\n")

    # 1. Standalone per-city optimization (quick preview)
    print("\n[Stage 1] Standalone optimization per city...")
    city_results, independent_total = run_all_cities_analysis(verbose=True)

    # 2. Global optimization (full search)
    print("\n[Stage 2] Global joint optimization search...")
    global_result = run_global_optimization(top_k=10, verbose=True)

    # 3. Generate detailed reports
    print("\n[Stage 3] Generating detailed reports...")
    output_dir = Path(__file__).parent / "output"
    report_files = generate_detailed_report(global_result, output_dir)

    # 4. Print the final summary
    print_final_summary(global_result)

    print(f"Report files saved:")
    for name, path in report_files.items():
        print(f"   - {name}: {path}")

    return global_result


if __name__ == "__main__":
    result = main()
