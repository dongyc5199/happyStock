# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

happyStock is a financial technology MVP platform focused on simulated stock trading with social features. This is a monorepo containing:
- **Frontend**: Next.js 15.4 with React 19, TypeScript, and Tailwind CSS
- **Backend**: FastAPI (Python 3.13) with PostgreSQL and Redis
- **Database**: MySQL/PostgreSQL for structured data, Redis for caching

### Product Vision
打造一个**专业图表工具 + AI模拟交易 + 投资社交平台**的综合性金融科技产品，通过游戏化和社交化降低投资学习门槛，帮助用户在零风险环境下提升投资能力。

### Core Value Propositions
- **专业性**: TradingView级别的专业图表分析工具
- **趣味性**: 游戏化学习体验，降低学习门槛
- **社交性**: 投资者社区，知识共享与交流
- **安全性**: 纯模拟交易，无金融牌照风险

### Current Status
The project is in **early MVP stage (Week 1-2)**, having completed initial infrastructure setup. Currently implementing core features including user authentication, professional charting (TradingView integration planned), simulated trading, and social networking capabilities.

## Repository Structure

```
happyStock/
├── frontend/          # Next.js frontend application
│   ├── src/
│   │   └── app/       # Next.js App Router pages
│   ├── package.json
│   └── tsconfig.json
├── backend/           # FastAPI backend application
│   ├── main.py        # FastAPI entry point
│   ├── Pipfile        # Python dependencies
│   └── Pipfile.lock
├── sql_scripts/       # Database schema definitions
│   └── create_user_table.sql  # Complete MVP schema
└── doc/               # Project documentation (Chinese)
```

## Development Commands

### Frontend (Next.js)
```bash
cd frontend

# Development server (runs on http://localhost:3000)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Backend (FastAPI)
```bash
cd backend

# Install dependencies (using Pipenv)
pipenv install

# Run development server
pipenv run uvicorn main:app --reload

