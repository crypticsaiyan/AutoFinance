# Setting Up Real Data Sources for AutoFinance

This guide shows you how to connect AutoFinance to real market data, news APIs, and databases instead of using simulations.

## Quick Start

```bash
cd /home/cryptosaiyan/Documents/AutoFinance/mcp-servers

# 1. Install real data dependencies
pip install -r requirements.txt

# 2. Create environment file
cp .env.example .env

# 3. Add your API keys to .env (see below)

# 4. Test real data
python market/server_real.py  # This uses Yahoo Finance (no API key needed!)
```

---

## 1. Market Data (FREE - No API Key Needed)

### Option A: Yahoo Finance (yfinance) - Recommended

**No API key required!** Already implemented in `market/server_real.py`

**Pros:**
- Free, no rate limits
- Real-time data
- Stocks, crypto, forex, commodities

**Cons:**
- Unofficial API (could break)
- No guaranteed uptime

**Test it:**
```bash
python market/server_real.py
```

### Option B: Alpha Vantage (if you want more reliability)

**Get free API key:** https://www.alphavantage.co/support/#api-key

**Limits:** 5 API calls/minute, 500/day (free tier)

Add to `.env`:
```
ALPHA_VANTAGE_API_KEY=your_key_here
```

---

## 2. News Sentiment (FREE Tier Available)

### NewsAPI

**Get free API key:** https://newsapi.org/register

**Free tier:** 100 requests/day, articles from last 1 month

**Setup:**
1. Register at newsapi.org
2. Get your API key
3. Add to `.env`:
   ```
   NEWS_API_KEY=your_newsapi_key_here
   ```

**Alternative:** Scrape financial news sites (Reddit r/wallstreetbets, Twitter/X, etc.)

---

## 3. Fundamental Data

### Option A: Use Alpha Vantage (same key as market data)

Alpha Vantage provides:
- Company fundamentals
- Balance sheets
- Income statements
- Cash flow

### Option B: Financial Modeling Prep

**Get free API key:** https://financialmodelingprep.com/developer/docs/

**Free tier:** 250 requests/day

Add to `.env`:
```
FMP_API_KEY=your_fmp_key_here
```

---

## 4. Database for Execution & Compliance

### Option A: PostgreSQL (Production)

**Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Arch Linux
sudo pacman -S postgresql

# macOS
brew install postgresql
```

**Setup database:**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE autofinance;
CREATE USER autofinance WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE autofinance TO autofinance;
\q
```

**Add to `.env`:**
```
DATABASE_URL=postgresql://autofinance:your_secure_password@localhost:5432/autofinance
```

### Option B: SQLite (Local Testing)

**Easiest option - no setup needed!**

Add to `.env`:
```
DATABASE_URL=sqlite:///autofinance.db
```

---

## 5. Testing Real Data

### Test Market Server
```bash
cd /home/cryptosaiyan/Documents/AutoFinance/mcp-servers
python -c "
import yfinance as yf
ticker = yf.Ticker('AAPL')
print(ticker.info['currentPrice'])
print('✓ Yahoo Finance working!')
"
```

### Test News API
```bash
curl "https://newsapi.org/v2/everything?q=Apple&apiKey=YOUR_KEY" | jq '.articles[0].title'
```

### Test Database Connection
```bash
python -c "
from sqlalchemy import create_engine
engine = create_engine('sqlite:///test.db')
print('✓ Database connection working!')
"
```

---

## 6. Updated Server Files

I've created real-data versions of the servers. To use them:

### Replace Market Server
```bash
cd /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market
mv server.py server_simulation.py  # Backup old version
mv server_real.py server.py         # Use real data version
```

### Update Other Servers

I can update these for you:
- `news/server.py` - Connect to NewsAPI
- `fundamental/server.py` - Connect to Alpha Vantage or FMP
- `execution/server.py` - Use PostgreSQL/SQLite
- `compliance/server.py` - Use PostgreSQL/SQLite for audit logs

Would you like me to update all of them now?

---

## 7. Rate Limit Management

Free APIs have limits. Here's how to handle them:

### Caching Strategy
```python
# Already implemented in market/server_real.py
_price_cache = {}
_CACHE_TTL = 60  # Cache for 60 seconds
```

### Request Throttling
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=5):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 8. API Key Security

**Never commit API keys to git!**

```bash
# Add to .gitignore
echo "mcp-servers/.env" >> .gitignore
echo "mcp-servers/*.env" >> .gitignore
```

**Use environment variables in production:**
```bash
export NEWS_API_KEY="your_key"
export ALPHA_VANTAGE_API_KEY="your_key"
```

---

## 9. Cost Estimates

All free tiers should be sufficient for development and demo:

| Service | Free Tier | Cost if Exceeding |
|---------|-----------|-------------------|
| Yahoo Finance | Unlimited | Free (but unofficial) |
| Alpha Vantage | 500/day | $49.99/month for premium |
| NewsAPI | 100/day | $449/month for business |
| PostgreSQL | Self-hosted | $0 (or cloud hosting ~$25/month) |

**For hackathon demo:** Free tiers are MORE than enough!

---

## 10. Production Considerations

### High-Frequency Trading?
- Use WebSocket connections (Binance, Kraken APIs)
- Consider paid data providers (Polygon.io, IEX Cloud)
- Setup Redis for sub-second caching

### Regulatory Compliance?
- Use licensed data providers
- Implement data retention policies
- Add audit logging for all API calls

### Scaling?
- Use message queue (RabbitMQ, Kafka)
- Distribute MCP servers across containers
- Setup load balancing

---

## Next Steps

Ready to make it real? Just say:
- "Update all servers to use real data"
- "Setup the database"
- "Show me how to deploy this"

Or test the market server now:
```bash
python /home/cryptosaiyan/Documents/AutoFinance/mcp-servers/market/server_real.py
```
