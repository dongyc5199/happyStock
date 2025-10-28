-- ============================================================================
-- A股虚拟市场数据库初始化脚本 (SQLite版本)
-- 创建日期: 2025-10-28
-- 数据库: SQLite 3.x
-- ============================================================================

-- ============================================================================
-- 1. 板块表 (Sectors)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sectors (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_en TEXT,
    beta REAL NOT NULL,
    total_market_cap INTEGER,
    stock_count INTEGER DEFAULT 0,
    avg_change_pct REAL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 插入10大板块初始数据
INSERT OR IGNORE INTO sectors (code, name, name_en, beta, description) VALUES
('TECH', '科技板块', 'Technology', 1.25, '互联网、软件、芯片、人工智能等高科技行业'),
('FIN', '金融板块', 'Finance', 0.75, '银行、保险、券商等金融服务行业'),
('CONS', '消费板块', 'Consumer', 0.85, '白酒、家电、食品饮料等消费品行业'),
('NEV', '新能源板块', 'NewEnergy', 1.40, '电动车、光伏、储能、充电桩等新能源行业'),
('HEALTH', '医药板块', 'Healthcare', 0.90, '创新药、医疗器械、生物医药等医疗健康行业'),
('IND', '工业板块', 'Industry', 1.05, '机械制造、建筑、航空航天等工业行业'),
('REAL', '地产板块', 'RealEstate', 1.15, '房地产开发、物业管理等地产行业'),
('ENERGY', '能源板块', 'Energy', 0.95, '煤炭、石油、天然气等传统能源行业'),
('MATER', '材料板块', 'Materials', 1.10, '钢铁、化工、有色金属等基础材料行业'),
('UTIL', '公用事业板块', 'Utilities', 0.65, '电力、水务、燃气等公共事业');

-- ============================================================================
-- 2. 股票表 (Stocks)
-- ============================================================================
CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector_code TEXT NOT NULL,
    current_price REAL NOT NULL CHECK (current_price > 0),
    previous_close REAL NOT NULL,
    change_value REAL,
    change_pct REAL CHECK (change_pct >= -10 AND change_pct <= 10),
    volume INTEGER DEFAULT 0,
    turnover REAL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sector_code) REFERENCES sectors(code)
);

CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector_code);
CREATE INDEX IF NOT EXISTS idx_stocks_price ON stocks(current_price DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_change_pct ON stocks(change_pct DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_is_active ON stocks(is_active);

-- ============================================================================
-- 3. 股票元数据表 (Stock Metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol TEXT PRIMARY KEY,
    market_cap INTEGER NOT NULL,
    market_cap_tier TEXT NOT NULL CHECK (market_cap_tier IN ('超大盘', '大盘', '中盘', '小盘', '微盘')),
    beta REAL NOT NULL DEFAULT 1.0 CHECK (beta >= 0.5 AND beta <= 2.0),
    volatility REAL NOT NULL CHECK (volatility >= 0.01 AND volatility <= 1.0),
    outstanding_shares INTEGER NOT NULL,
    listing_date TEXT DEFAULT '2024-01-01',
    is_happy300 INTEGER DEFAULT 0,
    weight_in_happy300 REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stock_meta_market_cap ON stock_metadata(market_cap DESC);
CREATE INDEX IF NOT EXISTS idx_stock_meta_is_happy300 ON stock_metadata(is_happy300);
CREATE INDEX IF NOT EXISTS idx_stock_meta_beta ON stock_metadata(beta);

-- ============================================================================
-- 4. 指数表 (Indices)
-- ============================================================================
CREATE TABLE IF NOT EXISTS indices (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    index_type TEXT NOT NULL CHECK (index_type IN ('CORE', 'SECTOR')),
    base_point REAL NOT NULL,
    base_date TEXT DEFAULT '2024-01-01',
    current_value REAL NOT NULL,
    previous_close REAL NOT NULL,
    change_value REAL,
    change_pct REAL,
    volume INTEGER,
    turnover INTEGER,
    constituent_count INTEGER DEFAULT 0,
    calculation_method TEXT DEFAULT 'FREE_FLOAT_MKT_CAP',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_indices_type ON indices(index_type);
CREATE INDEX IF NOT EXISTS idx_indices_change_pct ON indices(change_pct DESC);

-- 插入13个指数初始数据
INSERT OR IGNORE INTO indices (code, name, index_type, base_point, current_value, previous_close, constituent_count) VALUES
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
('UTIL_IDX', '公用事业指数', 'SECTOR', 1000, 1000, 1000, 5);

-- ============================================================================
-- 5. 指数成分股表 (Index Constituents)
-- ============================================================================
CREATE TABLE IF NOT EXISTS index_constituents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_code TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    weight REAL NOT NULL CHECK (weight >= 0.0001 AND weight <= 0.1000),
    rank INTEGER,
    join_date TEXT DEFAULT (date('now')),
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (index_code) REFERENCES indices(code) ON DELETE CASCADE,
    FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol) ON DELETE CASCADE,
    UNIQUE(index_code, stock_symbol)
);

CREATE INDEX IF NOT EXISTS idx_constituents_index ON index_constituents(index_code);
CREATE INDEX IF NOT EXISTS idx_constituents_stock ON index_constituents(stock_symbol);
CREATE INDEX IF NOT EXISTS idx_constituents_weight ON index_constituents(weight DESC);
CREATE INDEX IF NOT EXISTS idx_constituents_active ON index_constituents(is_active);

-- ============================================================================
-- 6. 价格数据表 (Price Data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS price_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL CHECK (target_type IN ('STOCK', 'INDEX')),
    target_code TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    datetime TEXT NOT NULL,
    open REAL NOT NULL,
    close REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    volume INTEGER DEFAULT 0,
    turnover REAL DEFAULT 0,
    change_pct REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    CHECK (low <= open AND low <= close),
    CHECK (high >= open AND high >= close),
    UNIQUE(target_type, target_code, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_price_target ON price_data(target_code, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_price_datetime ON price_data(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_price_type ON price_data(target_type);
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_data(timestamp DESC);

-- ============================================================================
-- 7. 市场状态表 (Market States)
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL CHECK (state IN ('BULL', 'BEAR', 'SIDEWAYS')),
    start_time TEXT NOT NULL,
    end_time TEXT,
    daily_trend REAL NOT NULL CHECK (daily_trend >= -0.05 AND daily_trend <= 0.05),
    volatility_multiplier REAL DEFAULT 1.0,
    description TEXT,
    is_current INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_market_state_current ON market_states(is_current);
CREATE INDEX IF NOT EXISTS idx_market_state_start ON market_states(start_time DESC);

-- 插入初始市场状态（横盘）
INSERT OR IGNORE INTO market_states (state, start_time, daily_trend, volatility_multiplier, description, is_current) VALUES
('SIDEWAYS', datetime('now'), 0.0, 1.0, '市场初始化状态，横盘震荡', 1);

-- ============================================================================
-- 触发器: 自动更新 updated_at 字段
-- ============================================================================
CREATE TRIGGER IF NOT EXISTS update_stocks_updated_at
AFTER UPDATE ON stocks
FOR EACH ROW
BEGIN
    UPDATE stocks SET updated_at = CURRENT_TIMESTAMP WHERE symbol = NEW.symbol;
END;

CREATE TRIGGER IF NOT EXISTS update_stock_metadata_updated_at
AFTER UPDATE ON stock_metadata
FOR EACH ROW
BEGIN
    UPDATE stock_metadata SET updated_at = CURRENT_TIMESTAMP WHERE symbol = NEW.symbol;
END;

CREATE TRIGGER IF NOT EXISTS update_indices_updated_at
AFTER UPDATE ON indices
FOR EACH ROW
BEGIN
    UPDATE indices SET updated_at = CURRENT_TIMESTAMP WHERE code = NEW.code;
END;

CREATE TRIGGER IF NOT EXISTS update_constituents_updated_at
AFTER UPDATE ON index_constituents
FOR EACH ROW
BEGIN
    UPDATE index_constituents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
