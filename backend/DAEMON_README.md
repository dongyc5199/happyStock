# Market Data Generation Daemon

This directory contains the market data generation system for simulated stock trading.

## Architecture

The system consists of two main daemons:

1. **Market Data Generator** (`start_market_generator.py`)
   - Generates 1-minute K-line data during trading hours
   - Trading hours: 9:30-11:30, 13:00-15:00 (Beijing time)
   - Updates every minute with realistic price movements
   - Uses Geometric Brownian Motion with dynamic market states

2. **Data Aggregator** (`start_aggregator.py`)
   - Aggregates 1m data into larger intervals (5m, 15m, 30m, 60m, 120m)
   - Runs periodically (default: every 5 minutes)
   - Ensures all timeframes are available for charts

## Setup

### 1. Install Dependencies

```bash
cd backend
pipenv install

# Additional dependencies for data generation
pipenv install numpy sqlalchemy psycopg2-binary
```

### 2. Configure Database

Copy `.env.example` to `.env` and configure your database:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

**PostgreSQL (Recommended for Production):**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/happystock
```

**SQLite (Development Only):**
```env
DATABASE_URL=sqlite:///happystock.db
```

### 3. Initialize Database

Run the database migration script:

```bash
# For PostgreSQL
psql -U postgres -d happystock -f ../sql_scripts/create_market_data_tables.sql

# For SQLite
sqlite3 happystock.db < ../sql_scripts/create_market_data_tables.sql
```

This creates:
- `market_klines` - Partitioned K-line data table
- `stock_state` - Current price and market state
- `market_status` - Global trading status
- `stock_realtime_price` - Performance cache table
- `stock_metadata` - Stock information (pre-populated with 10 stocks)

### 4. Initialize Historical Data (Optional)

Generate historical data to populate charts:

```bash
pipenv run python init_historical_data.py --days 30
```

This generates 30 days of historical 1-minute K-line data for all stocks.

## Running the Daemons

### Development Mode

**Terminal 1 - Market Data Generator:**
```bash
cd backend
pipenv run python start_market_generator.py --test --verbose
```

Options:
- `--test`: Run continuously without time checks (for testing)
- `--verbose`: Enable debug logging
- `--db-url`: Override database URL

**Terminal 2 - Data Aggregator:**
```bash
cd backend
pipenv run python start_aggregator.py --interval 5
```

Options:
- `--interval N`: Run aggregation every N minutes (default: 5)

### Production Mode

**Without test mode** (respects trading hours):
```bash
# Market data generator (runs only during trading hours)
pipenv run python start_market_generator.py

# Data aggregator
pipenv run python start_aggregator.py
```

### Using systemd (Linux)

Create service files in `/etc/systemd/system/`:

**market-generator.service:**
```ini
[Unit]
Description=Market Data Generator
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/happyStock/backend
Environment="PATH=/path/to/.local/share/virtualenvs/backend-xxx/bin"
ExecStart=/path/to/.local/share/virtualenvs/backend-xxx/bin/python start_market_generator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**data-aggregator.service:**
```ini
[Unit]
Description=Data Aggregator
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/happyStock/backend
Environment="PATH=/path/to/.local/share/virtualenvs/backend-xxx/bin"
ExecStart=/path/to/.local/share/virtualenvs/backend-xxx/bin/python start_aggregator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable market-generator data-aggregator
sudo systemctl start market-generator data-aggregator
sudo systemctl status market-generator data-aggregator
```

### Using PM2 (Node.js process manager)

```bash
# Install PM2 globally
npm install -g pm2

# Start daemons
pm2 start start_market_generator.py --name market-generator --interpreter python3
pm2 start start_aggregator.py --name data-aggregator --interpreter python3

# View logs
pm2 logs market-generator
pm2 logs data-aggregator

# Save process list
pm2 save

# Setup auto-start on boot
pm2 startup
```

## Monitoring

### Check Daemon Status

**Market Generator:**
```bash
# Check logs
tail -f logs/market_generator.log

# Check database
psql -U postgres -d happystock -c "SELECT * FROM market_status;"
```

**Data Aggregator:**
```bash
# Check logs
tail -f logs/data_aggregator.log

# Check aggregated data
psql -U postgres -d happystock -c "
  SELECT interval, COUNT(*)
  FROM market_klines
  WHERE symbol='AAPL'
  GROUP BY interval;
"
```

### Performance Monitoring

Monitor key metrics:

```sql
-- K-line count by interval
SELECT interval, COUNT(*) as count
FROM market_klines
GROUP BY interval;

-- Recent prices
SELECT symbol, current_price, market_state,
       to_timestamp(last_update) as updated_at
FROM stock_state
ORDER BY symbol;

-- Market status
SELECT is_trading, current_session, last_update
FROM market_status;
```

