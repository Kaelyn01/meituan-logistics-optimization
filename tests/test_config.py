import sys
from datetime import datetime
from pathlib import Path

# 导入配置模块
from config import (
    get_daily_demand,
    get_city_total_demand,
    get_station_count,
    get_city_parameters,
    get_vehicle_type,
    get_all_stations,
    
    # 也可以直接访问常量
    CITIES,
    VEHICLE_TYPES,
    MAX_STATIONS_PER_TRIP,
    LEAD_TIME,
)


def test_basic_data():
    """测试基础数据访问"""
    print("=" * 50)
    print("1. 访问基础常量")
    print("=" * 50)
    
    print(f"\n所有城市列表：{CITIES}")
    print(f"约束条件 - 每车最多站点数：{MAX_STATIONS_PER_TRIP}")
    print(f"约束条件 - 提前期：{LEAD_TIME} 天")
    

def test_vehicle_types():
    """测试车型参数"""
    print("\n" + "=" * 50)
    print("2. 车型参数查询")
    print("=" * 50)
    
    large = get_vehicle_type('large')
    small = get_vehicle_type('small')
    
    print(f"\n大车参数:")
    print(f"  - 固定成本：{large['fixed_cost']} 元/次")
    print(f"  - 变动成本：{large['variable_cost']} 元/km")
    print(f"  - 载货量：{large['capacity']:,} pcs")
    
    print(f"\n小车参数:")
    print(f"  - 固定成本：{small['fixed_cost']} 元/次")
    print(f"  - 变动成本：{small['variable_cost']} 元/km")
    print(f"  - 载货量：{small['capacity']:,} pcs")


def test_city_demands():
    """测试城市需求数据"""
    print("\n" + "=" * 50)
    print("3. 各城市站点需求统计")
    print("=" * 50)
    
    for city in CITIES:
        station_count = get_station_count(city)
        total_demand = get_city_total_demand(city)
        
        print(f"\nCity {city}:")
        print(f"  - 站点数量：{station_count} 个")
        print(f"  - 总日均销量：{total_demand:,} pcs/天")
        print(f"  - 站点列表：{get_all_stations(city)}")


def test_station_details():
    """测试单个站点详情"""
    print("\n" + "=" * 50)
    print("4. City A 各站点详细销量")
    print("=" * 50)
    
    stations = get_all_stations('A')
    for i, station in enumerate(stations):
        demand = get_daily_demand('A', i)
        print(f"  {station}: {demand:,} pcs/天")


def test_city_parameters():
    """测试城市参数（距离、仓租）"""
    print("\n" + "=" * 50)
    print("5. 各城市物流参数")
    print("=" * 50)
    
    for city in CITIES:
        params = get_city_parameters(city)
        print(f"\nCity {city}:")
        print(f"  - CDC 到该城市距离：{params['cdc_distance']} km")
        print(f"  - 单平方米租金：{params['rent_per_m2']} 元/m²/天")
        print(f"  - 站点间距离：{params['inter_station_distance']} km")


def calculate_storage_cost_example():
    """示例：计算某站点的日仓租"""
    print("\n" + "=" * 50)
    print("6. 计算示例：City A 第 1 个站点的仓储成本")
    print("=" * 50)
    
    from config import STORAGE_CONVERSION
    
    city = 'A'
    station_index = 0
    T = 3  # 假设订货周期为 3 天
    
    # 获取数据
    daily_demand = get_daily_demand(city, station_index)
    city_params = get_city_parameters(city)
    rent = city_params['rent_per_m2']
    
    # 计算
    peak_inventory = daily_demand * (T + LEAD_TIME)  # 峰值库存 (pcs)
    required_area = peak_inventory / STORAGE_CONVERSION  # 所需面积 (m²)
    daily_storage_cost = required_area * rent  # 日仓租 (元)
    
    print(f"\n已知条件:")
    print(f"  - 站点：{get_all_stations(city)[station_index]}")
    print(f"  - 日均销量：{daily_demand:,} pcs/天")
    print(f"  - 订货周期 T: {T} 天")
    print(f"  - 提前期：{LEAD_TIME} 天")
    print(f"  - 单位租金：{rent} 元/m²/天")
    
    print(f"\n计算过程:")
    print(f"  1. 峰值库存 = {daily_demand:,} × ({T} + {LEAD_TIME}) = {peak_inventory:,} pcs")
    print(f"  2. 所需面积 = {peak_inventory:,} ÷ {STORAGE_CONVERSION} = {required_area:.1f} m²")
    print(f"  3. 日仓租 = {required_area:.1f} × {rent} = {daily_storage_cost:.1f} 元/天")


def calculate_transport_cost_example():
    """示例：计算运输成本"""
    print("\n" + "=" * 50)
    print("7. 计算示例：City A 的运输成本")
    print("=" * 50)
    
    city = 'A'
    k = 3  # 假设一辆车服务 3 个站点
    vehicle = 'large'  # 使用大车
    
    # 获取数据
    city_params = get_city_parameters(city)
    cdc_distance = city_params['cdc_distance']
    inter_station = city_params['inter_station_distance']
    vehicle_params = get_vehicle_type(vehicle)
    
    # 计算里程
    total_distance = 2 * cdc_distance + (k - 1) * inter_station
    
    # 计算成本
    fixed_cost = vehicle_params['fixed_cost']
    variable_cost = vehicle_params['variable_cost'] * total_distance
    total_cost = fixed_cost + variable_cost
    
    print(f"\n已知条件:")
    print(f"  - 城市：City {city}")
    print(f"  - 车型：{vehicle} (大车)")
    print(f"  - 服务站点数：{k} 个")
    print(f"  - CDC 距离：{cdc_distance} km")
    
    print(f"\n计算过程:")
    print(f"  1. 总里程 = 2 × {cdc_distance} + ({k}-1) × {inter_station}")
    print(f"     = {total_distance} km")
    print(f"  2. 固定成本 = {fixed_cost} 元")
    print(f"  3. 变动成本 = {vehicle_params['variable_cost']} × {total_distance} = {variable_cost:.1f} 元")
    print(f"  4. 总运输成本 = {fixed_cost} + {variable_cost:.1f} = {total_cost:.1f} 元")


class TeeOutput:
    """将输出同时打印到控制台和文件"""
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
    # 创建 output 目录（如果不存在）
    output_dir = Path(__file__).parent / "output" / "logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成带时间戳的日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = output_dir / f"config_test_{timestamp}.log"
    
    # 打开日志文件
    with open(log_file, 'w', encoding='utf-8') as f_log:
        # 重定向输出
        original_stdout = sys.stdout
        sys.stdout = TeeOutput(original_stdout, f_log)
        
        try:
            print("\n" + "🚀" * 25)
            print("美团物流优化系统 - 配置参数演示")
            print("🚀" * 25 + "\n")
            
            # 运行所有测试
            test_basic_data()
            test_vehicle_types()
            test_city_demands()
            test_station_details()
            test_city_parameters()
            calculate_storage_cost_example()
            calculate_transport_cost_example()
            
            print("\n" + "=" * 50)
            print("✅ 所有配置参数测试完成！")
            print("=" * 50)
            print(f"\n💡 日志已保存到：{log_file}")
            print("   在其他文件中使用：from config import get_daily_demand, get_city_parameters\n")
        finally:
            # 恢复标准输出
            sys.stdout = original_stdout
