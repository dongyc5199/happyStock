-- ============================================================================
-- A股虚拟市场数据库初始化脚本
-- 创建日期: 2025-10-28
-- 描述: 创建虚拟市场所有表（stocks, indices, price_data等）
-- 数据库: PostgreSQL 14+
-- ============================================================================

-- 设置字符集
SET client_encoding = 'UTF8';

-- ============================================================================
-- 1. 板块表 (Sectors)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sectors (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    name_en VARCHAR(50),
    beta NUMERIC(4, 2) NOT NULL,
    total_market_cap BIGINT,
    stock_count INTEGER DEFAULT 0,
    avg_change_pct NUMERIC(6, 3),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_sectors_beta ON sectors(beta);

-- 插入10大板块初始数据
INSERT INTO sectors (code, name, name_en, beta, description) VALUES
('TECH', '科技板块', 'Technology', 1.25, '互联网、软件、芯片、人工智能等高科技行业'),
('FIN', '金融板块', 'Finance', 0.75, '银行、保险、券商等金融服务行业'),
('CONS', '消费板块', 'Consumer', 0.85, '白酒、家电、食品饮料等消费品行业'),
('NEV', '新能源板块', 'NewEnergy', 1.40, '电动车、光伏、储能、充电桩等新能源行业'),
('HEALTH', '医药板块', 'Healthcare', 0.90, '创新药、医疗器械、生物医药等医疗健康行业'),
('IND', '工业板块', 'Industry', 1.05, '机械制造、建筑、航空航天等工业行业'),
('REAL', '地产板块', 'RealEstate', 1.15, '房地产开发、物业管理等地产行业'),
('ENERGY', '能源板块', 'Energy', 0.95, '煤炭、石油、天然气等传统能源行业'),
('MATER', '材料板块', 'Materials', 1.10, '钢铁、化工、有色金属等基础材料行业'),
('UTIL', '公用事业板块', 'Utilities', 0.65, '电力、水务、燃气等公共事业')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- 2. 股票表 (Stocks)
-- ============================================================================
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    sector_code VARCHAR(20) NOT NULL REFERENCES sectors(code),
    current_price NUMERIC(10, 2) NOT NULL CHECK (current_price > 0),
    previous_close NUMERIC(10, 2) NOT NULL,
    change_value NUMERIC(10, 2),
    change_pct NUMERIC(6, 3) CHECK (change_pct >= -10 AND change_pct <= 10),
    volume BIGINT DEFAULT 0,
    turnover NUMERIC(18, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector_code);
CREATE INDEX IF NOT EXISTS idx_stocks_price ON stocks(current_price DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_change_pct ON stocks(change_pct DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_is_active ON stocks(is_active);

-- ============================================================================
-- 3. 股票元数据表 (Stock Metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol VARCHAR(10) PRIMARY KEY REFERENCES stocks(symbol) ON DELETE CASCADE,
    market_cap BIGINT NOT NULL,
    market_cap_tier VARCHAR(20) NOT NULL CHECK (market_cap_tier IN ('超大盘', '大盘', '中盘', '小盘', '微盘')),
    beta NUMERIC(4, 2) NOT NULL DEFAULT 1.0 CHECK (beta >= 0.5 AND beta <= 2.0),
    volatility NUMERIC(6, 4) NOT NULL CHECK (volatility >= 0.01 AND volatility <= 1.0),
    outstanding_shares BIGINT NOT NULL,
    listing_date DATE DEFAULT '2024-01-01',
    is_happy300 BOOLEAN DEFAULT FALSE,
    weight_in_happy300 NUMERIC(6, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_meta_market_cap ON stock_metadata(market_cap DESC);
CREATE INDEX IF NOT EXISTS idx_stock_meta_is_happy300 ON stock_metadata(is_happy300);
CREATE INDEX IF NOT EXISTS idx_stock_meta_beta ON stock_metadata(beta);

-- ============================================================================
-- 4. 指数表 (Indices)
-- ============================================================================
CREATE TABLE IF NOT EXISTS indices (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    index_type VARCHAR(20) NOT NULL CHECK (index_type IN ('CORE', 'SECTOR')),
    base_point NUMERIC(10, 2) NOT NULL,
    base_date DATE DEFAULT '2024-01-01',
    current_value NUMERIC(10, 2) NOT NULL,
    previous_close NUMERIC(10, 2) NOT NULL,
    change_value NUMERIC(10, 2),
    change_pct NUMERIC(6, 3),
    volume BIGINT,
    turnover BIGINT,
    constituent_count INTEGER DEFAULT 0,
    calculation_method VARCHAR(50) DEFAULT 'FREE_FLOAT_MKT_CAP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_indices_type ON indices(index_type);
CREATE INDEX IF NOT EXISTS idx_indices_change_pct ON indices(change_pct DESC);

-- 插入13个指数初始数据
INSERT INTO indices (code, name, index_type, base_point, current_value, previous_close, constituent_count) VALUES
-- 核心指数
('HAPPY300', '快乐综合指数', 'CORE', 3000, 3000, 3000, 100),
('HAPPY50', '快乐50指数', 'CORE', 2500, 2500, 2500, 50),
('GROW100', '创新成长指数', 'CORE', 2000, 2000, 2000, 50),
-- 行业指数
('TECH_IDX', '科技指数', 'SECTOR', 1000, 1000, 1000, 20),
('FIN_IDX', '金融指数', 'SECTOR', 1000, 1000, 1000, 12),
('CONS_IDX', '消费指数', 'SECTOR', 1000, 1000, 1000, 15),
('NEV_IDX', '新能源指数', 'SECTOR', 1000, 1000, 1000, 10),
('HEALTH_IDX', '医药健康指数', 'SECTOR', 1000, 1000, 1000, 12),
('IND_IDX', '工业指数', 'SECTOR', 1000, 1000, 1000, 10),
('REAL_IDX', '地产指数', 'SECTOR', 1000, 1000, 1000, 8),
('ENERGY_IDX', '能源指数', 'SECTOR', 1000, 1000, 1000, 8),
('MATER_IDX', '材料指数', 'SECTOR', 1000, 1000, 1000, 6),
('UTIL_IDX', '公用事业指数', 'SECTOR', 1000, 1000, 1000, 5)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- 5. 指数成分股表 (Index Constituents)
-- ============================================================================
CREATE TABLE IF NOT EXISTS index_constituents (
    id SERIAL PRIMARY KEY,
    index_code VARCHAR(20) NOT NULL REFERENCES indices(code) ON DELETE CASCADE,
    stock_symbol VARCHAR(10) NOT NULL REFERENCES stocks(symbol) ON DELETE CASCADE,
    weight NUMERIC(6, 4) NOT NULL CHECK (weight >= 0.0001 AND weight <= 0.1000),
    rank INTEGER,
    join_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(index_code, stock_symbol)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_constituents_index ON index_constituents(index_code);
CREATE INDEX IF NOT EXISTS idx_constituents_stock ON index_constituents(stock_symbol);
CREATE INDEX IF NOT EXISTS idx_constituents_weight ON index_constituents(weight DESC);
CREATE INDEX IF NOT EXISTS idx_constituents_active ON index_constituents(is_active);

-- ============================================================================
-- 6. 价格数据表 (Price Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_data (
    id BIGSERIAL PRIMARY KEY,
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('STOCK', 'INDEX')),
    target_code VARCHAR(20) NOT NULL,
    timestamp BIGINT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    open NUMERIC(10, 2) NOT NULL,
    close NUMERIC(10, 2) NOT NULL,
    high NUMERIC(10, 2) NOT NULL,
    low NUMERIC(10, 2) NOT NULL,
    volume BIGINT DEFAULT 0,
    turnover NUMERIC(18, 2) DEFAULT 0,
    change_pct NUMERIC(6, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (low <= open AND low <= close),
    CHECK (high >= open AND high >= close),
    UNIQUE(target_type, target_code, timestamp)
);

-- 创建索引（关键性能优化）
CREATE INDEX IF NOT EXISTS idx_price_target ON price_data(target_code, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_price_datetime ON price_data(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_price_type ON price_data(target_type);
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_data(timestamp DESC);

-- ============================================================================
-- 7. 市场状态表 (Market States)
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_states (
    id SERIAL PRIMARY KEY,
    state VARCHAR(20) NOT NULL CHECK (state IN ('BULL', 'BEAR', 'SIDEWAYS')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    daily_trend NUMERIC(6, 4) NOT NULL CHECK (daily_trend >= -0.05 AND daily_trend <= 0.05),
    volatility_multiplier NUMERIC(4, 2) DEFAULT 1.0,
    description TEXT,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_market_state_current ON market_states(is_current);
CREATE INDEX IF NOT EXISTS idx_market_state_start ON market_states(start_time DESC);

-- 插入初始市场状态（横盘）
INSERT INTO market_states (state, start_time, daily_trend, volatility_multiplier, description, is_current) VALUES
('SIDEWAYS', CURRENT_TIMESTAMP, 0.0, 1.0, '市场初始化状态，横盘震荡', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 触发器: 自动更新 updated_at 字段
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表创建触发器
DROP TRIGGER IF EXISTS update_stocks_updated_at ON stocks;
CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_stock_metadata_updated_at ON stock_metadata;
CREATE TRIGGER update_stock_metadata_updated_at BEFORE UPDATE ON stock_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_indices_updated_at ON indices;
CREATE TRIGGER update_indices_updated_at BEFORE UPDATE ON indices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_constituents_updated_at ON index_constituents;
CREATE TRIGGER update_constituents_updated_at BEFORE UPDATE ON index_constituents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 数据完整性验证视图
-- ============================================================================

-- 视图1: 检查指数权重和是否为1.0
CREATE OR REPLACE VIEW v_index_weight_validation AS
SELECT
    index_code,
    SUM(weight) as total_weight,
    COUNT(*) as constituent_count,
    ABS(SUM(weight) - 1.0) as weight_deviation
FROM index_constituents
WHERE is_active = TRUE
GROUP BY index_code
HAVING ABS(SUM(weight) - 1.0) > 0.0001;

-- 视图2: 检查K线数据一致性
CREATE OR REPLACE VIEW v_price_data_validation AS
SELECT
    id,
    target_type,
    target_code,
    datetime,
    CASE
        WHEN low > LEAST(open, close) THEN 'LOW_TOO_HIGH'
        WHEN high < GREATEST(open, close) THEN 'HIGH_TOO_LOW'
        ELSE 'VALID'
    END as validation_status
FROM price_data
WHERE low > LEAST(open, close) OR high < GREATEST(open, close);

-- 视图3: 股票市值排名
CREATE OR REPLACE VIEW v_stock_market_cap_ranking AS
SELECT
    s.symbol,
    s.name,
    s.sector_code,
    sm.market_cap,
    sm.market_cap_tier,
    RANK() OVER (ORDER BY sm.market_cap DESC) as market_cap_rank
FROM stocks s
JOIN stock_metadata sm ON s.symbol = sm.symbol
WHERE s.is_active = TRUE
ORDER BY sm.market_cap DESC;

-- ============================================================================
-- 说明
-- ============================================================================

-- 表创建顺序说明:
-- 1. sectors (无外键依赖)
-- 2. stocks (依赖 sectors)
-- 3. stock_metadata (依赖 stocks)
-- 4. indices (无外键依赖，但有初始数据)
-- 5. index_constituents (依赖 stocks 和 indices)
-- 6. price_data (逻辑依赖 stocks 和 indices，但无强制外键)
-- 7. market_states (无外键依赖)

-- 下一步操作:
-- 1. 执行本脚本创建所有表
-- 2. 运行 backend/lib/data_initializer.py 插入106只股票数据
-- 3. 运行 backend/lib/data_initializer.py 生成90天历史K线数据

-- ============================================================================
-- 完成
-- ============================================================================

COMMENT ON TABLE sectors IS '行业板块表，定义10大板块';
COMMENT ON TABLE stocks IS '股票基本信息表，包含106只虚拟股票';
COMMENT ON TABLE stock_metadata IS '股票元数据表，包含Beta、市值等静态属性';
COMMENT ON TABLE indices IS '市场指数表，包含3大核心指数和10个行业指数';
COMMENT ON TABLE index_constituents IS '指数成分股关系表，股票与指数的多对多关系';
COMMENT ON TABLE price_data IS 'K线价格数据表，存储股票和指数的历史价格';
COMMENT ON TABLE market_states IS '市场状态表，记录牛市/熊市/横盘状态';

-- 执行成功提示
DO $$
BEGIN
    RAISE NOTICE '✅ A股虚拟市场数据库初始化完成！';
    RAISE NOTICE '📊 已创建7个核心表：sectors, stocks, stock_metadata, indices, index_constituents, price_data, market_states';
    RAISE NOTICE '📈 已插入10个板块初始数据';
    RAISE NOTICE '📊 已插入13个指数定义';
    RAISE NOTICE '🚀 下一步：运行 backend/lib/data_initializer.py 插入股票数据和历史K线';
END $$;
