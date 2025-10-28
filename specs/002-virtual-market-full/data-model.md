# Data Model Design: A股虚拟市场

**Date**: 2025-10-28
**Purpose**: 定义虚拟市场系统的数据模型，包括数据库表结构、实体关系和验证规则

## Entity Relationship Overview

```
┌─────────────┐
│ MarketState │  (1)  全局市场状态（牛/熊/横盘）
└─────────────┘
       │
       │ influences (影响)
       ▼
┌─────────────┐      ┌──────────────┐
│   Sector    │◄────►│    Stock     │  (多对一) 板块包含多只股票
└─────────────┘      └──────────────┘
       │                    │
       │                    │ has metadata (1:1)
       ▼                    ▼
 ┌──────────────┐    ┌──────────────────┐
 │ SectorIndex  │    │ StockMetadata    │
 │ (行业指数)   │    │ (股票元数据)     │
 └──────────────┘    └──────────────────┘
                            │
                            │ belongs to (多对多)
                            ▼
                     ┌──────────────┐
                     │    Index     │  (指数)
                     └──────────────┘
                            │
                            │ has constituents (1:多)
                            ▼
                     ┌────────────────────┐
                     │ IndexConstituent   │  (成分股关系)
                     └────────────────────┘

      ┌──────────────┐
      │  PriceData   │  (价格数据：股票和指数都有)
      └──────────────┘
             │
             │ belongs to
             ▼
   ┌─────────────────┐
   │ Stock 或 Index  │
   └─────────────────┘
```

## Core Entities

### 1. Stock (股票)

**描述**: 虚拟股票的基本信息和当前状态

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| symbol | VARCHAR(10) | PK, NOT NULL, UNIQUE | 股票代码（6位数字，如600001） |
| name | VARCHAR(50) | NOT NULL | 股票名称（如"国民银行"） |
| sector_code | VARCHAR(20) | FK → Sector, NOT NULL | 所属板块代码 |
| current_price | NUMERIC(10, 2) | NOT NULL | 当前价格（元） |
| previous_close | NUMERIC(10, 2) | NOT NULL | 昨日收盘价 |
| change_value | NUMERIC(10, 2) | | 涨跌额（current_price - previous_close） |
| change_pct | NUMERIC(6, 3) | | 涨跌幅百分比 |
| volume | BIGINT | DEFAULT 0 | 成交量（股） |
| turnover | NUMERIC(18, 2) | DEFAULT 0 | 成交额（元） |
| is_active | BOOLEAN | DEFAULT TRUE | 是否活跃（用于停牌等） |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 最后更新时间 |

**索引**:
- PRIMARY KEY: `symbol`
- INDEX: `sector_code`
- INDEX: `current_price` (用于市值排序)

**验证规则**:
- `symbol` 必须是6位数字
- `current_price` > 0
- `change_pct` 必须在 [-10, 10] 范围内（涨跌停限制）

---

### 2. StockMetadata (股票元数据)

**描述**: 股票的静态属性，用于价格生成和分类

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| symbol | VARCHAR(10) | PK, FK → Stock, NOT NULL | 股票代码 |
| market_cap | BIGINT | NOT NULL | 总市值（亿元） |
| market_cap_tier | VARCHAR(20) | NOT NULL | 市值等级（超大盘/大盘/中盘/小盘/微盘） |
| beta | NUMERIC(4, 2) | NOT NULL, DEFAULT 1.0 | Beta系数（相对大盘波动率） |
| volatility | NUMERIC(6, 4) | NOT NULL | 年化波动率（如0.25表示25%） |
| outstanding_shares | BIGINT | NOT NULL | 流通股本（亿股） |
| listing_date | DATE | DEFAULT '2024-01-01' | 上市日期 |
| is_happy300 | BOOLEAN | DEFAULT FALSE | 是否是HAPPY300成分股 |
| weight_in_happy300 | NUMERIC(6, 4) | | 在HAPPY300中的权重（如0.0850） |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `symbol`
- INDEX: `market_cap` DESC (用于指数成分股选择)
- INDEX: `is_happy300`

