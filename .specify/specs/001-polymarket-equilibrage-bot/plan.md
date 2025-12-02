# Implementation Plan: Polymarket Equilibrage Bot

**Feature**: 001-polymarket-equilibrage-bot  
**Status**: Planning  
**Created**: 2025-12-02

---

## Overview

This implementation plan outlines the technical approach for building the Polymarket Equilibrage Bot. The system will be built as a full-stack application with a Python backend for trading logic and a modern web frontend for the dashboard.

---

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI for REST API
- **Database**: PostgreSQL for persistence
- **ORM**: SQLAlchemy
- **Task Queue**: Celery with Redis for background jobs
- **Polymarket Integration**: py-clob-client (official Polymarket Python SDK)

### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI (MUI)
- **Charts**: Recharts for performance visualization
- **Real-time Updates**: WebSocket connection to backend

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Environment**: .env for configuration
- **Logging**: Python logging with structured output

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │Settings  │  │History   │  │Scanner   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API + WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API Layer  │  │ WebSocket    │  │  Auth/Config │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Trading Engine│  │  Scanner     │  │ Opportunity  │     │
│  │              │  │  Service     │  │  Scorer      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Position      │  │ Whale        │  │ Info         │     │
│  │Monitor       │  │ Tracker      │  │ Aggregator   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              Background Workers (Celery)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Market Scanner│  │Position      │  │ Whale        │     │
│  │Task          │  │Monitor Task  │  │ Tracker Task │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Data Layer (PostgreSQL)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Positions    │  │ Trades       │  │ Config       │     │
│  │ Opportunities│  │ Whale Data   │  │ Market Data  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### Component 1: Core Backend Infrastructure

#### [NEW] `backend/app/main.py`
FastAPI application entry point with CORS, middleware, and route registration.

#### [NEW] `backend/app/config.py`
Configuration management using Pydantic settings, loading from environment variables.

#### [NEW] `backend/app/database.py`
Database connection setup, session management, and base model definitions.

#### [NEW] `backend/requirements.txt`
Python dependencies including FastAPI, SQLAlchemy, py-clob-client, Celery, etc.

---

### Component 2: Data Models

#### [NEW] `backend/app/models/position.py`
SQLAlchemy model for active and historical positions:
- Market ID, entry time, entry prices (YES/NO)
- Current prices, status (active/closed/liquidated)
- P&L calculations, liquidation details

#### [NEW] `backend/app/models/opportunity.py`
Model for detected opportunities:
- Market ID, score (1-10), detection time
- Liquidity metrics, whale activity indicators
- Scoring factors breakdown

#### [NEW] `backend/app/models/config.py`
User configuration model:
- Wallet credentials (encrypted)
- Trading parameters (SL, TP, capital allocation)
- Position limits, opportunity threshold

#### [NEW] `backend/app/models/trade.py`
Trade history model:
- Transaction details, timestamps
- Entry/exit prices, P&L
- Market information

#### [NEW] `backend/app/models/whale.py`
Whale tracker data model:
- Wallet address, total volume
- Recent trades, markets active in

---

### Component 3: Trading Engine

#### [NEW] `backend/app/services/trading_engine.py`
Core trading logic:
- `enter_position()`: Execute 50/50 YES/NO entry
- `liquidate_position()`: Sell specified side
- `close_position()`: Close both sides
- Transaction confirmation and error handling

#### [NEW] `backend/app/services/polymarket_client.py`
Wrapper around py-clob-client:
- Market data fetching
- Order placement and execution
- Balance queries
- Rate limiting and retry logic

#### [NEW] `backend/app/services/position_monitor.py`
Position monitoring service:
- Track all active positions
- Detect 30% divergence
- Trigger automatic liquidation
- Update position status in database

---

### Component 4: Opportunity Detection

#### [NEW] `backend/app/services/market_scanner.py`
Market scanning service:
- Fetch active Polymarket markets
- Filter for suitable markets (liquidity, activity)
- Identify equilibrage candidates
- Store opportunities in database

#### [NEW] `backend/app/services/opportunity_scorer.py`
Opportunity scoring algorithm:
- Multi-factor scoring (liquidity, volatility, whale activity, news)
- Weighted scoring model
- Score normalization to 1-10 scale
- Transparent factor breakdown

#### [NEW] `backend/app/services/whale_tracker.py`
Whale detection and tracking:
- Identify high-volume wallets
- Track whale positions in markets
- Analyze whale trading patterns
- Update whale database

