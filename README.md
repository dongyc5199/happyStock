# happyStock - 专业投资模拟平台

> 打造一个**专业图表工具 + AI模拟交易 + 投资社交平台**的综合性金融科技产品

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.4-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

---

## 🚀 快速启动

### 前置要求
1. **Redis** (实时推送必需)
   ```bash
   # 快速启动 Redis (Docker 方式)
   ./start_redis.bat      # Windows
   ./start_redis.sh       # Linux/Mac
   
   # 或参考: REDIS_SETUP.md
   ```

2. **Node.js** (前端) + **Python 3.13+** (后端)

### Windows 用户
```batch
# 一键启动（推荐）
start.bat

# 或分别启动
cd backend && start.bat
cd frontend && start.bat
```

### Linux / macOS 用户
```bash
# 一键启动
./start.sh

# 停止服务
./stop.sh
```

### 访问地址
- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

📖 **详细启动指南**: [STARTUP.md](STARTUP.md) | **快速参考**: [QUICKSTART.md](QUICKSTART.md) | **Redis 安装**: [REDIS_SETUP.md](REDIS_SETUP.md)

---

## ✨ 项目特性

### 已实现功能 ✅
- ✅ **模拟交易系统**: 完整的买入/卖出交易流程
- ✅ **账户管理**: 创建、查询、重置模拟账户
- ✅ **持仓管理**: 实时持仓查询、盈亏计算
- ✅ **交易历史**: 完整的交易记录查询
- ✅ **资产数据**: 股票列表、搜索、K线数据
- ✅ **精确计算**: 使用 Decimal 确保资金精度
- ✅ **事务安全**: 数据库事务保证原子性

### 开发中功能 🚧
- 🚧 专业图表系统（TradingView 集成）
- 🚧 实时行情推送（WebSocket）
- 🚧 AI 交易建议
- 🚧 社交功能（分享、关注）

---

## 🛠️ 技术栈

### 前端
- **框架**: Next.js 15.4 + React 19
- **语言**: TypeScript 5+
- **样式**: Tailwind CSS v4
- **状态管理**: Zustand
- **图表**: Lightweight Charts

### 后端
- **框架**: FastAPI (Python 3.13)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: Tortoise-ORM
- **缓存**: Redis
- **验证**: Pydantic

---

## 📋 项目结构

```
happyStock/
├── frontend/          # Next.js 前端应用
│   ├── src/
│   │   ├── app/       # App Router 页面
│   │   ├── components/# React 组件
│   │   ├── stores/    # Zustand 状态管理
│   │   └── lib/       # 工具库
│   └── package.json
├── backend/           # FastAPI 后端应用
│   ├── main.py        # 应用入口
│   ├── models/        # ORM 模型
│   ├── services/      # 业务逻辑
│   ├── routers/       # API 路由
│   ├── schemas/       # Pydantic 模型
│   └── Pipfile        # Python 依赖
├── doc/               # 项目文档
├── sql_scripts/       # 数据库脚本
├── start.bat          # Windows 启动脚本
├── start.sh           # Linux/Mac 启动脚本
└── README.md          # 本文件
```

---

## 📖 文档

- [模拟交易系统详细设计方案](doc/模拟交易系统详细设计方案.md)
- [项目启动指南](STARTUP.md)
- [快速启动卡片](QUICKSTART.md)
- [项目规划](CLAUDE.md)

---

## 🎯 开发路线图

### ✅ Phase 1: MVP 核心功能（当前阶段）
- [x] 项目架构搭建
- [x] 数据库设计和 ORM 模型
- [x] 模拟交易引擎
- [x] 账户和持仓管理
- [x] 基础交易界面组件
- [ ] 完整前端页面
- [ ] K线图表集成

### 🚧 Phase 2: 功能增强（1-2个月）
- [ ] 实时行情数据对接
- [ ] WebSocket 实时推送
- [ ] TradingView 图表集成
- [ ] 高级订单类型
- [ ] 交易手续费

### 📅 Phase 3: 高级功能（2-3个月）
- [ ] AI 交易建议
- [ ] 回测系统
- [ ] 社交功能
- [ ] 移动端适配

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 📧 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/happyStock)
- 问题反馈: [Issues](https://github.com/yourusername/happyStock/issues)

---

# 第一阶段：MVP开发（0-3个月）详细任务分解

## 第1个月：基础架构搭建与用户系统

### Week 1-2: 技术选型与环境搭建

*   **技术选型：** 确定技术栈（Next.js + TypeScript）。
*   **开发环境搭建：** 配置 Cursor + GitHub Copilot 开发环境。
*   **项目初始化：** 初始化项目架构，并配置 CI/CD 流水线（GitHub Actions）。
*   **数据库设计：** 设计数据库架构（PostgreSQL + Redis）。
*   **云服务配置：** 配置云服务环境（AWS/阿里云）。

#### AI工具应用：

*   使用 Claude 生成项目架构模板。
*   使用 Cursor 快速搭建基础框架。
*   使用 V0 生成基础 UI 组件。

### Week 3-4: 用户系统开发

#### 功能实现：

*   实现注册/登录功能（使用 JWT 认证）。
*   设计用户画像系统。
*   开发权限管理系统。
*   搭建个人中心页面。
*   实现账户安全功能。

#### 关键指标：

*   注册转化率 > 30%。
*   登录响应时间 < 1秒。

## 第2个月：核心功能实现 - 图表与模拟交易

### Week 5-6: 专业图表系统开发

*   **图表集成：** 集成 TradingView 图表库或开发自有图表组件。

#### 核心功能：

*   实现多种图表类型：K线、美国线、山峰图、Heiken Ashi等。
*   支持多时间周期（1分钟-月线全覆盖）。
*   实现多屏显示，最多支持8个图表窗口。

#### 技术指标系统：

*   集成超过50种经典技术指标（MA、MACD、RSI、KDJ、布林带等）。
*   集成专业级高级指标（一目均衡图、市场轮廓等）。
*   支持自定义指标（通过 Pine Script 脚本语言）。

#### AI工具应用：

*   使用 Cursor + Tabnine 辅助后端开发和 API 自动生成。
*   使用 V0 + Claude 生成图表组件。

### Week 7-8: 模拟交易系统开发

#### 核心功能：

*   开发完整的模拟交易流程（买入、卖出、持仓管理、历史交易记录）。
*   对接数据接口获取实时行情。
*   开发简单的 AI 分析功能，为用户提供交易建议。

#### AI工具应用：

*   使用 AutoML + Claude API 快速部署 AI 算法模型。
*   使用 Jest AI + Playwright 生成测试用例。

## 第3个月：产品完善与上线准备

### Week 9-12: 社交功能、移动适配与测试上线

#### 社交功能基础版：

*   实现用户发帖、评论、点赞、关注等基本互动功能。

#### 移动端适配：

*   优化界面布局和交互，确保在不同尺寸的移动设备上都能良好运行。

#### 产品测试与上线：

*   进行全面的功能测试、性能测试和兼容性测试。
*   部署产品至线上服务器，并进行最后的上线检查。

*   整理技术文档，为后续迭代打好基础.