# A股风格虚拟市场设计方案

## 一、板块体系设计

### 1.1 主板块分类（参考申万一级行业）

| 板块代码 | 板块名称 | 股票数量 | 特征 | 平均波动率 |
|---------|---------|---------|------|-----------|
| **Technology** | 科技板块 | 15-20只 | 高成长、高波动 | 3.5% |
| **Finance** | 金融板块 | 10-12只 | 低波动、蓝筹 | 1.8% |
| **Consumer** | 消费板块 | 12-15只 | 稳健成长 | 2.5% |
| **Industry** | 工业板块 | 10-12只 | 周期性 | 2.8% |
| **Healthcare** | 医药板块 | 10-12只 | 防御性 | 2.2% |
| **RealEstate** | 地产板块 | 8-10只 | 政策敏感 | 3.0% |
| **Energy** | 能源板块 | 8-10只 | 周期性强 | 3.2% |
| **Materials** | 材料板块 | 6-8只 | 周期性 | 2.9% |
| **Utilities** | 公用事业 | 5-6只 | 低波动 | 1.5% |
| **Telecom** | 通信板块 | 4-5只 | 稳定 | 2.0% |

**合计**：约80-100只虚拟股票

### 1.2 市值分类（参考A股市值分布）

| 类别 | 市值范围 | 占比 | 特征 | 代码前缀 |
|-----|---------|-----|------|---------|
| **超大盘股** | >5000亿 | 10% | 蓝筹、权重股 | HS (沪深) |
| **大盘股** | 1000-5000亿 | 20% | 稳健 | HS |
| **中盘股** | 300-1000亿 | 35% | 成长 | SZ (深圳) |
| **小盘股** | 100-300亿 | 25% | 高成长 | SZ |
| **微盘股** | <100亿 | 10% | 高风险 | CY (创业板) |

---

## 二、虚拟指数体系设计

### 2.1 核心指数

#### **快乐综合指数（HAPPY300）**
- **定位**：对标沪深300
- **样本股**：市值最大的300只虚拟股票
- **加权方式**：自由流通市值加权
- **基点**：3000点（初始值）
- **代码**：HAPPY300 或 HS300

#### **快乐50指数（HAPPY50）**
- **定位**：对标上证50
- **样本股**：超大盘蓝筹股50只
- **特征**：低波动、高分红
- **基点**：2500点

#### **创新成长指数（GROW100）**
- **定位**：对标创业板指
- **样本股**：科技、新能源等成长股100只
- **特征**：高成长、高波动
- **基点**：2000点

### 2.2 行业指数

| 指数名称 | 代码 | 样本股 | 用途 |
|---------|------|--------|------|
| 科技指数 | TECH | 科技板块全部 | 板块轮动 |
| 金融指数 | FIN | 金融板块全部 | 经济晴雨表 |
| 消费指数 | CONS | 消费板块全部 | 内需指标 |
| 新能源指数 | NEV | 新能源相关 | 主题投资 |

---

## 三、股票命名规则（A股风格）

### 3.1 命名体系

**格式**：`代码(6位) + 名称`

**代码规则**（参考真实A股）：
- `600xxx`：沪市主板（大盘蓝筹）
- `601xxx`：沪市主板（大型国企）
- `603xxx`：沪市主板（民营企业）
- `000xxx`：深市主板
- `002xxx`：深市中小板
- `300xxx`：创业板

**示例**：
```
600001  快乐银行        （对标：601398 工商银行）
600028  国家电网        （对标：600900 长江电力）
600519  贵州快乐        （对标：600519 贵州茅台）
601888  中国云计算      （对标：601888 中国中免）
000001  深圳科技        （对标：000001 平安银行）
002415  芯片制造        （对标：002415 海康威视）
300059  新能源汽车      （对标：300059 东方财富）
```

### 3.2 完整股票清单（80只示例）

#### 金融板块（12只）
```
代码      名称             市值(亿)  价格   波动率
600001   快乐银行          8000     15.00   1.5%   (权重股)
601398   国民银行          12000    6.50    1.4%   (超级权重)
601328   交通银行          4500     8.20    1.6%
601166   城市银行          3200     9.80    1.7%
600036   招商银行          9000     42.00   1.8%
601318   平安保险          15000    58.00   2.0%
600030   中信证券          3800     25.00   2.5%
601688   华泰证券          2500     18.50   2.6%
601066   中信建设          2100     12.30   2.3%
600999   招商证券          1800     16.80   2.7%
601998   中信银行          3500     5.60    1.6%
600016   民生银行          4200     4.80    1.9%
```