**验证规则**:
- `beta` 范围: [0.5, 2.0]
- `volatility` 范围: [0.01, 1.0] （1%-100%）
- `market_cap_tier` 枚举: ['超大盘', '大盘', '中盘', '小盘', '微盘']
- 如果`is_happy300=TRUE`，则`weight_in_happy300`必须有值

---

### 3. Sector (板块)

**描述**: 行业板块信息

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| code | VARCHAR(20) | PK, NOT NULL | 板块代码（如TECH, FIN） |
| name | VARCHAR(50) | NOT NULL | 板块名称（如"科技板块"） |
| name_en | VARCHAR(50) | | 英文名称（如Technology） |
| beta | NUMERIC(4, 2) | NOT NULL | 板块Beta系数 |
| total_market_cap | BIGINT | | 板块总市值（亿元） |
| stock_count | INTEGER | DEFAULT 0 | 板块内股票数量 |
| avg_change_pct | NUMERIC(6, 3) | | 板块平均涨跌幅 |
| description | TEXT | | 板块描述 |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `code`

**预定义数据** (10大板块):
```sql
INSERT INTO sectors (code, name, name_en, beta) VALUES
('TECH', '科技板块', 'Technology', 1.25),
('FIN', '金融板块', 'Finance', 0.75),
('CONS', '消费板块', 'Consumer', 0.85),
('NEV', '新能源板块', 'NewEnergy', 1.40),
('HEALTH', '医药板块', 'Healthcare', 0.90),
('IND', '工业板块', 'Industry', 1.05),
('REAL', '地产板块', 'RealEstate', 1.15),
('ENERGY', '能源板块', 'Energy', 0.95),
('MATER', '材料板块', 'Materials', 1.10),
('UTIL', '公用事业板块', 'Utilities', 0.65);
```

---

### 4. Index (指数)

**描述**: 市场指数（包括核心指数和行业指数）

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| code | VARCHAR(20) | PK, NOT NULL | 指数代码（HAPPY300, HAPPY50, GROW100） |
| name | VARCHAR(50) | NOT NULL | 指数名称（如"快乐综合指数"） |
| index_type | VARCHAR(20) | NOT NULL | 指数类型（CORE核心/SECTOR行业） |
| base_point | NUMERIC(10, 2) | NOT NULL | 基点（如3000） |
| base_date | DATE | DEFAULT '2024-01-01' | 基期日期 |
| current_value | NUMERIC(10, 2) | NOT NULL | 当前点位 |
| previous_close | NUMERIC(10, 2) | NOT NULL | 昨日收盘 |
| change_value | NUMERIC(10, 2) | | 涨跌点数 |
| change_pct | NUMERIC(6, 3) | | 涨跌幅 |
| volume | BIGINT | | 成交量（亿股） |
| turnover | BIGINT | | 成交额（亿元） |
| constituent_count | INTEGER | DEFAULT 0 | 成分股数量 |
| calculation_method | VARCHAR(50) | DEFAULT 'FREE_FLOAT_MKT_CAP' | 计算方法 |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `code`
- INDEX: `index_type`

**预定义数据** (13个指数):
```sql
INSERT INTO indices (code, name, index_type, base_point, constituent_count) VALUES
-- 核心指数
('HAPPY300', '快乐综合指数', 'CORE', 3000, 100),
('HAPPY50', '快乐50指数', 'CORE', 2500, 50),
('GROW100', '创新成长指数', 'CORE', 2000, 50),
-- 行业指数
('TECH_IDX', '科技指数', 'SECTOR', 1000, 20),
('FIN_IDX', '金融指数', 'SECTOR', 1000, 12),
('CONS_IDX', '消费指数', 'SECTOR', 1000, 15),
('NEV_IDX', '新能源指数', 'SECTOR', 1000, 10),
('HEALTH_IDX', '医药健康指数', 'SECTOR', 1000, 12),
('IND_IDX', '工业指数', 'SECTOR', 1000, 10),
('REAL_IDX', '地产指数', 'SECTOR', 1000, 8),
('ENERGY_IDX', '能源指数', 'SECTOR', 1000, 8),
('MATER_IDX', '材料指数', 'SECTOR', 1000, 6),
('UTIL_IDX', '公用事业指数', 'SECTOR', 1000, 5);
```