## Trading Hours

The system follows Chinese stock market trading hours (Beijing time):

- **Morning Session**: 9:30 - 11:30 (120 minutes)
- **Afternoon Session**: 13:00 - 15:00 (120 minutes)
- **Daily Total**: 240 minutes (4 hours)
- **Market Closed**: Weekends, outside trading hours

In **test mode**, the generator runs continuously for development purposes.

## Price Generation Algorithm

The system uses **Geometric Brownian Motion (GBM)** with dynamic market states:

### Market States (Markov Chain)

1. **Bull Market** (15% annual upward drift, normal volatility)
2. **Bear Market** (-15% annual downward drift, 1.5x volatility)
3. **Sideways Market** (0% drift, 0.8x volatility)

States transition probabilistically every 30-120 minutes based on a Markov chain.

### OHLCV Generation

- **Open**: Previous bar's close
- **Close**: GBM calculation with drift and random shock
- **High/Low**: Derived from intraday volatility
- **Volume**: Correlated with price movement (larger moves = higher volume)

## Data Aggregation

1-minute bars are aggregated into larger intervals:

- **5m, 15m, 30m**: Minute-based aggregation
- **60m (1h), 120m (2h)**: Hour-based aggregation
- **Daily, Weekly, Monthly**: Future implementation

Aggregation rules:
- **Open**: First bar's open
- **High**: Maximum of all highs
- **Low**: Minimum of all lows
- **Close**: Last bar's close
- **Volume**: Sum of all volumes

## Database Performance

### Connection Pooling

The system uses SQLAlchemy connection pooling:
- **Pool size**: 20 base connections
- **Max overflow**: 30 additional connections
- **Pool timeout**: 30 seconds
- **Pre-ping**: Enabled (verifies connections before use)

### Optimization Features

1. **Partitioned Tables**: Monthly partitions for K-line data
2. **Covering Indexes**: Avoid table lookups for queries
3. **Bulk Inserts**: Batch operations for performance
4. **Realtime Cache**: UNLOGGED table for hot data

### Expected Performance

- **100 concurrent users**: Supported
- **Query response**: <100ms (P95)
- **Write throughput**: 1.67 QPS per stock
- **Read throughput**: 17 QPS per stock

## Troubleshooting

### Generator Not Running

1. Check trading hours (use `--test` mode for continuous generation)
2. Verify database connection in `.env`
3. Check logs for errors
4. Ensure stock metadata is populated

### No Data Being Generated

```bash
# Check if stocks exist
psql -U postgres -d happystock -c "SELECT * FROM stock_metadata;"

# Check stock states
psql -U postgres -d happystock -c "SELECT * FROM stock_state;"

# If empty, reinitialize database
psql -U postgres -d happystock -f ../sql_scripts/create_market_data_tables.sql
```

### Aggregation Not Working

1. Ensure 1-minute data exists
2. Check aggregator daemon is running
3. Verify lookback period covers available data
4. Check database permissions

### Database Connection Issues

```bash
# Test database connection
pipenv run python -c "from lib.db_models import get_db_manager; db = get_db_manager(); print(db.db_url)"

# Test database tables
pipenv run python lib/db_models.py
```

## Development

### Testing Price Generator

```bash
# Test price generation algorithm
pipenv run python lib/price_generator.py
```

This outputs sample K-lines for bull, bear, and sideways markets.

### Testing Database Models

```bash
# Test database connection and models
pipenv run python lib/db_models.py
```

### Testing Aggregation

```bash
# Aggregate single stock
pipenv run python lib/data_aggregator.py --symbol AAPL --interval 5m

# Aggregate all intervals for a stock
pipenv run python lib/data_aggregator.py --symbol AAPL --interval all

# Aggregate all stocks
pipenv run python lib/data_aggregator.py
```

## API Integration

The generated data is accessed via the main FastAPI application:

```python
# In main.py or routes
from lib.db_models import get_db_manager

@app.get("/api/klines")
def get_klines(symbol: str, interval: str = "1m", limit: int = 200):
    db = get_db_manager()
    with db.get_session() as session:
        klines = session.query(MarketKline).filter(
            MarketKline.symbol == symbol,
            MarketKline.interval == interval
        ).order_by(MarketKline.time.desc()).limit(limit).all()

        return [k.to_dict() for k in reversed(klines)]
```

## Next Steps

1. **Implement API endpoints** for K-line data with time range support
2. **Add Redis caching** for frequently accessed data
3. **Implement volume correlation** with smarter algorithms
4. **Add more stocks** to stock_metadata table
5. **Create monitoring dashboard** for daemon health
6. **Implement alerting** for daemon failures
7. **Add data quality checks** to detect anomalies

## License

Internal use only - part of happyStock MVP project.