#### 科技板块（20只）
```
代码      名称             市值(亿)  价格   波动率
600519   云端计算          5000     180.00  3.0%   (科技龙头)
688001   半导体芯片        3500     120.00  4.2%
688012   人工智能          2800     95.00   4.5%
300059   互联网科技        4200     68.00   3.8%
300750   智能硬件          1500     52.00   4.0%
002415   视频监控          3000     48.00   3.5%
002230   通信设备          1800     38.00   3.6%
300033   云存储            1200     45.00   4.2%
603986   软件开发          980      32.00   3.9%
688111   量子计算          650      88.00   5.5%   (概念股)
688188   光刻机            520      220.00  6.0%   (高科技)
300456   大数据            1100     28.00   4.1%
002049   紫光芯片          2200     42.00   4.3%
603160   电子元件          880      25.00   3.7%
300661   5G通信            1350     38.00   4.0%
002371   北方华创          1800     78.00   4.8%
688008   集成电路          980      56.00   5.2%
300142   物联网            720      18.50   4.4%
688036   工业软件          560      42.00   4.6%
300308   网络安全          890      28.00   4.2%
```

#### 消费板块（15只）
```
代码      名称             市值(亿)  价格   波动率
600519   贵州快乐          22000    1680.00 2.0%   (茅台对标)
000858   五粮液            5800     168.00  2.2%
600887   伊利乳业          3200     38.00   2.3%
000333   美的电器          5500     72.00   2.5%
000651   格力电器          3800     35.00   2.6%
603288   海天调味          4200     88.00   2.4%
002304   洋河酒业          1800     128.00  2.8%
600779   全聚德            420      12.00   3.2%
002507   连锁超市          680      18.50   2.9%
600600   青岛啤酒          980      78.00   2.5%
603369   今世缘            520      48.00   2.7%
002572   家居家电          1200     52.00   3.0%
600809   快乐服饰          850      22.00   3.3%
603589   食品饮料          680      35.00   2.8%
300999   快乐餐饮          420      28.00   3.5%
```

#### 新能源板块（12只）
```
代码      名称             市值(亿)  价格   波动率
300750   新能源汽车        8000     245.00  4.5%   (龙头)
002594   动力电池          4500     180.00  4.8%
601012   光伏科技          3200     85.00   4.2%
600438   风力发电          1800     28.00   3.8%
300274   储能技术          2100     95.00   5.0%
688599   锂电材料          1500     120.00  5.2%
002129   充电桩            980      42.00   4.6%
300014   氢能源            720      35.00   5.5%
601865   太阳能            1200     18.50   4.0%
300763   电池回收          560      28.00   4.9%
688303   钠电池            380      68.00   6.0%
603501   新能源车企        2500     158.00  4.7%
```

#### 工业板块（10只）
```
代码      名称             市值(亿)  价格   波动率
601668   中国建筑          4500     6.80    2.5%
600585   机械制造          2200     28.00   3.0%
601766   航空航天          1800     35.00   3.2%
600031   重工集团          3200     12.50   2.8%
600150   船舶制造          1500     18.00   3.4%
002202   工程机械          980      22.00   3.1%
601919   高铁装备          2800     8.50    2.6%
603766   电气设备          720      42.00   3.3%
600875   化工材料          1200     25.00   3.5%
002459   通用机械          680      15.50   3.2%
```

#### 医药板块（11只）
```
代码      名称             市值(亿)  价格   波动率
600276   生物医药          3800     88.00   2.5%
000661   长春制药          2200     45.00   2.8%
002007   华东医药          1500     32.00   2.6%
300015   创新药            2800     68.00   3.2%
603259   医疗器械          1200     58.00   2.9%
688180   基因测序          680      95.00   4.0%
300529   中药制造          980      28.00   2.7%
600521   疫苗研发          1800     78.00   3.5%
002773   医疗服务          720      42.00   3.0%
688396   细胞治疗          450      120.00  4.8%
603392   保健品            580      25.00   2.8%
```

---

## 四、指数计算方法

### 4.1 HAPPY300指数计算公式

#### 市值加权法（参考沪深300）

```python
# 指数计算公式
指数 = (当前总市值 / 基期总市值) × 基点

# 详细公式
HAPPY300 = Σ(股价i × 流通股本i × 权重因子i) / 除数 × 1000
```

