# 系统总体设计

## 一、架构
前端（已有框架） → API（FastAPI） → 仿真引擎（SimV2） → 核心模块（Orderbook、Impact、Agents、Sentiment）

## 二、模块
core：价格引擎与撮合
agents：智能体建模
sim：时序驱动与回放
utils：参数管理与统计检验
api：对外接口层

## 三、核心算法
- 冲击函数 ΔP = α * (|Q| / L^β) * sign(Q)
- 惯性 ΔP_t = λ * ΔP_new + (1-λ) * ΔP_prev
- 情绪模型 E_t = (1-ζ)*E_(t-1)+η*ΔP_t

## 四、接口
| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /simulate/start | 启动仿真 |
| POST | /simulate/step | 推进 tick |
| POST | /player/order | 下单 |
| GET | /market/state | 市场状态 |
| GET | /replay/:id | 回放 |
