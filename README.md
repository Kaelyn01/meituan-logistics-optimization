# 美团城市群零售网络物流与库存联合优化

**Meituan Multi-City Joint Inventory–Routing Optimization**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Tests](https://github.com/Kaelyn01/meituan-logistics-optimization/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-green)

## 📝 English Abstract

This repository provides a **joint inventory–routing optimization framework** for a multi-city fresh-food logistics network. Given one central distribution center (CDC) and five satellite cities (25 retail stations in total), the model determines the optimal replenishment cycle $T^* \in \{1,\dots,7\}$ for each city and the corresponding vehicle routing plans. The objective is to minimize the sum of daily inventory holding and transportation costs. A complete enumeration of all $7^5 = 16{,}807$ global $T$-combinations guarantees system-wide optimality. The best policy achieves a total daily cost of **24,874 CNY**, outperforming uniform-$T$ baselines by up to **80.6%**.

---

## 项目概述

本项目解决某快消品巨头在主城 CDC 向周边 5 个卫星城（共 25 个零售站点）进行补货配送的联合优化问题。

**核心决策变量：**

1. 各城市的订货周期 $T \in \{1, 2, 3, 4, 5, 6, 7\}$ 天
2. 具体的车辆调度方案（站点分组 + 车型选择 + 卸货路径）

**优化目标：**

```
Min Total Cost = Σ(日均运输成本 + 日均仓储成本)
```

## 核心结果

```
🎯 全局最优方案:
   City A: T=1天, 日成本=9,130元
   City B: T=1天, 日成本=6,215元
   City C: T=2天, 日成本=4,915元
   City D: T=3天, 日成本=2,928元
   City E: T=6天, 日成本=1,686元

💰 系统日总成本最小值: 24,874 元
   - 总仓储成本: 13,409 元 (53.9%)
   - 总运输成本: 11,465 元 (46.1%)
```

相比所有城市统一周期的 uniform-$T$ 基线方案，总成本最多降低 **80.6%**。

**装载率洞察**：城市 B 中站点 `[B_4, B_5]` 采用大车配送时装载率仅为 42.5%，反映出远距离低需求站点组合容易出现运力闲置；而城市 A 的 `[A_3, A_4, A_5]` 大车装载率高达 95%，说明高需求密集区的分组能充分利用运力。

## 快速开始

### 安装

```bash
git clone https://github.com/Kaelyn01/meituan-logistics-optimization.git
cd meituan-logistics-optimization
pip install -r requirements.txt
```

### 运行优化

```bash
python main.py
```

程序将执行：

1. 各城市独立优化分析
2. 全局联合优化搜索（遍历 $7^5 = 16{,}807$ 种组合）
3. 生成详细报告到 `output/` 目录

### 运行测试

```bash
python -m pytest tests/ -v
```

### 重新生成图表

```bash
python scripts/fig1.py
python scripts/fig2.py
python scripts/fig3.py
python scripts/fig4.py
python scripts/combine_fig1_fig2.py
```

图表输出到 `figures/`，论文按相对路径 `../figures/` 引用。

## 项目结构

```
meituan-logistics-optimization/
├── main.py                     # 主程序入口
├── config/                     # 配置模块
│   └── parameters.py           # 固定参数（车型、城市距离、站点需求等）
├── models/                     # 成本计算模型
│   └── cost_models.py          # 仓储成本 + 运输成本计算
├── optimization/               # 优化算法模块
│   ├── route_optimizer.py      # 路径优化（站点分组 + 车辆调度）
│   ├── inventory_optimizer.py  # 库存优化（单城市最优 T 搜索）
│   └── global_search.py        # 全局寻优（16807 种组合枚举）
├── tests/                      # 单元测试
│   ├── test_config.py          # 配置参数测试
│   └── test_cost_models.py     # 成本计算测试
├── scripts/                    # 图表生成脚本
│   ├── fig1.py ~ fig4.py       # 单图生成
│   └── combine_fig1_fig2.py    # 论文双栏组合图
├── data/
│   └── results.json            # 各城市最优解数据（供图表与论文使用）
├── figures/                    # 生成的图表（png / pdf）
├── report/                     # 学术论文（英文）
│   ├── main.tex                # LaTeX 源文件
│   └── main.pdf                # 编译后 PDF
└── output/                     # 运行时输出（最优解 / Top 10 / 日志，已 gitignore）
```

## 核心模块说明

### `route_optimizer.py` — 路径优化

- **算法**：回溯法枚举所有合法分组（每组 ≤3 站点），选择总成本最低的方案
- **特色**：支持多车配送（当单站点需求 × T > 20万时自动拆分），并输出每辆车的逐站装载率变化（卸货前/后装载率）

### `inventory_optimizer.py` — 库存优化

- **算法**：遍历 T=1~7，计算每个周期下的总成本
- **输出**：最优 T、成本明细、各 T 值对比

### `global_search.py` — 全局寻优

- **算法**：暴力枚举 16,807 种 T 组合（5 个城市 × 7 种周期）
- **输出**：全局最优方案 + Top 10 备选方案

**算法复杂度**：站点分组 $O(B_n)$（贝尔数，6 站点约 203 种分组）；全局搜索 $O(7^5 \times 5 \times B_6) \approx 340$ 万次计算，现代计算机秒级完成。

## 数据说明

### 城市参数

| 城市 | CDC距离 | 仓租(元/㎡/天) | 站点数 | 日均总需求(pcs) | 特征 |
| --- | --- | --- | --- | --- | --- |
| A | 40km | 5.0 | 6 | 405,000 | 近郊，寸土寸金 |
| B | 70km | 4.0 | 5 | 250,000 | 商务区，租金较高 |
| C | 100km | 3.0 | 5 | 200,000 | 正常区域 |
| D | 140km | 2.0 | 5 | 125,000 | 远郊 |
| E | 180km | 1.5 | 4 | 57,000 | 偏远，地价极低 |

### 车辆参数

| 车型 | 满载量 | 固定成本 | 变动成本 |
| --- | --- | --- | --- |
| 小车 | 80,000 pcs | 300 元/次 | 4.0 元/km |
| 大车 | 200,000 pcs | 600 元/次 | 6.5 元/km |

### 约束条件

- 单车最多串 3 个站点
- 严禁跨城串点
- 订货周期 T 必须是整数 1~7 天
- 同一城市所有站点必须相同 T
- 车辆必须返回主城

## 生成图表

| 图表 | 说明 | 生成脚本 |
| --- | --- | --- |
| Fig 1 | 物流网络拓扑与最优配置 | `scripts/fig1.py` |
| Fig 2 | 各城市最优日成本分解 | `scripts/fig2.py` |
| Fig 3 | 五城市 T 敏感性分析 (2×3) | `scripts/fig3.py` |
| Fig 4 | 全局 Top-10 与 uniform-T 对比 | `scripts/fig4.py` |
| Fig 1+2 | 组合图（论文双栏排版） | `scripts/combine_fig1_fig2.py` |

## 学术论文

| 版本 | 文件 |
| --- | --- |
| 英文版 | [report/main.pdf](report/main.pdf) |

论文包含数学模型、算法伪代码、敏感性分析及管理启示，LaTeX 源文件见 `report/main.tex`。

## 输出文件

运行 `python main.py` 后生成到 `output/` 目录：

| 文件 | 说明 |
| --- | --- |
| `optimal_solution_*.json` | 最优解详细信息（JSON 格式） |
| `top_solutions_*.json` | Top 10 方案列表 |
| `optimization_report_*.txt` | 文本格式优化报告（含详细车辆调度） |

## 依赖

- Python 3.10+
- [requirements.txt](requirements.txt)：numpy、matplotlib
- LaTeX 编译环境（MacTeX / TeX Live，可选，仅编译论文时需要）

## License

[MIT](LICENSE)