#### 权重因子计算

```python
# 单只股票权重上限：10%（防止过度集中）
权重因子 = min(自由流通市值 / 总自由流通市值, 0.10)

# 示例：
# 601318 平安保险：市值15000亿，占比12% → 限制到10%
# 600519 贵州快乐：市值22000亿，占比15% → 限制到10%
# 其他股票：按实际市值比例
```

### 4.2 指数成分股权重分布（HAPPY300示例）

| 档位 | 单股权重 | 股票数 | 合计权重 | 代表股票 |
|------|---------|--------|---------|---------|
| 超大权重 | 5-10% | 5只 | 40% | 平安、茅台、工行、新能源汽车 |
| 大权重 | 2-5% | 15只 | 45% | 招商银行、美的、五粮液 |
| 中权重 | 0.5-2% | 80只 | 15% | 各行业龙头 |
| 小权重 | <0.5% | 200只 | - | 不纳入HAPPY300 |

### 4.3 指数计算实现

```python
# backend/lib/index_calculator.py

class IndexCalculator:
    """虚拟指数计算器"""

    def __init__(self, db_manager):
        self.db = db_manager
        # 基期设置：2024-01-01 的市值作为基期
        self.base_date = datetime(2024, 1, 1)
        self.base_point = 3000  # HAPPY300 基点

    def calculate_happy300(self, timestamp: int) -> float:
        """
        计算 HAPPY300 指数

        Args:
            timestamp: 当前时间戳

        Returns:
            指数点位
        """
        # 1. 获取成分股列表（市值前300）
        constituents = self.get_top_stocks_by_market_cap(limit=300)

        # 2. 获取成分股当前价格
        current_market_cap = 0
        for stock in constituents:
            price = self.get_stock_price(stock.symbol, timestamp)
            shares = stock.outstanding_shares  # 流通股本
            market_cap = price * shares

            # 应用权重上限
            weight = min(market_cap / total_market_cap, 0.10)
            current_market_cap += market_cap * weight

        # 3. 获取基期市值
        base_market_cap = self.get_base_market_cap(constituents)

        # 4. 计算指数
        index_value = (current_market_cap / base_market_cap) * self.base_point

        return round(index_value, 2)

    def calculate_index_change(self, current: float, previous: float) -> dict:
        """计算指数涨跌"""
        change = current - previous
        change_pct = (change / previous) * 100

        return {
            'current': current,
            'change': round(change, 2),
            'change_pct': round(change_pct, 2)
        }
```

---

## 五、市场联动机制

### 5.1 指数与个股联动

```python
# 个股价格生成时考虑大盘影响

def generate_stock_price_with_market(stock, market_trend):
    """
    生成股票价格（考虑大盘影响）

    Args:
        stock: 股票对象
        market_trend: 大盘趋势（-0.03 到 +0.03）

    Returns:
        新价格
    """
    # 1. 个股自身的GBM生成（70%权重）
    individual_change = gbm_generate(stock)

    # 2. 大盘影响（30%权重）
    market_influence = market_trend * stock.beta * 0.3

    # 3. 行业影响（可选，暂不实现）
    # sector_influence = get_sector_trend(stock.sector) * 0.1

    # 4. 综合计算
    total_change = individual_change * 0.7 + market_influence

    new_price = stock.current_price * (1 + total_change)

    return new_price
```

### 5.2 Beta系数设置

| 股票类型 | Beta值 | 含义 | 示例 |
|---------|--------|------|------|
| 超级蓝筹 | 0.6-0.8 | 抗跌、跟随性弱 | 银行、公用事业 |
| 普通蓝筹 | 0.8-1.0 | 跟随大盘 | 消费、医药 |
| 成长股 | 1.0-1.3 | 大盘涨它涨更多 | 科技、新能源 |
| 小盘股 | 1.3-1.8 | 高弹性 | 创业板、概念股 |

```sql
-- 在 stock_metadata 表添加 beta 字段
ALTER TABLE stock_metadata ADD COLUMN beta NUMERIC(4, 2) DEFAULT 1.0;

-- 更新示例
UPDATE stock_metadata SET beta = 0.7 WHERE sector = 'Finance';
UPDATE stock_metadata SET beta = 1.2 WHERE sector = 'Technology';
UPDATE stock_metadata SET beta = 1.5 WHERE symbol LIKE '300%';
```

