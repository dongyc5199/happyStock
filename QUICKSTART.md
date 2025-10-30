# 🚀 快速启动卡片

> 5秒内启动 happyStock 项目

## Windows 用户

```batch
# 双击运行
start.bat

# 或在命令行运行
.\start.bat
```

## Linux / macOS 用户

```bash
# 一键启动
./start.sh

# 停止服务
./stop.sh
```

---

## 访问地址

- **前端**: http://localhost:3000
- **后端**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## 分别启动

### Windows
```batch
# 后端
cd backend
start.bat

# 前端
cd frontend
start.bat
```

### Linux / macOS
```bash
# 后端
cd backend && ./start.sh

# 前端
cd frontend && ./start.sh
```

---

## 初始化测试数据

```bash
cd backend
pipenv shell
python scripts/init_test_data.py
```

---

## 常用命令

```bash
# 查看后端日志
cd backend && pipenv run uvicorn main:app --reload

# 查看前端日志
cd frontend && npm run dev

# 清理缓存
cd frontend && rm -rf .next

# 重建数据库
cd backend && rm db.sqlite3*
```

---

**详细文档**: [STARTUP.md](STARTUP.md)
