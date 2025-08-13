--
-- 数据库建库脚本 for 金融科技产品MVP
-- 存储引擎: InnoDB
-- 字符集: utf8mb4
--

-- 创建数据库
CREATE DATABASE IF NOT EXISTS fin_tech_mvp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fin_tech_mvp;

-- 1. 用户表 (users)
-- 存储用户基本信息和认证凭据
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '用户基本信息表';

-- 2. 用户资料表 (user_profiles)
-- 存储用户的扩展资料，与用户表一对一关系
CREATE TABLE user_profiles (
    user_id INT UNSIGNED PRIMARY KEY,
    full_name VARCHAR(100) COMMENT '用户昵称或真实姓名',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    bio TEXT COMMENT '个人简介',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '用户资料表';

-- 3. 金融资产表 (assets)
-- 存储模拟交易中可用的金融产品，如股票、基金
CREATE TABLE assets (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE COMMENT '股票代码/唯一标识符',
    name VARCHAR(100) NOT NULL COMMENT '资产名称',
    exchange VARCHAR(50) COMMENT '所属交易所',
    asset_type ENUM('股票', '基金', '虚拟货币') NOT NULL COMMENT '资产类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '金融资产表';

-- 4. 模拟账户表 (sim_accounts)
-- 存储用户的模拟交易账户信息
CREATE TABLE sim_accounts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    account_name VARCHAR(100) NOT NULL COMMENT '账户名称',
    initial_balance DECIMAL(18, 2) NOT NULL COMMENT '初始资金',
    current_balance DECIMAL(18, 2) NOT NULL COMMENT '当前可用资金',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '模拟账户表';

-- 5. 模拟交易记录表 (sim_trades)
-- 记录每一次模拟交易的详细信息
CREATE TABLE sim_trades (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    account_id INT UNSIGNED NOT NULL,
    asset_id INT UNSIGNED NOT NULL,
    trade_type ENUM('BUY', 'SELL') NOT NULL COMMENT '交易类型：买入或卖出',
    quantity DECIMAL(18, 4) NOT NULL COMMENT '交易数量',
    price DECIMAL(18, 4) NOT NULL COMMENT '成交价格',
    trade_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '交易时间',
    FOREIGN KEY (account_id) REFERENCES sim_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '模拟交易记录表';

-- 6. 模拟持仓表 (sim_holdings)
-- 记录用户在模拟账户中的持仓情况
CREATE TABLE sim_holdings (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    account_id INT UNSIGNED NOT NULL,
    asset_id INT UNSIGNED NOT NULL,
    quantity DECIMAL(18, 4) NOT NULL COMMENT '持有数量',
    avg_price DECIMAL(18, 4) NOT NULL COMMENT '平均成本价',
    FOREIGN KEY (account_id) REFERENCES sim_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    UNIQUE KEY (account_id, asset_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '模拟持仓表';

-- 7. 帖子表 (posts)
-- 存储用户发布的社交帖子
CREATE TABLE posts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    content TEXT NOT NULL COMMENT '帖子内容',
    likes_count INT UNSIGNED DEFAULT 0 COMMENT '点赞数',
    comments_count INT UNSIGNED DEFAULT 0 COMMENT '评论数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '社交帖子表';

-- 8. 评论表 (comments)
-- 存储用户对帖子的评论
CREATE TABLE comments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    post_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    content TEXT NOT NULL COMMENT '评论内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '评论表';

-- 9. 点赞表 (likes)
-- 记录用户对帖子的点赞
CREATE TABLE likes (
    user_id INT UNSIGNED NOT NULL,
    post_id INT UNSIGNED NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '点赞表';

-- 10. 关注表 (followers)
-- 记录用户之间的关注关系
CREATE TABLE followers (
    follower_id INT UNSIGNED NOT NULL COMMENT '关注者ID',
    following_id INT UNSIGNED NOT NULL COMMENT '被关注者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '关注关系表';

-- 11. 通知表 (notifications)
-- 记录系统或用户的通知信息
CREATE TABLE notifications (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    type ENUM('comment', 'like', 'follow', 'system') NOT NULL COMMENT '通知类型',
    message TEXT NOT NULL COMMENT '通知内容',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '系统通知表';