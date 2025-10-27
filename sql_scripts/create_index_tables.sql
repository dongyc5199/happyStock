-- ============================================================
-- 指数体系数据库表结构
-- ============================================================
-- 功能：支持市值加权指数计算和成分股管理
-- 包含：
--   - market_indices: 指数历史数据表
--   - index_constituents: 指数成分股关系表
--   - index_metadata: 指数元数据表
--   - sector_indices: 板块指数表
-- ============================================================

-- 1. 指数元数据表
CREATE TABLE IF NOT EXISTS index_metadata (
    index_code VARCHAR(20) PRIMARY KEY,
    index_name VARCHAR(50) NOT NULL,
    index_name_en VARCHAR(50),
    base_date DATE NOT NULL DEFAULT '2024-01-01',
    base_value NUMERIC(10, 2) NOT NULL DEFAULT 1000.00,
    divisor NUMERIC(20, 8),                        -- 除数（动态调整）
    index_type VARCHAR(20) NOT NULL,               -- market, sector, style
    weight_method VARCHAR(20) NOT NULL DEFAULT 'market_cap',  -- market_cap, equal
    weight_cap NUMERIC(4, 3) DEFAULT 0.100,       -- 单股权重上限（10%）
    constituent_count INTEGER NOT NULL,            -- 成分股数量
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入核心指数元数据
INSERT INTO index_metadata (index_code, index_name, index_name_en, base_date, base_value, index_type, weight_cap, constituent_count, description) VALUES
('HAPPY300', '快乐综合指数', 'HAPPY 300 Index', '2024-01-01', 3000.00, 'market', 0.100, 100, '市值最大、流动性最好的100只股票，反映市场整体走势'),
('HAPPY50', '快乐50指数', 'HAPPY 50 Index', '2024-01-01', 2500.00, 'market', 0.100, 50, '超大盘蓝筹股，低波动高分红'),
('GROW100', '创新成长指数', 'Growth 100 Index', '2024-01-01', 2000.00, 'style', 0.100, 50, '科技、新能源等高成长行业'),
('FIN', '金融指数', 'Financial Index', '2024-01-01', 1000.00, 'sector', 0.150, 12, '金融板块指数'),
('TECH', '科技指数', 'Technology Index', '2024-01-01', 1000.00, 'sector', 0.150, 20, '科技板块指数'),
('CONS', '消费指数', 'Consumer Index', '2024-01-01', 1000.00, 'sector', 0.150, 15, '消费板块指数'),
('NEV', '新能源指数', 'New Energy Index', '2024-01-01', 1000.00, 'sector', 0.150, 10, '新能源板块指数'),
('HEALTH', '医药健康指数', 'Healthcare Index', '2024-01-01', 1000.00, 'sector', 0.150, 12, '医药健康板块指数'),
('IND', '工业指数', 'Industrial Index', '2024-01-01', 1000.00, 'sector', 0.150, 10, '工业板块指数'),
('REAL', '地产指数', 'Real Estate Index', '2024-01-01', 1000.00, 'sector', 0.150, 8, '地产板块指数')
ON CONFLICT (index_code) DO UPDATE SET
    index_name = EXCLUDED.index_name,
    base_value = EXCLUDED.base_value,
    constituent_count = EXCLUDED.constituent_count,
    description = EXCLUDED.description;

-- 2. 市场指数历史数据表
CREATE TABLE IF NOT EXISTS market_indices (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL,
    index_name VARCHAR(50) NOT NULL,
    time BIGINT NOT NULL,                          -- 时间戳（秒）
    value NUMERIC(10, 2) NOT NULL,                -- 指数点位
    change_value NUMERIC(10, 2),                  -- 涨跌点数
    change_pct NUMERIC(6, 3),                     -- 涨跌幅(%)
    volume BIGINT,                                 -- 成交量（亿股）
    amount BIGINT,                                 -- 成交额（亿元）
    constituent_count INTEGER,                     -- 成分股数量
    up_count INTEGER,                              -- 上涨家数
    down_count INTEGER,                            -- 下跌家数
    flat_count INTEGER,                            -- 平盘家数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(index_code, time)
);

-- 创建索引
CREATE INDEX idx_indices_code_time ON market_indices (index_code, time DESC);
CREATE INDEX idx_indices_time ON market_indices (time DESC);

-- 分区（可选，提升性能）
-- 如果数据量大，可以按月分区
-- CREATE TABLE market_indices_2025_01 PARTITION OF market_indices
--     FOR VALUES FROM (1704067200) TO (1706745600);

-- 3. 指数成分股关系表
CREATE TABLE IF NOT EXISTS index_constituents (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL,              -- 指数代码
    stock_symbol VARCHAR(20) NOT NULL,            -- 股票代码
    weight NUMERIC(6, 4) NOT NULL,                -- 权重（0.0850 表示8.5%）
    rank INTEGER,                                  -- 在指数中的排名
    join_date DATE DEFAULT CURRENT_DATE,          -- 纳入日期
    exit_date DATE,                                -- 退出日期（NULL表示仍在）
    is_active BOOLEAN DEFAULT TRUE,               -- 是否仍在指数中
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(index_code, stock_symbol, join_date)
);

-- 创建索引
CREATE INDEX idx_constituents_index ON index_constituents (index_code);
CREATE INDEX idx_constituents_stock ON index_constituents (stock_symbol);
CREATE INDEX idx_constituents_active ON index_constituents (index_code, is_active);

-- 4. 板块指数表（存储板块整体表现）
CREATE TABLE IF NOT EXISTS sector_indices (
    id SERIAL PRIMARY KEY,
    sector_code VARCHAR(20) NOT NULL,             -- Finance, Technology等
    sector_name VARCHAR(50) NOT NULL,             -- 金融板块、科技板块
    time BIGINT NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    change_pct NUMERIC(6, 3),
    avg_pe NUMERIC(8, 2),                         -- 平均市盈率
    avg_pb NUMERIC(8, 2),                         -- 平均市净率
    total_market_cap BIGINT,                      -- 总市值（亿元）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(sector_code, time)
);

CREATE INDEX idx_sector_indices_code_time ON sector_indices (sector_code, time DESC);

-- 5. 市场全局状态表
CREATE TABLE IF NOT EXISTS market_global_state (
    id SERIAL PRIMARY KEY,
    state VARCHAR(20) NOT NULL,                   -- bull, bear, sideways
    state_strength NUMERIC(4, 2),                 -- 状态强度（0-1）
    trend NUMERIC(6, 4),                          -- 趋势强度（-0.02 到 +0.02）
    volatility NUMERIC(6, 4),                     -- 全市场波动率
    started_at BIGINT NOT NULL,                   -- 状态开始时间
    last_update BIGINT NOT NULL,                  -- 最后更新时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入初始全局状态
INSERT INTO market_global_state (state, state_strength, trend, volatility, started_at, last_update)
VALUES ('sideways', 0.5, 0.0, 0.02, EXTRACT(EPOCH FROM NOW())::BIGINT, EXTRACT(EPOCH FROM NOW())::BIGINT)
ON CONFLICT DO NOTHING;

-- 6. 板块轮动记录表
CREATE TABLE IF NOT EXISTS sector_rotation (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    leading_sector VARCHAR(20),                   -- 领涨板块
    lagging_sector VARCHAR(20),                   -- 落后板块
    rotation_type VARCHAR(20),                    -- 轮动类型：defensive, cyclical, growth
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(date)
);

-- ============================================================
-- 辅助视图
-- ============================================================

-- 视图：当前活跃指数成分股
CREATE OR REPLACE VIEW v_active_constituents AS
SELECT
    ic.index_code,
    im.index_name,
    ic.stock_symbol,
    sm.name AS stock_name,
    ic.weight,
    ic.rank,
    sm.sector,
    sm.market_cap,
    sm.beta
FROM index_constituents ic
JOIN index_metadata im ON ic.index_code = im.index_code
JOIN stock_metadata sm ON ic.stock_symbol = sm.symbol
WHERE ic.is_active = TRUE
ORDER BY ic.index_code, ic.rank;

-- 视图：指数最新行情
CREATE OR REPLACE VIEW v_latest_index_quotes AS
SELECT DISTINCT ON (index_code)
    index_code,
    index_name,
    value,
    change_value,
    change_pct,
    volume,
    amount,
    time,
    to_timestamp(time) AS quote_time
FROM market_indices
ORDER BY index_code, time DESC;

-- 视图：板块最新行情
CREATE OR REPLACE VIEW v_latest_sector_quotes AS
SELECT DISTINCT ON (sector_code)
    sector_code,
    sector_name,
    value,
    change_pct,
    total_market_cap,
    time,
    to_timestamp(time) AS quote_time
FROM sector_indices
ORDER BY sector_code, time DESC;

-- ============================================================
-- 初始化HAPPY300成分股（市值前100）
-- ============================================================

-- 自动选择市值最大的100只股票作为HAPPY300成分股
INSERT INTO index_constituents (index_code, stock_symbol, weight, rank, is_active)
SELECT
    'HAPPY300' AS index_code,
    symbol AS stock_symbol,
    0.01 AS weight,  -- 初始权重，后续会根据市值计算
    ROW_NUMBER() OVER (ORDER BY market_cap DESC) AS rank,
    TRUE AS is_active
FROM stock_metadata
WHERE is_active = TRUE
ORDER BY market_cap DESC
LIMIT 100
ON CONFLICT (index_code, stock_symbol, join_date) DO UPDATE SET
    weight = EXCLUDED.weight,
    rank = EXCLUDED.rank,
    is_active = EXCLUDED.is_active;

-- 初始化HAPPY50成分股（市值前50）
INSERT INTO index_constituents (index_code, stock_symbol, weight, rank, is_active)
SELECT
    'HAPPY50' AS index_code,
    symbol AS stock_symbol,
    0.02 AS weight,
    ROW_NUMBER() OVER (ORDER BY market_cap DESC) AS rank,
    TRUE AS is_active
FROM stock_metadata
WHERE is_active = TRUE
ORDER BY market_cap DESC
LIMIT 50
ON CONFLICT (index_code, stock_symbol, join_date) DO UPDATE SET
    weight = EXCLUDED.weight,
    rank = EXCLUDED.rank,
    is_active = EXCLUDED.is_active;

-- 初始化GROW100成分股（科技、新能源等成长板块）
INSERT INTO index_constituents (index_code, stock_symbol, weight, rank, is_active)
SELECT
    'GROW100' AS index_code,
    symbol AS stock_symbol,
    0.02 AS weight,
    ROW_NUMBER() OVER (ORDER BY market_cap DESC) AS rank,
    TRUE AS is_active
FROM stock_metadata
WHERE is_active = TRUE
  AND sector IN ('Technology', 'NewEnergy', 'Healthcare')
ORDER BY market_cap DESC
LIMIT 50
ON CONFLICT (index_code, stock_symbol, join_date) DO UPDATE SET
    weight = EXCLUDED.weight,
    rank = EXCLUDED.rank,
    is_active = EXCLUDED.is_active;

-- 初始化板块指数成分股
INSERT INTO index_constituents (index_code, stock_symbol, weight, rank, is_active)
SELECT
    'FIN' AS index_code,
    symbol AS stock_symbol,
    1.0 / COUNT(*) OVER() AS weight,
    ROW_NUMBER() OVER (ORDER BY market_cap DESC) AS rank,
    TRUE AS is_active
FROM stock_metadata
WHERE sector = 'Finance' AND is_active = TRUE
ON CONFLICT (index_code, stock_symbol, join_date) DO UPDATE SET
    weight = EXCLUDED.weight,
    rank = EXCLUDED.rank;

INSERT INTO index_constituents (index_code, stock_symbol, weight, rank, is_active)
SELECT
    'TECH' AS index_code,
    symbol AS stock_symbol,
    1.0 / COUNT(*) OVER() AS weight,
    ROW_NUMBER() OVER (ORDER BY market_cap DESC) AS rank,
    TRUE AS is_active
FROM stock_metadata
WHERE sector = 'Technology' AND is_active = TRUE
ON CONFLICT (index_code, stock_symbol, join_date) DO UPDATE SET
    weight = EXCLUDED.weight,
    rank = EXCLUDED.rank;

-- ============================================================
-- 统计信息
-- ============================================================

-- 查看各指数成分股数量
SELECT
    im.index_code,
    im.index_name,
    COUNT(ic.stock_symbol) AS constituent_count,
    ROUND(SUM(ic.weight)::NUMERIC, 4) AS total_weight
FROM index_metadata im
LEFT JOIN index_constituents ic ON im.index_code = ic.index_code AND ic.is_active = TRUE
GROUP BY im.index_code, im.index_name
ORDER BY im.index_code;

-- 查看HAPPY300成分股分布
SELECT
    sm.sector AS "板块",
    COUNT(*) AS "成分股数量",
    ROUND(SUM(sm.market_cap)::NUMERIC, 0) AS "市值(亿元)",
    ROUND(AVG(ic.weight)::NUMERIC * 100, 2) || '%' AS "平均权重"
FROM index_constituents ic
JOIN stock_metadata sm ON ic.stock_symbol = sm.symbol
WHERE ic.index_code = 'HAPPY300' AND ic.is_active = TRUE
GROUP BY sm.sector
ORDER BY SUM(sm.market_cap) DESC;

-- ============================================================
-- 完成提示
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE '指数体系初始化完成！';
    RAISE NOTICE '- 核心指数：HAPPY300, HAPPY50, GROW100';
    RAISE NOTICE '- 板块指数：FIN, TECH, CONS, NEV 等';
    RAISE NOTICE '- HAPPY300成分股：100只';
    RAISE NOTICE '- HAPPY50成分股：50只';
    RAISE NOTICE '- GROW100成分股：50只';
    RAISE NOTICE '============================================================';
END $$;