#### [NEW] `backend/app/services/info_aggregator.py`
Information aggregation service:
- News API integration (e.g., NewsAPI, Google News)
- On-chain data analysis
- Market trend detection
- Information relevance scoring

---

### Component 5: Background Tasks

#### [NEW] `backend/app/tasks/scanner_task.py`
Celery task for periodic market scanning:
- Runs every 5 minutes (configurable)
- Calls market_scanner and opportunity_scorer
- Updates opportunity database

#### [NEW] `backend/app/tasks/monitor_task.py`
Celery task for position monitoring:
- Runs every 30 seconds (configurable)
- Monitors all active positions
- Triggers liquidations when needed

#### [NEW] `backend/app/tasks/whale_task.py`
Celery task for whale tracking:
- Runs every 10 minutes (configurable)
- Updates whale data
- Identifies new whales

#### [NEW] `backend/app/celery_app.py`
Celery application configuration and task registration.

---

### Component 6: API Endpoints

#### [NEW] `backend/app/api/positions.py`
Position management endpoints:
- `GET /api/positions` - List active positions
- `POST /api/positions` - Manually enter position
- `DELETE /api/positions/{id}` - Close position
- `GET /api/positions/history` - Historical positions

#### [NEW] `backend/app/api/opportunities.py`
Opportunity endpoints:
- `GET /api/opportunities` - List detected opportunities
- `POST /api/opportunities/scan` - Trigger manual scan

#### [NEW] `backend/app/api/config.py`
Configuration endpoints:
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration
- `POST /api/config/wallet` - Configure wallet

#### [NEW] `backend/app/api/dashboard.py`
Dashboard data endpoints:
- `GET /api/dashboard/overview` - Capital, P&L, active positions count
- `GET /api/dashboard/performance` - Performance metrics

#### [NEW] `backend/app/api/whales.py`
Whale data endpoints:
- `GET /api/whales` - List tracked whales
- `GET /api/whales/{address}` - Whale details

#### [NEW] `backend/app/api/info.py`
Information scanner endpoints:
- `GET /api/info/news` - Recent news
- `GET /api/info/trends` - Market trends

#### [NEW] `backend/app/api/websocket.py`
WebSocket endpoint for real-time updates:
- Position updates
- New opportunities
- Trade executions

---

### Component 7: Frontend Structure

#### [NEW] `frontend/src/App.tsx`
Main React application with routing and layout.

#### [NEW] `frontend/src/store/store.ts`
Redux store configuration with slices for positions, opportunities, config, etc.

#### [NEW] `frontend/src/pages/Dashboard.tsx`
Main dashboard page:
- Capital overview cards
- Active positions table
- Recent opportunities
- Quick stats

#### [NEW] `frontend/src/pages/Settings.tsx`
Configuration page:
- Wallet configuration form
- Trading parameters (SL, TP, capital allocation)
- Position limits slider
- Opportunity threshold slider

#### [NEW] `frontend/src/pages/History.tsx`
Trade history page:
- Historical trades table
- Filters (date, market, outcome)
- Export to CSV button
- Performance charts

#### [NEW] `frontend/src/pages/Scanner.tsx`
Information scanner page:
- News feed
- Whale movements
- Market trends
- Opportunity table with scores

#### [NEW] `frontend/src/components/PositionCard.tsx`
Component for displaying individual position with close button.

#### [NEW] `frontend/src/components/OpportunityTable.tsx`
Table component for displaying opportunities with scores.

#### [NEW] `frontend/src/services/api.ts`
API client for backend communication using axios.

#### [NEW] `frontend/src/services/websocket.ts`
WebSocket client for real-time updates.

---

### Component 8: Security & Wallet Management

#### [NEW] `backend/app/security/encryption.py`
Wallet credential encryption/decryption using Fernet (symmetric encryption).

#### [NEW] `backend/app/security/wallet.py`
Wallet management:
- Load wallet from encrypted credentials
- Sign transactions
- Balance queries

---

### Component 9: Database Migrations

#### [NEW] `backend/alembic/`
Alembic migration setup for database schema versioning.

#### [NEW] `backend/alembic/versions/001_initial_schema.py`
Initial database schema migration with all tables.

---

### Component 10: Deployment & Configuration

#### [NEW] `docker-compose.yml`
Docker Compose configuration:
- Backend service (FastAPI)
- Frontend service (React dev server or Nginx)
- PostgreSQL database
- Redis for Celery
- Celery worker

#### [NEW] `backend/Dockerfile`
Backend container definition.

