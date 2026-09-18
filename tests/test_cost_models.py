"""
测试成本计算模块
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
    """测试仓储成本计算"""
    print("=" * 60)
    print("1. 仓储成本测试")
    print("=" * 60)
    
    city = 'A'
    T = 3  # 订货周期 3 天
    
    print(f"\nCity {city}, 订货周期 T={T}天\n")
    
    # 计算每个站点的仓租
    for i in range(6):
        cost = calculate_daily_storage_cost(city, i, T)
        print(f"站点 A_{i+1}: 日仓租 = {cost:,.1f} 元/天")
    
    # 计算城市总仓租
    total_storage = calculate_city_total_storage_cost(city, T)
    print(f"\nCity A 总仓租：{total_storage:,.1f} 元/天")


def test_transport_cost():
    """测试运输成本计算"""
    print("\n" + "=" * 60)
    print("2. 运输成本测试")
    print("=" * 60)
    
    city = 'A'
    
    # 测试不同站点数的运输成本
    for k in range(1, 4):
        large_cost = calculate_single_trip_cost(city, k, 'large')
        small_cost = calculate_single_trip_cost(city, k, 'small')
        
        distance = calculate_total_distance(city, k)
        
        print(f"\n服务{k}个站点 (里程={distance} km):")
        print(f"  - 大车：{large_cost:,.1f} 元")
        print(f"  - 小车：{small_cost:,.1f} 元")


def test_vehicle_selection():
    """测试车型选择"""
    print("\n" + "=" * 60)
    print("3. 车型选择测试")
    print("=" * 60)
    
    city = 'A'
    
    # 测试单站点
    vehicle = select_optimal_vehicle(city, [0])
    demand = sum([calculate_daily_storage_cost(city, 0, 1)])  # 只是获取需求量的方式
    print(f"\n站点 A_1: 推荐车型 = {vehicle}")
    
    # 测试多站点组合
    test_cases = [
        [0],           # 单个站点
        [0, 1],        # 两个站点
        [0, 1, 2],     # 三个站点
        [0, 1, 2, 3],  # 四个站点（可能超载）
    ]
    
    for group in test_cases:
        vehicle = select_optimal_vehicle(city, group)
        station_names = [f"A_{i+1}" for i in group]
        print(f"站点{station_names}: 推荐车型 = {vehicle if vehicle else '需要多辆车'}")


def test_full_scenario():
    """测试完整场景"""
    print("\n" + "=" * 60)
    print("4. 完整场景测试 - City A, T=3 天")
    print("=" * 60)
    
    city = 'A'
    T = 3
    
    # 使用路由优化器获取真实最优分组方案（支持多车拆分）
    route_result = optimize_city_routes(city, T)
    grouping_plan = route_result['grouping_plan']
    
    print(f"\n【真实最优分组方案 (T={T})】")
    print(f"  可行性: {route_result['feasible']}")
    print(f"  日均运输成本: {route_result['daily_transport_cost']:,.1f} 元")
    for i, vp in enumerate(route_result['vehicle_plans'], 1):
        group = vp['group']
        plan = vp['plan']
        stations = [f"{city}_{s+1}" for s in group]
        print(f"  车组{i}: 站点{stations} → 车型:{plan['n_small']}小+{plan['n_large']}大 → 单次成本:{plan['total_trip_cost']:,.1f}元")
    
    # 直接使用路由优化器返回的日均运输成本计算总成本
    # （旧版 cost_models 的 calculate_daily_total_cost 不支持多车拆分）
    storage = calculate_city_total_storage_cost(city, T)
    transport_daily = route_result['daily_transport_cost']
    total_cost = storage + transport_daily
    
    print(f"\n【日总成本】")
    print(f"  日总成本 = 仓储 {storage:,.1f} + 运输 {transport_daily:,.1f} = {total_cost:,.1f} 元/天")
    print(f"{'='*60}\n")


def compare_T_scenarios():
    """比较不同订货周期的成本"""
    print("\n" + "=" * 60)
    print("5. 不同订货周期成本对比 - City A")
    print("=" * 60)
    
    city = 'A'
    
    print(f"\n{'订货周期 T':<12} {'仓储成本':<15} {'运输成本':<15} {'总成本':<15}")
    print("-" * 60)
    
    for T in range(1, 8):
        storage = calculate_city_total_storage_cost(city, T)
        
        # 使用路由优化器获取真实最优分组和运输成本
        route_result = optimize_city_routes(city, T)
        transport = route_result['daily_transport_cost'] * T  # 单次总运费
        
        total = storage + route_result['daily_transport_cost']
        
        print(f"{T:<12} {storage:>10,.1f}      {route_result['daily_transport_cost']:>10,.1f}      {total:>10,.1f}")


if __name__ == "__main__":
    print("\n" + "🧮" * 30)
    print("美团物流优化系统 - 成本计算模块测试")
    print("🧮" * 30 + "\n")
    
    # 运行所有测试
    test_storage_cost()
    test_transport_cost()
    test_vehicle_selection()
    test_full_scenario()
    compare_T_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ 所有成本计算测试完成！")
    print("=" * 60 + "\n")