### 5.3 市场状态同步

```python
# 全市场统一的市场状态（牛市/熊市/横盘）

class MarketStateManager:
    """全市场状态管理器"""

    def __init__(self):
        self.global_state = MarketState.SIDEWAYS
        self.state_duration = 0

    def update_global_state(self):
        """更新全局市场状态"""
        # 每个交易日开盘时，10%概率切换市场状态
        if random() < 0.10:
            self.global_state = self.transition_state(self.global_state)
            logger.info(f"市场状态切换为: {self.global_state.value}")

    def get_market_trend(self) -> float:
        """获取当前市场趋势强度"""
        trends = {
            MarketState.BULL: +0.02,    # 牛市：日均涨0.2%
            MarketState.BEAR: -0.02,    # 熊市：日均跌0.2%
            MarketState.SIDEWAYS: 0.0,  # 横盘：无趋势
        }
        return trends[self.global_state]
```

---

## 六、数据库表结构扩展

### 6.1 新增表：市场指数

```sql
-- 市场指数表
CREATE TABLE market_indices (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL,     -- HAPPY300, HAPPY50
    index_name VARCHAR(50) NOT NULL,     -- 快乐综合指数
    time BIGINT NOT NULL,                 -- 时间戳
    value NUMERIC(10, 2) NOT NULL,       -- 指数点位
    change_value NUMERIC(10, 2),         -- 涨跌点数
    change_pct NUMERIC(6, 3),            -- 涨跌幅
    volume BIGINT,                        -- 成交量（亿股）
    amount BIGINT,                        -- 成交额（亿元）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(index_code, time)
);

-- 索引
CREATE INDEX idx_indices_code_time ON market_indices (index_code, time DESC);

-- 初始化指数
INSERT INTO market_indices (index_code, index_name, time, value, change_value, change_pct)
VALUES
    ('HAPPY300', '快乐综合指数', extract(epoch from now())::bigint, 3000.00, 0, 0),
    ('HAPPY50', '快乐50指数', extract(epoch from now())::bigint, 2500.00, 0, 0),
    ('GROW100', '创新成长指数', extract(epoch from now())::bigint, 2000.00, 0, 0);
```

### 6.2 扩展表：股票元数据

```sql
-- 扩展 stock_metadata 表
ALTER TABLE stock_metadata
ADD COLUMN IF NOT EXISTS outstanding_shares BIGINT DEFAULT 1000000000,  -- 流通股本（10亿股）
ADD COLUMN IF NOT EXISTS market_cap BIGINT,                             -- 总市值（亿元）
ADD COLUMN IF NOT EXISTS beta NUMERIC(4, 2) DEFAULT 1.0,               -- Beta系数
ADD COLUMN IF NOT EXISTS weight_in_index NUMERIC(6, 4),                -- 在指数中的权重
ADD COLUMN IF NOT EXISTS is_index_constituent BOOLEAN DEFAULT FALSE,   -- 是否是成分股
ADD COLUMN IF NOT EXISTS listing_date DATE,                            -- 上市日期
ADD COLUMN IF NOT EXISTS stock_type VARCHAR(20) DEFAULT 'A股';         -- 股票类型

-- 添加注释
COMMENT ON COLUMN stock_metadata.outstanding_shares IS '流通股本（股）';
COMMENT ON COLUMN stock_metadata.market_cap IS '总市值（亿元）';
COMMENT ON COLUMN stock_metadata.beta IS 'Beta系数，衡量与大盘相关性';
COMMENT ON COLUMN stock_metadata.weight_in_index IS '在HAPPY300中的权重';
```

### 6.3 新增表：指数成分股

```sql
-- 指数成分股关系表
CREATE TABLE index_constituents (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL,      -- HAPPY300
    stock_symbol VARCHAR(20) NOT NULL,    -- 600001
    weight NUMERIC(6, 4) NOT NULL,        -- 权重 0.0850 表示8.5%
    rank INTEGER,                          -- 在指数中的排名
    join_date DATE,                        -- 纳入日期
    is_active BOOLEAN DEFAULT TRUE,       -- 是否仍在指数中
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(index_code, stock_symbol)
);

-- 索引
CREATE INDEX idx_constituents_index ON index_constituents (index_code);
CREATE INDEX idx_constituents_stock ON index_constituents (stock_symbol);
```

---

## 七、实施步骤