#### [NEW] `frontend/Dockerfile`
Frontend container definition.

#### [NEW] `.env.example`
Example environment variables:
- Database credentials
- Polymarket API keys
- News API keys
- Encryption keys

#### [NEW] `README.md`
Project documentation:
- Setup instructions
- Configuration guide
- Architecture overview
- Development workflow

---

## Data Model

### Positions Table
```sql
CREATE TABLE positions (
    id UUID PRIMARY KEY,
    market_id VARCHAR NOT NULL,
    market_name VARCHAR NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    entry_price_yes DECIMAL NOT NULL,
    entry_price_no DECIMAL NOT NULL,
    capital_yes DECIMAL NOT NULL,
    capital_no DECIMAL NOT NULL,
    current_price_yes DECIMAL,
    current_price_no DECIMAL,
    status VARCHAR NOT NULL, -- 'active', 'closed', 'liquidated'
    liquidated_side VARCHAR, -- 'yes', 'no', NULL
    liquidation_time TIMESTAMP,
    close_time TIMESTAMP,
    pnl DECIMAL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Opportunities Table
```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    market_id VARCHAR NOT NULL,
    market_name VARCHAR NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 10),
    liquidity DECIMAL,
    whale_activity_score INTEGER,
    news_relevance_score INTEGER,
    volatility_score INTEGER,
    detected_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Config Table
```sql
CREATE TABLE config (
    id INTEGER PRIMARY KEY DEFAULT 1,
    wallet_credentials_encrypted TEXT,
    stop_loss DECIMAL DEFAULT 0,
    take_profit DECIMAL DEFAULT 0,
    capital_allocation_percent INTEGER DEFAULT 10,
    max_positions INTEGER DEFAULT 3,
    opportunity_threshold INTEGER DEFAULT 6,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Trades Table
```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    position_id UUID REFERENCES positions(id),
    side VARCHAR NOT NULL, -- 'yes', 'no'
    action VARCHAR NOT NULL, -- 'buy', 'sell'
    price DECIMAL NOT NULL,
    amount DECIMAL NOT NULL,
    transaction_hash VARCHAR,
    executed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Whales Table
```sql
CREATE TABLE whales (
    id UUID PRIMARY KEY,
    wallet_address VARCHAR UNIQUE NOT NULL,
    total_volume DECIMAL,
    trade_count INTEGER,
    markets_active JSON,
    last_trade_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Specification

### REST Endpoints

#### Positions
- `GET /api/positions` - List active positions
  - Response: `{ positions: Position[] }`
- `POST /api/positions` - Enter new position
  - Body: `{ market_id: string, capital_amount: number }`
  - Response: `{ position: Position }`
- `DELETE /api/positions/{id}` - Close position
  - Response: `{ success: boolean }`

#### Opportunities
- `GET /api/opportunities` - List opportunities
  - Query: `?min_score=6`
  - Response: `{ opportunities: Opportunity[] }`

#### Configuration
- `GET /api/config` - Get configuration
  - Response: `{ config: Config }`
- `PUT /api/config` - Update configuration
  - Body: `{ stop_loss?: number, take_profit?: number, ... }`
  - Response: `{ config: Config }`

#### Dashboard
- `GET /api/dashboard/overview` - Dashboard overview
  - Response: `{ total_capital: number, active_positions: number, total_pnl: number, ... }`

### WebSocket Events

#### Client → Server
- `subscribe_positions` - Subscribe to position updates
- `subscribe_opportunities` - Subscribe to opportunity updates

#### Server → Client
- `position_update` - Position state changed
- `new_opportunity` - New opportunity detected
- `trade_executed` - Trade completed

---

## Verification Plan

### Automated Tests

#### Unit Tests
```bash
# Backend unit tests
cd backend
pytest tests/unit/

# Test coverage for:
# - Opportunity scoring algorithm
# - Position P&L calculations
# - Wallet encryption/decryption
# - Trading engine logic
```

#### Integration Tests
```bash
# Backend integration tests
cd backend
pytest tests/integration/

# Test coverage for:
# - API endpoints
# - Database operations
# - Polymarket client integration (mocked)
# - WebSocket connections
```

#### Frontend Tests
```bash
# Frontend component tests
cd frontend
npm test