# Or activate virtual environment first
pipenv shell
uvicorn main:app --reload
```

### Database Setup
```bash
# Execute the complete schema from root directory
mysql -u username -p database_name < sql_scripts/create_user_table.sql
# Or for PostgreSQL:
psql -U username -d database_name -f sql_scripts/create_user_table.sql
```

## Architecture & Key Decisions

### Frontend Architecture
- **Framework**: Next.js 15.4 with App Router (not Pages Router)
- **Path Aliases**: Use `@/*` to import from `src/` directory (configured in tsconfig.json)
- **Styling**: Tailwind CSS v4 with PostCSS
- **Type Safety**: Strict TypeScript configuration enabled
- **Font**: Geist font family (loaded via next/font)

### Backend Architecture
- **Framework**: FastAPI for high-performance async API
- **Database ORM**: psycopg2-binary for PostgreSQL connections
- **Caching**: Redis for session management and real-time data caching
- **API Design**: RESTful endpoints starting from a simple root endpoint

### Database Schema
The complete database schema is defined in `sql_scripts/create_user_table.sql` and includes:

**Core Tables**:
- `users` - User authentication (username, email, password_hash)
- `user_profiles` - Extended user information (full_name, avatar_url, bio)
- `sim_accounts` - Simulated trading accounts with balance tracking
- `sim_trades` - Trade history (BUY/SELL transactions)
- `sim_holdings` - Current positions (quantity, avg_price)
- `assets` - Financial products (stocks, funds, crypto)

**Social Features**:
- `posts` - User-generated content with engagement metrics
- `comments` - Post comments
- `likes` - Post likes (user-post relationship)
- `followers` - User follow relationships
- `notifications` - System and user notifications

**Key Constraints**:
- All foreign keys use `ON DELETE CASCADE`
- Unique constraints on `(account_id, asset_id)` for holdings
- Character set: utf8mb4_unicode_ci for full Unicode support
- Engine: InnoDB for transaction support

## MVP Development Roadmap (0-3 Months)

### Month 1: Infrastructure & User System

**Week 1-2: Technical Setup** ✅ (Current Stage)
- [x] Development environment setup (Cursor + GitHub Copilot)
- [x] Project initialization (Next.js + TypeScript)
- [x] Database architecture design (PostgreSQL + Redis)
- [x] Initial project structure created

**Week 3-4: User System Development** (Next)
- [ ] User registration/login (JWT authentication)
- [ ] User profile system
- [ ] Permission management
- [ ] Personal center page
- [ ] Account security features
- **KPI**: Registration conversion rate > 30%, Login response time < 1s

### Month 2: Core Features

**Week 5-6: Professional Charting System**
- [ ] Integrate TradingView Charting Library or develop custom charts
- [ ] Implement K-line, candlestick charts, technical indicators
- [ ] Drawing tools (trend lines, support/resistance)
- [ ] Multi-timeframe switching (1min to monthly)
- [ ] Chart data caching optimization
- **Tech Stack**: WebGL rendering, WebSocket real-time push, smooth rendering for millions of data points

**Week 7-8: Simulated Trading System**
- [ ] Simulated account system design
- [ ] Trading matching engine
- [ ] Order management system
- [ ] Position & P&L calculation
- [ ] Trading history records
- **AI Integration**: Simple AI recommendation system, risk assessment model, smart stop-loss alerts

### Month 3: Product Polish & Launch

**Week 9-10: Social Features (Basic Version)**
- [ ] User follow system
- [ ] Trading updates sharing
- [ ] Comment & like functionality
- [ ] Simple leaderboards
- [ ] Basic community rules

**Week 11-12: Testing & Launch**
- [ ] Comprehensive functional testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] Production deployment
- [ ] Monitoring system setup

### 3-Month Success Metrics
- ✅ MVP product successfully launched
- ✅ Core features complete and usable
- ✅ Mobile responsive design
- 📊 Registered users: 1,000+
- 📊 Daily active users: 200+
- 📊 User retention rate: 70%+
- ⚡ Page load time: < 3s
- ⚡ API response time: < 500ms
- ⚡ System availability: > 99%

## Development Workflow

### When Adding New Features
1. Check if database schema changes are needed in `sql_scripts/create_user_table.sql`
2. Implement backend API endpoints in `backend/main.py` (will be modularized later)
3. Create frontend components in `frontend/src/app/` using App Router conventions
4. Use TypeScript path alias `@/` for clean imports
5. Test thoroughly before committing
6. Update this CLAUDE.md if architectural decisions are made

## Technical Stack Details

### Current Implementation
**Frontend**:
- React 19.1.0 (latest stable)
- Next.js 15.4.6 with Turbopack for fast dev builds
- TypeScript 5+
- Tailwind CSS v4
- ESLint with Next.js config

**Backend**:
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- psycopg2-binary (PostgreSQL adapter)
- redis (Redis client)

### Planned Tech Stack (from roadmap)

**Frontend (Future)**:
- UI Library: Ant Design / Material-UI
- Charts: TradingView Charting Library / D3.js
- State Management: Zustand / Redux Toolkit
- Styling: TailwindCSS ✅ (already in use)

**Backend (Future)**:
- Alternative framework consideration: Node.js + Express / NestJS
- Message Queue: RabbitMQ / Kafka (for high-volume trading events)
- WebSocket: Socket.io (for real-time market data)
- API Documentation: Swagger

**AI/ML Stack (Future)**:
- Machine Learning: TensorFlow.js / PyTorch
- Natural Language: Claude API / GPT-4 API
- AutoML: Google AutoML / H2O.ai
- Data Analysis: Pandas + NumPy

## Budget & Resources

### Monthly Operating Costs (Estimated: ¥4,500)
- **AI Tools**: ¥2,000/month
  - Cursor Pro: $20
  - GitHub Copilot: $10
  - Claude API: $20
  - V0: $30
- **Cloud Services**: ¥1,500/month
  - Server: ¥800
  - CDN: ¥300
  - Database: ¥400
- **Third-party APIs**: ¥1,000/month
  - Market data: ¥800
  - Other services: ¥200

## Key Decision Points

### Critical Choices to Make
1. **Charting Solution**:
   - Option A: TradingView Charting Library (paid but professional, faster to market)
   - Option B: Custom development with D3.js (lower cost but longer development cycle)
   - **Recommendation**: Start with TradingView for MVP, consider custom solution post-validation

2. **Market Data Source**:
   - Option A: Free data sources (limitations on frequency/features)
   - Option B: Paid data services (higher cost but stable and reliable)
   - **Recommendation**: Free for MVP testing, upgrade to paid after user validation

3. **Team Expansion Timing**:
   - Option A: Hire immediately when funding secured
   - Option B: Validate MVP first, then expand team
   - **Recommendation**: Solo through MVP, expand after achieving 1,000+ users

## Risk Management

### Technical Risks
- **Chart Performance**: Use mature charting libraries, optimize with WebGL rendering
- **Data Latency**: CDN acceleration + Redis caching optimization
- **System Stability**: Automated monitoring + quick rollback mechanisms

### Market Risks
- **Slow User Growth**: Strengthen content marketing, community building
- **Competition**: Differentiate with unique features (AI + gamification + social)
- **Monetization**: Diversify revenue streams (freemium, B2B API, premium features)

### Compliance Risks
- **Clear Educational Positioning**: Emphasize learning and simulation, not real trading
- **Avoid Real Trading**: Pure simulation only, no financial license required
- **Content Moderation**: Implement automated and manual review systems

## Long-term Roadmap

### Phase 1: MVP (0-3 months) - Current
- Basic functionality development
- 1,000 seed users
- Product validation

### Phase 2: Growth (3-6 months)
- Enhanced social features
- Gamification mechanics
- 10,000 registered users
- First revenue

### Phase 3: Expansion (6-12 months)
- AI feature upgrades
- B2B service development
- 100,000 registered users
- Monthly revenue: ¥500,000+

### Phase 4: Maturity (12+ months)
- Platform ecosystem building
- Open API platform
- International expansion
- Funding round or acquisition

## Important Notes

- The frontend uses **Turbopack** for development (`--turbopack` flag in dev script)
- Database schema uses **MySQL syntax** but project mentions PostgreSQL - verify target DB before production
- All user-facing text in database and docs is in **Chinese** (target market: China)
- Project is designed for **solo developer** leveraging AI tools (Cursor, Claude, GitHub Copilot, V0)
- MVP target is **3-month development cycle**
- **Focus on core features first** - avoid feature creep during MVP stage
- **Data-driven decisions** - establish monitoring early, make all decisions based on metrics
- **User-first approach** - rapid response to user feedback, continuous iteration
- **AI-powered efficiency** - leverage AI tools extensively while maintaining code quality