### Phase 1: 股票数据准备（1-2天）

1. **设计完整股票清单**（80只）
   - 按板块分配数量
   - 设置合理价格区间
   - 配置波动率和Beta

2. **编写初始化SQL**
   ```sql
   -- sql_scripts/init_a_stock_market.sql
   -- 包含80只股票的INSERT语句
   ```

3. **生成历史数据**
   ```bash
   python init_historical_data.py --days 90 --market-style a-stock
   ```

### Phase 2: 指数计算实现（2-3天）

1. **实现指数计算器**
   - `backend/lib/index_calculator.py`
   - 实现市值加权算法
   - 实现成分股选择逻辑

2. **集成到数据生成器**
   - 每分钟生成股票数据后，计算指数
   - 同时写入 `market_indices` 表

3. **测试指数准确性**
   - 验证权重和为1
   - 验证涨跌逻辑正确

### Phase 3: 市场联动机制（2-3天）

1. **实现全局市场状态**
   - `MarketStateManager` 类
   - 统一控制牛熊转换

2. **修改价格生成算法**
   - 添加大盘影响因子
   - 添加Beta系数应用

3. **测试联动效果**
   - 验证大盘涨时，大部分股票跟涨
   - 验证Beta高的股票弹性更大

### Phase 4: 前端展示（3-4天）

1. **指数看板**
   - 显示HAPPY300、HAPPY50实时点位
   - K线图展示指数走势

2. **板块热力图**
   - 显示各板块涨跌
   - 颜色深浅表示涨跌幅

3. **个股页面增强**
   - 显示所属板块
   - 显示在指数中的权重
   - 显示Beta系数

---

## 八、预期效果

### 8.1 真实感提升

✅ **A股特色**：
- 6位数字代码（600xxx, 000xxx, 300xxx）
- 中文股票名称
- 真实的行业板块分类
- 符合A股的价格区间和波动特征

✅ **市场联动**：
- 大盘涨，多数股票跟涨
- 牛市来临，板块轮动
- 熊市时，普遍下跌

✅ **专业性**：
- 指数作为市场风向标
- Beta系数体现风险特征
- 市值加权符合真实逻辑

### 8.2 教育价值

📚 **用户可以学习**：
- 指数成分股的概念
- 大盘与个股的关系
- Beta系数的含义
- 板块轮动的规律
- 市值加权的原理

### 8.3 可扩展性

🚀 **未来可以添加**：
- 行业指数（科技指数、金融指数）
- 主题指数（新能源指数、芯片指数）
- 风格指数（大盘股指数、小盘股指数）
- 北向资金流入流出
- 融资融券数据
- 龙虎榜数据

---

## 九、技术实现要点

### 9.1 性能优化

```python
# 指数计算优化：使用缓存

@lru_cache(maxsize=1)
def get_index_constituents(index_code: str) -> List[str]:
    """获取指数成分股（带缓存）"""
    # 每小时更新一次即可，不需要每分钟查询
    pass

# 批量查询股票价格
def get_batch_stock_prices(symbols: List[str], timestamp: int) -> Dict[str, float]:
    """批量查询，减少数据库往返"""
    pass
```

### 9.2 数据一致性

```python
# 使用事务确保数据一致性

with db.get_session() as session:
    # 1. 生成所有股票的K线
    klines = generate_all_stocks_klines()
    session.bulk_insert_mappings(MarketKline, klines)

    # 2. 计算指数
    index_value = calculate_happy300(klines)

    # 3. 插入指数数据
    session.add(MarketIndex(
        index_code='HAPPY300',
        time=timestamp,
        value=index_value
    ))

    # 4. 提交事务（要么全成功，要么全失败）
    session.commit()
```

---

## 十、总结

这套A股风格虚拟市场设计方案具备：

✅ **高度真实**：
- 完整的板块体系
- 符合A股特征的代码命名
- 真实的指数编制方法
- 市场联动机制

✅ **教育价值**：
- 学习指数的概念
- 理解市场联动
- 掌握风险度量（Beta）

✅ **可扩展性**：
- 易于添加新股票
- 可以创建新指数
- 支持更多市场机制

✅ **零风险**：
- 完全虚拟，无法律问题
- 明确是模拟环境
- 可自由配置和调整

**下一步建议**：先实现核心的80只股票 + HAPPY300指数，验证联动效果后再扩展其他功能。

你觉得这个方案如何？需要调整哪些细节？