# Test coverage for:
# - Component rendering
# - Redux state management
# - API service calls
```

### Manual Verification

#### 1. Configuration Testing
- [ ] Navigate to Settings page
- [ ] Configure wallet (use test wallet)
- [ ] Set trading parameters (SL=0, TP=0, capital=10%)
- [ ] Set position limit to 3
- [ ] Set opportunity threshold to 6
- [ ] Verify settings persist after page refresh

#### 2. Market Scanning
- [ ] Navigate to Scanner page
- [ ] Click "Scan Now" button
- [ ] Verify opportunities appear in table
- [ ] Verify each opportunity has score 1-10
- [ ] Verify opportunities sorted by score

#### 3. Position Entry (Manual)
- [ ] From opportunities table, click "Enter Position" on high-scored opportunity
- [ ] Verify position appears in Dashboard active positions
- [ ] Verify capital allocated correctly (50% YES, 50% NO)
- [ ] Verify wallet balance decreased

#### 4. Position Monitoring
- [ ] Wait for price movement in active position
- [ ] Verify current prices update in real-time
- [ ] Verify P&L calculated correctly
- [ ] If 30% drop occurs, verify automatic liquidation

#### 5. Manual Position Close
- [ ] Click "Close" button on active position
- [ ] Confirm in dialog
- [ ] Verify position moved to History
- [ ] Verify capital returned to wallet

#### 6. Historical Data
- [ ] Navigate to History page
- [ ] Verify closed positions appear
- [ ] Verify P&L displayed correctly
- [ ] Test date filter
- [ ] Test CSV export

### Performance Testing
```bash
# Load testing with locust
cd backend
locust -f tests/load/locustfile.py

# Verify:
# - Dashboard loads within 2 seconds
# - Position monitoring responds within 1 second
# - Market scan completes within 60 seconds
```

### Security Testing
- [ ] Verify wallet credentials encrypted in database
- [ ] Verify no private keys in logs
- [ ] Verify API requires authentication (if implemented)
- [ ] Test SQL injection prevention
- [ ] Test XSS prevention in frontend

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Set up project structure
- Configure Docker Compose
- Database schema and migrations
- Basic FastAPI app with health check
- React app with routing

### Phase 2: Core Trading (Week 2)
- Polymarket client integration
- Trading engine implementation
- Position monitoring service
- Position API endpoints
- Dashboard position display

### Phase 3: Opportunity Detection (Week 3)
- Market scanner implementation
- Opportunity scoring algorithm
- Whale tracker
- Scanner API endpoints
- Scanner page UI

### Phase 4: Configuration & Settings (Week 4)
- Configuration management
- Wallet encryption
- Settings API endpoints
- Settings page UI
- Parameter validation

### Phase 5: Real-time & Polish (Week 5)
- WebSocket implementation
- Real-time dashboard updates
- Information aggregator
- Historical data page
- Performance charts

### Phase 6: Testing & Deployment (Week 6)
- Comprehensive testing
- Bug fixes
- Documentation
- Deployment guide
- Production configuration

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Polymarket API rate limits | Implement caching, request throttling, exponential backoff |
| Network failures during trades | Transaction retry logic, state recovery, confirmation checks |
| Wallet security | Encryption at rest, secure key management, no logging of credentials |
| Inaccurate opportunity scoring | Transparent scoring, manual override, iterative refinement |
| Insufficient liquidity | Pre-trade liquidity checks, configurable minimum thresholds |
| Database performance | Indexing on frequently queried fields, connection pooling |
| Real-time update latency | WebSocket optimization, efficient database queries |

---

## Dependencies

### External Services
- Polymarket API (market data, trading)
- News API (e.g., NewsAPI.org)
- Ethereum node (for on-chain data)

### Python Packages
- fastapi
- uvicorn
- sqlalchemy
- alembic
- psycopg2-binary
- py-clob-client
- celery
- redis
- cryptography
- pydantic
- python-dotenv

### Node Packages
- react
- react-router-dom
- @reduxjs/toolkit
- @mui/material
- axios
- recharts
- socket.io-client

---

## Open Questions

1. **Polymarket API Access**: Do we have API keys and access to py-clob-client?
2. **News API**: Which news API should we integrate? (NewsAPI, Google News, other?)
3. **Hosting**: Where will this be deployed? (Local, VPS, cloud?)
4. **Authentication**: Should the dashboard have login/authentication, or is it single-user local only?
5. **Notification**: Should the bot send notifications (email, Telegram) for important events?

---

## Next Steps

1. Review and approve this implementation plan
2. Set up development environment (Docker, PostgreSQL, Redis)
3. Obtain Polymarket API credentials
4. Begin Phase 1 implementation
5. Iterative development with testing at each phase