---

### 5. IndexConstituent (指数成分股)

**描述**: 股票与指数的关联关系及权重

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | SERIAL | PK | 自增ID |
| index_code | VARCHAR(20) | FK → Index, NOT NULL | 指数代码 |
| stock_symbol | VARCHAR(10) | FK → Stock, NOT NULL | 股票代码 |
| weight | NUMERIC(6, 4) | NOT NULL | 权重（0-1之间，如0.0850表示8.5%） |
| rank | INTEGER | | 排名（按权重降序） |
| join_date | DATE | DEFAULT NOW() | 纳入日期 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否有效（用于成分股调整） |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(index_code, stock_symbol)`
- INDEX: `index_code`
- INDEX: `stock_symbol`
- INDEX: `weight` DESC

**约束**:
- UNIQUE(`index_code`, `stock_symbol`) - 同一只股票在同一指数中只能出现一次
- `weight` 范围: [0.0001, 0.1000] （0.01%-10%）
- 同一`index_code`的所有`weight`之和应为1.0

---

### 6. PriceData (价格数据)

**描述**: 股票和指数的历史价格K线数据

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGSERIAL | PK | 自增ID |
| target_type | VARCHAR(10) | NOT NULL | 目标类型（STOCK/INDEX） |
| target_code | VARCHAR(20) | NOT NULL | 股票代码或指数代码 |
| timestamp | BIGINT | NOT NULL | Unix时间戳（秒） |
| datetime | TIMESTAMP | NOT NULL | 日期时间（便于查询） |
| open | NUMERIC(10, 2) | NOT NULL | 开盘价/点位 |
| close | NUMERIC(10, 2) | NOT NULL | 收盘价/点位 |
| high | NUMERIC(10, 2) | NOT NULL | 最高价/点位 |
| low | NUMERIC(10, 2) | NOT NULL | 最低价/点位 |
| volume | BIGINT | DEFAULT 0 | 成交量 |
| turnover | NUMERIC(18, 2) | DEFAULT 0 | 成交额 |
| change_pct | NUMERIC(6, 3) | | 涨跌幅 |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `(target_type, target_code, timestamp)` - 防止重复数据
- INDEX: `target_code, datetime` DESC - 用于按时间查询某股票/指数历史
- INDEX: `datetime` - 用于查询某时刻所有数据

**验证规则**:
- `low` ≤ `open`, `close` ≤ `high`
- `high` ≥ `open`, `close` ≥ `low`
- `target_type` 枚举: ['STOCK', 'INDEX']

**数据量估算**:
- 每只股票/指数每分钟1条 × 106股票+13指数 × 1440分钟/天 × 90天 ≈ **1550万条**
- 建议定期归档：将90天前的分钟数据聚合为日K线，减少存储压力

---

### 7. MarketState (市场状态)

**描述**: 全局市场状态（牛市/熊市/横盘），影响所有股票价格生成

**字段**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | SERIAL | PK | 自增ID |
| state | VARCHAR(20) | NOT NULL | 市场状态（BULL牛市/BEAR熊市/SIDEWAYS横盘） |
| start_time | TIMESTAMP | NOT NULL | 状态开始时间 |
| end_time | TIMESTAMP | | 预计结束时间（NULL表示当前状态） |
| daily_trend | NUMERIC(6, 4) | NOT NULL | 日均趋势（如0.005表示日均+0.5%） |
| volatility_multiplier | NUMERIC(4, 2) | DEFAULT 1.0 | 波动率乘数（如1.5表示比正常波动大50%） |
| description | TEXT | | 状态描述（如"科技股领涨的牛市"） |
| is_current | BOOLEAN | DEFAULT FALSE | 是否是当前状态 |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `is_current`
- INDEX: `start_time` DESC

**约束**:
- 同一时刻只能有一个`is_current=TRUE`的记录
- `state` 枚举: ['BULL', 'BEAR', 'SIDEWAYS']
- `daily_trend` 范围: [-0.05, 0.05] （-5%到+5%）

**状态转换规则**:
- 牛市(BULL): `daily_trend` > 0.002 （日均+0.2%以上）
- 熊市(BEAR): `daily_trend` < -0.002 （日均-0.2%以下）
- 横盘(SIDEWAYS): `daily_trend` 在 [-0.002, 0.002] 之间
- 状态持续时间: 至少7天

---

## Relationship Summary

**一对多 (1:N)**:
- `Sector` → `Stock`: 一个板块包含多只股票
- `Index` → `IndexConstituent`: 一个指数有多个成分股
- `Stock` → `PriceData`: 一只股票有多条历史价格
- `Index` → `PriceData`: 一个指数有多条历史点位

**多对多 (N:M)**:
- `Stock` ↔ `Index` (通过`IndexConstituent`): 一只股票可属于多个指数，一个指数包含多只股票

**一对一 (1:1)**:
- `Stock` ↔ `StockMetadata`: 每只股票有唯一的元数据记录

**全局影响**:
- `MarketState`: 影响所有股票和板块的价格生成

## Data Consistency Rules

### 1. 指数成分股权重和
对于每个指数，其所有成分股的权重之和必须等于1.0（误差 < 0.0001）

```sql
-- 验证查询
SELECT index_code, SUM(weight) as total_weight
FROM index_constituents
WHERE is_active = TRUE
GROUP BY index_code
HAVING ABS(SUM(weight) - 1.0) > 0.0001;
-- 应返回0行
```

### 2. 价格数据时序一致性
K线数据的high、low必须包含open和close

```sql
-- 验证查询
SELECT id FROM price_data
WHERE low > LEAST(open, close)
   OR high < GREATEST(open, close);
