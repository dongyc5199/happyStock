# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

happyStock is a financial technology MVP platform focused on simulated stock trading with social features. This is a monorepo containing:
- **Frontend**: Next.js 15.4 with React 19, TypeScript, and Tailwind CSS
- **Backend**: FastAPI (Python 3.13) with PostgreSQL and Redis
- **Database**: MySQL/PostgreSQL for structured data, Redis for caching

The project is in early MVP stage, implementing core features including user authentication, professional charting (TradingView integration planned), simulated trading, and social networking capabilities.

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

## Development Workflow

### When Adding New Features
1. Check if database schema changes are needed in `sql_scripts/create_user_table.sql`
2. Implement backend API endpoints in `backend/main.py` (will be modularized later)
3. Create frontend components in `frontend/src/app/` using App Router conventions
4. Use TypeScript path alias `@/` for clean imports

### Planned Features (from MVP roadmap)
- User authentication with JWT
- TradingView chart integration (50+ technical indicators)
- Multi-timeframe support (1min to monthly)
- Real-time market data integration
- AI-powered trading suggestions
- Mobile responsive design

## Technical Stack Details

**Frontend Dependencies**:
- React 19.1.0 (latest stable)
- Next.js 15.4.6 with Turbopack for fast dev builds
- TypeScript 5+
- ESLint with Next.js config

**Backend Dependencies**:
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- psycopg2-binary (PostgreSQL adapter)
- redis (Redis client)

## Important Notes

- The frontend uses **Turbopack** for development (`--turbopack` flag in dev script)
- Database schema uses **MySQL syntax** but project mentions PostgreSQL - verify target DB
- All user-facing text in database and docs is in **Chinese**
- Project is designed for **solo developer** leveraging AI tools (Cursor, Claude, GitHub Copilot)
- MVP target is **3-month development cycle**
