# happyStock 项目启动指南

本文档提供 happyStock 项目的快速启动方法。

## 📋 前提条件

### 必需软件
- **Node.js** >= 18.0.0 ([下载地址](https://nodejs.org/))
- **Python** >= 3.9 ([下载地址](https://www.python.org/))
- **pipenv** (Python 包管理工具)
  ```bash
  pip install pipenv
  ```

### 可选软件
- **PostgreSQL** (生产环境推荐，开发环境使用 SQLite)
- **Redis** (用于缓存和实时数据)

---

## 🚀 快速启动

### Windows 用户

#### 方法 1: 一键启动（推荐）
双击根目录的 **`start.bat`** 文件，脚本会：
- ✅ 自动检查运行环境
- ✅ 自动安装依赖（如果缺失）
- ✅ 同时启动前端和后端服务
- ✅ 在新窗口中运行，便于查看日志

#### 方法 2: 分别启动
**启动后端**:
```cmd
cd backend
start.bat
```

**启动前端**:
```cmd
cd frontend
start.bat
```

---

### Linux / macOS 用户

#### 方法 1: 一键启动（推荐）
```bash
chmod +x start.sh
./start.sh
```

#### 方法 2: 分别启动
**启动后端**:
```bash
cd backend
chmod +x start.sh
./start.sh
```

**启动前端**:
```bash
cd frontend
chmod +x start.sh
./start.sh
```

#### 停止服务
```bash
./stop.sh
```

---

## 🌐 访问地址

启动成功后，可以访问以下地址：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端应用** | http://localhost:3000 | Next.js 开发服务器 |
| **后端 API** | http://localhost:8000 | FastAPI 服务 |
| **API 文档** | http://localhost:8000/docs | Swagger UI 交互式文档 |
| **API 文档（备用）** | http://localhost:8000/redoc | ReDoc 文档 |

---

## 📦 手动安装依赖

如果自动安装失败，可以手动安装：

### 后端依赖
```bash
cd backend
pipenv install
```

### 前端依赖
```bash
cd frontend
npm install
```

---

## 🛠️ 开发模式

### 后端开发
```bash
cd backend
pipenv shell                    # 激活虚拟环境
uvicorn main:app --reload      # 启动服务（热重载）
```

### 前端开发
```bash
cd frontend
npm run dev                     # 启动开发服务器（Turbopack）
```

---

## 🔧 环境配置

### 后端配置
编辑 `backend/config.py` 或创建 `backend/.env` 文件：

```env
# 应用配置
DEBUG=True
APP_NAME=happyStock Trading API

# 数据库配置（开发环境使用 SQLite）
DATABASE_URL=sqlite://db.sqlite3

# 生产环境使用 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/happystock

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production
```

### 前端配置
前端配置已在 `frontend/package.json` 中定义，默认连接到 `http://localhost:8000`。

如需修改后端地址，可创建 `frontend/.env.local`：
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🗄️ 数据库初始化

### 首次启动
第一次启动后端时，Tortoise-ORM 会自动创建数据库表结构（`generate_schemas=True`）。

### 初始化测试数据
```bash
cd backend
pipenv shell
python scripts/init_test_data.py
```

测试数据包括：
- 测试用户账户
- 模拟交易账户
- 测试资产数据（股票）

---

## ❓ 常见问题

### Q1: pipenv 安装失败
**解决方法**:
```bash
# Windows
python -m pip install --upgrade pip
pip install pipenv

# Linux/Mac
pip3 install --upgrade pip
pip3 install pipenv
```

### Q2: 端口被占用
**错误**: `Address already in use`

**解决方法**:
```bash
# Windows - 查找并关闭占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Q3: 前端依赖安装慢
**解决方法**: 使用国内镜像源
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Q4: 数据库文件损坏
**解决方法**: 删除并重新创建
```bash
cd backend
rm db.sqlite3*
# 重新启动后端，会自动创建新数据库
```

### Q5: 虚拟环境找不到
**解决方法**: 重新创建虚拟环境
```bash
cd backend
pipenv --rm        # 删除旧环境
pipenv install     # 重新创建
```

---

## 📚 更多信息

- **项目文档**: [doc/模拟交易系统详细设计方案.md](doc/模拟交易系统详细设计方案.md)
- **API 文档**: 启动后访问 http://localhost:8000/docs
- **技术栈**:
  - 前端: Next.js 15 + React 19 + TypeScript + Tailwind CSS
  - 后端: FastAPI + Tortoise-ORM + SQLite/PostgreSQL
  - 状态管理: Zustand
  - 图表: Lightweight Charts

---

## 🆘 获取帮助

如遇到问题，请检查：
1. 日志输出（终端窗口）
2. 后端日志: `backend/backend.log` (Linux/Mac)
3. 前端日志: `frontend/frontend.log` (Linux/Mac)
4. API 文档: http://localhost:8000/docs

---

**祝你开发愉快！🎉**