-- 应返回0行
```

### 3. 涨跌停限制
股票当日涨跌幅不得超过±10%

```sql
-- 验证查询
SELECT symbol, change_pct FROM stocks
WHERE ABS(change_pct) > 10.0;
-- 应返回0行（除非有特殊情况）
```

### 4. 指数与成分股同步
指数的`current_value`更新时，必须基于当前成分股的最新价格计算

```sql
-- 检查指数更新时间是否晚于成分股
SELECT i.code, i.updated_at as index_time, MAX(s.updated_at) as max_stock_time
FROM indices i
JOIN index_constituents ic ON i.code = ic.index_code
JOIN stocks s ON ic.stock_symbol = s.symbol
GROUP BY i.code, i.updated_at
HAVING MAX(s.updated_at) > i.updated_at;
-- 如果返回行，说明指数计算滞后
```

## Migration Strategy

由于这是新功能，所有表都将在`sql_scripts/init_virtual_market.sql`中创建。

**建议的执行顺序**:
1. 创建基础表（无外键）：`sectors`, `market_states`
2. 创建核心表：`stocks`, `indices`
3. 创建元数据表：`stock_metadata` (外键指向`stocks`)
4. 创建关系表：`index_constituents` (外键指向`stocks`和`indices`)
5. 创建价格表：`price_data` (最大的表，最后创建)
6. 插入初始数据：106只股票、10个板块、13个指数、成分股关系
7. 生成历史数据：运行`backend/lib/data_initializer.py`生成90天历史K线

## Indexes and Performance

**关键索引**（已在各实体中标注）:
- `price_data(target_code, datetime)`: 查询单只股票历史数据
- `stock_metadata(market_cap)`: 按市值排序选择指数成分股
- `index_constituents(index_code, weight)`: 计算指数时按权重遍历

**查询优化建议**:
- 时间范围查询使用`datetime`字段而非`timestamp`（PostgreSQL对TIMESTAMP优化更好）
- 大数据量查询（如90天历史）考虑分页或限制返回字段
- 实时价格查询优先从Redis缓存读取，减少数据库压力

## Next Steps

- [x] Phase 0: 技术研究（research.md）
- [x] Phase 1: 数据模型设计（本文件）
- [ ] Phase 1: API契约定义（contracts/）
- [ ] Phase 1: 快速开始指南（quickstart.md）
