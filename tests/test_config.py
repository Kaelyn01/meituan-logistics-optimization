import sys
from datetime import datetime
from pathlib import Path

# Import the configuration module
from config import (
    get_daily_demand,
    get_city_total_demand,
    get_station_count,
    get_city_parameters,
    get_vehicle_type,
    get_all_stations,

    # Constants can also be accessed directly
    CITIES,
    VEHICLE_TYPES,
    MAX_STATIONS_PER_TRIP,
    LEAD_TIME,
)


def test_basic_data():
    """Verify access to the base data."""
    print("=" * 50)
    print("1. Base constants")
    print("=" * 50)

    print(f"\nAll cities: {CITIES}")
    print(f"Constraint - max stations per trip: {MAX_STATIONS_PER_TRIP}")
    print(f"Constraint - lead time: {LEAD_TIME} days")


def test_vehicle_types():
    """Verify vehicle parameters."""
    print("\n" + "=" * 50)
    print("2. Vehicle parameters")
    print("=" * 50)

    large = get_vehicle_type('large')
    small = get_vehicle_type('small')

    print(f"\nLarge vehicle:")
    print(f"  - Fixed cost: {large['fixed_cost']} CNY/trip")
    print(f"  - Variable cost: {large['variable_cost']} CNY/km")
    print(f"  - Capacity: {large['capacity']:,} pcs")

    print(f"\nSmall vehicle:")
    print(f"  - Fixed cost: {small['fixed_cost']} CNY/trip")
    print(f"  - Variable cost: {small['variable_cost']} CNY/km")
    print(f"  - Capacity: {small['capacity']:,} pcs")


def test_city_demands():
    """Verify per-city demand data."""
    print("\n" + "=" * 50)
    print("3. Station demand statistics per city")
    print("=" * 50)

    for city in CITIES:
        station_count = get_station_count(city)
        total_demand = get_city_total_demand(city)

        print(f"\nCity {city}:")
        print(f"  - Stations: {station_count}")
        print(f"  - Total average daily sales: {total_demand:,} pcs/day")
        print(f"  - Station list: {get_all_stations(city)}")


def test_station_details():
    """Verify per-station details."""
    print("\n" + "=" * 50)
    print("4. Detailed daily sales of City A stations")
    print("=" * 50)

    stations = get_all_stations('A')
    for i, station in enumerate(stations):
        demand = get_daily_demand('A', i)
        print(f"  {station}: {demand:,} pcs/day")


def test_city_parameters():
    """Verify city parameters (distances, rent)."""
    print("\n" + "=" * 50)
    print("5. Logistics parameters per city")
    print("=" * 50)

    for city in CITIES:
        params = get_city_parameters(city)
        print(f"\nCity {city}:")
        print(f"  - CDC distance: {params['cdc_distance']} km")
        print(f"  - Rent per m^2: {params['rent_per_m2']} CNY/m^2/day")
        print(f"  - Inter-station distance: {params['inter_station_distance']} km")


def calculate_storage_cost_example():
    """Worked example: daily holding cost of one station."""
    print("\n" + "=" * 50)
    print("6. Worked example: holding cost of the first City A station")
    print("=" * 50)

    from config import STORAGE_CONVERSION

    city = 'A'
    station_index = 0
    T = 3  # Assume a 3-day replenishment cycle

    # Fetch inputs
    daily_demand = get_daily_demand(city, station_index)
    city_params = get_city_parameters(city)
    rent = city_params['rent_per_m2']

    # Compute
    peak_inventory = daily_demand * (T + LEAD_TIME)  # Peak inventory (pcs)
    required_area = peak_inventory / STORAGE_CONVERSION  # Required area (m^2)
    daily_storage_cost = required_area * rent  # Daily holding cost (CNY)

    print(f"\nGiven:")
    print(f"  - Station: {get_all_stations(city)[station_index]}")
    print(f"  - Average daily sales: {daily_demand:,} pcs/day")
    print(f"  - Replenishment cycle T: {T} days")
    print(f"  - Lead time: {LEAD_TIME} days")
    print(f"  - Rent: {rent} CNY/m^2/day")

    print(f"\nComputation:")
    print(f"  1. Peak inventory = {daily_demand:,} x ({T} + {LEAD_TIME}) = {peak_inventory:,} pcs")
    print(f"  2. Required area = {peak_inventory:,} / {STORAGE_CONVERSION} = {required_area:.1f} m^2")
    print(f"  3. Daily holding cost = {required_area:.1f} x {rent} = {daily_storage_cost:.1f} CNY/day")


def calculate_transport_cost_example():
    """Worked example: transportation cost."""
    print("\n" + "=" * 50)
    print("7. Worked example: transportation cost of City A")
    print("=" * 50)

    city = 'A'
    k = 3  # Assume one vehicle serves 3 stations
    vehicle = 'large'  # Use the large vehicle

    # Fetch inputs
    city_params = get_city_parameters(city)
    cdc_distance = city_params['cdc_distance']
    inter_station = city_params['inter_station_distance']
    vehicle_params = get_vehicle_type(vehicle)

    # Distance
    total_distance = 2 * cdc_distance + (k - 1) * inter_station

    # Cost
    fixed_cost = vehicle_params['fixed_cost']
    variable_cost = vehicle_params['variable_cost'] * total_distance
    total_cost = fixed_cost + variable_cost

    print(f"\nGiven:")
    print(f"  - City: City {city}")
    print(f"  - Vehicle: {vehicle} (large)")
    print(f"  - Stations served: {k}")
    print(f"  - CDC distance: {cdc_distance} km")

    print(f"\nComputation:")
    print(f"  1. Total distance = 2 x {cdc_distance} + ({k}-1) x {inter_station}")
    print(f"     = {total_distance} km")
    print(f"  2. Fixed cost = {fixed_cost} CNY")
    print(f"  3. Variable cost = {vehicle_params['variable_cost']} x {total_distance} = {variable_cost:.1f} CNY")
    print(f"  4. Total transport cost = {fixed_cost} + {variable_cost:.1f} = {total_cost:.1f} CNY")


class TeeOutput:
    """Write output to the console and a file simultaneously."""
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for f in self.files:
            f.write(text)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


if __name__ == "__main__":
    # Create the output directory if it does not exist
    output_dir = Path(__file__).parent / "output" / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Timestamped log file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = output_dir / f"config_test_{timestamp}.log"

    # Open the log file
    with open(log_file, 'w', encoding='utf-8') as f_log:
        # Redirect output
        original_stdout = sys.stdout
        sys.stdout = TeeOutput(original_stdout, f_log)

        try:
            print("\n" + "=" * 50)
            print("Meituan logistics optimization system - configuration walkthrough")
            print("=" * 50 + "\n")

            # Run all tests
            test_basic_data()
            test_vehicle_types()
            test_city_demands()
            test_station_details()
            test_city_parameters()
            calculate_storage_cost_example()
            calculate_transport_cost_example()

            print("\n" + "=" * 50)
            print("All configuration tests passed!")
            print("=" * 50)
            print(f"\nLog saved to: {log_file}")
            print("   Usage elsewhere: from config import get_daily_demand, get_city_parameters\n")
        finally:
            # Restore standard output
            sys.stdout = original_stdout
