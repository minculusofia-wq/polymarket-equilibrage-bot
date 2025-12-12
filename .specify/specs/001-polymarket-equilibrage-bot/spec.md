# Feature Specification: Polymarket Equilibrage Bot

**Feature ID**: 001-polymarket-equilibrage-bot  
**Status**: Draft  
**Created**: 2025-12-02  
**Last Updated**: 2025-12-02

---

## Executive Summary

The Polymarket Equilibrage Bot is an automated trading system that implements a flexible equilibrage strategy on Polymarket prediction markets. The bot enters positions with configurable YES/NO ratios per bet, monitors price movements, and intelligently liquidates losing positions while holding winning positions when configurable stop-loss or take-profit thresholds are reached. The strategy maximizes profit by selling the declining side and riding the winning side to bet resolution.

---

## Problem Statement

### Current Situation
Traders on Polymarket must manually:
- Monitor multiple markets for equilibrage opportunities
- Track price movements across YES/NO positions
- Execute trades at optimal times
- Manage risk across multiple concurrent positions
- Analyze whale movements and market information

### Challenges
1. **Time-intensive monitoring**: Requires constant attention to multiple markets
2. **Missed opportunities**: Manual monitoring can't track all potential opportunities
3. **Emotional trading**: Human traders may hold losing positions too long
4. **Information overload**: Difficult to aggregate and analyze all relevant data sources
5. **Capital management**: Hard to maintain disciplined position sizing across multiple bets

### Target Users
- Active Polymarket traders seeking automated equilibrage strategies
- Traders who want systematic, emotion-free trading execution
- Users who want to capitalize on market inefficiencies automatically

---

## Goals & Success Criteria

### Primary Goals
1. **Automated Trading**: Execute equilibrage strategy without manual intervention
2. **Risk Management**: Protect capital through configurable limits and stop-losses
3. **Opportunity Detection**: Identify and score potential equilibrage opportunities
4. **Transparency**: Provide complete visibility into bot decisions and performance

### Success Metrics
- Bot successfully enters and manages positions according to strategy
- All trades execute within configured risk parameters
- Dashboard provides real-time visibility into all operations
- Historical data accurately tracks all trades and outcomes
- Opportunity scoring system identifies viable trades

---

## User Stories

### Epic 1: Configuration & Setup

#### US-1.1: Wallet Configuration
**As a** trader  
**I want to** configure my wallet credentials securely  
**So that** the bot can execute trades on my behalf

**Acceptance Criteria:**
- Settings page has dedicated wallet configuration section
- Support for private key or seed phrase input
- Wallet credentials stored securely (encrypted)
- Wallet balance displayed in dashboard
- Ability to disconnect/reconnect wallet

#### US-1.2: Trading Parameters
**As a** trader  
**I want to** configure trading parameters (SL, TP, entry ratios)  
**So that** I can control risk and position sizing

**Acceptance Criteria:**
- Stop-loss (SL) configurable with default value of 0% (disabled)
- Take-profit (TP) configurable with default value of 0% (disabled)
- Option for single threshold (applies to both YES/NO) OR separate thresholds for YES and NO
- Entry ratio configurable per bet (e.g., 50/50, 60/40, 70/30, or even 100/0)
- Default entry ratio: 50% YES / 50% NO
- Per-bet capital allocation as percentage (1-100%)
- Settings persist across bot restarts
- Changes take effect for new positions only

#### US-1.3: Position Limits
**As a** trader  
**I want to** limit the number of concurrent positions (1-10)  
**So that** I can control overall exposure

**Acceptance Criteria:**
- Configurable slider/input for max positions (1-10)
- Bot respects limit and won't exceed it
- Dashboard shows current vs max positions
- Bot prioritizes highest-scored opportunities when at limit

#### US-1.4: Opportunity Threshold
**As a** trader  
**I want to** set minimum opportunity score for auto-trading (1-10)  
**So that** the bot only trades high-quality opportunities

**Acceptance Criteria:**
- Configurable threshold (1-10 scale)
- Bot only auto-trades when opportunity score >= threshold
- Opportunities below threshold shown but not traded
- Threshold setting saved and persisted

### Epic 2: Opportunity Detection & Scoring

#### US-2.1: Market Scanning
**As a** trader  
**I want to** the bot to scan Polymarket for equilibrage opportunities  
**So that** I don't miss potential trades

**Acceptance Criteria:**
- Bot continuously scans active Polymarket markets
- Identifies markets suitable for equilibrage strategy
- Filters out markets with insufficient liquidity
- Scans run at configurable intervals

#### US-2.2: Opportunity Scoring
**As a** trader  
**I want to** opportunities scored from 1-10  
**So that** I can understand trade quality

**Acceptance Criteria:**
- Each opportunity assigned score (1-10)
- Score based on multiple factors (liquidity, volatility, whale activity, news)
- Scoring algorithm transparent and documented
- Score displayed with each opportunity

#### US-2.3: Whale Tracking
**As a** trader  
**I want to** track whale trader movements  
**So that** I can factor large trades into opportunity assessment

**Acceptance Criteria:**
- Bot identifies wallets with significant trading volume
- Tracks whale positions in relevant markets
- Whale activity factored into opportunity scoring
- Dashboard shows recent whale movements

#### US-2.4: Information Aggregation
**As a** trader  
**I want to** relevant news and data aggregated  
**So that** I can make informed decisions

**Acceptance Criteria:**
- Integration with news APIs for market-relevant information
- On-chain data analysis for market trends
- Information displayed in scanner section of dashboard
- Information freshness indicated (timestamp)

### Epic 3: Trading Execution

#### US-3.1: Flexible Equilibrage Entry
**As a** trader  
**I want to** the bot to enter positions with configurable YES/NO ratios  
**So that** I can execute customized equilibrage strategies per bet

**Acceptance Criteria:**
- Bot enters positions with configurable ratio (e.g., 50/50, 60/40, 70/30, 100/0)
- Ratio configurable per bet opportunity
- Default ratio: 50% YES / 50% NO
- Entry only when opportunity score >= configured threshold
- Respects position limits (won't exceed max concurrent positions)
- Uses configured per-bet capital allocation percentage
- Transaction confirmation before position marked active

#### US-3.2: Position Monitoring
**As a** trader  
**I want to** positions monitored for configured SL/TP thresholds  
**So that** the strategy executes correctly

**Acceptance Criteria:**
- Real-time monitoring of all active positions (every 30 seconds)
- Detects when YES or NO reaches configured stop-loss threshold
- Detects when YES or NO reaches configured take-profit threshold
- Supports single threshold (applies to both) OR separate YES/NO thresholds
- Monitoring continues until bet resolution or manual close
- Price data refreshed every 30 seconds (configurable)

#### US-3.3: Intelligent Automatic Liquidation
**As a** trader  
**I want to** losing positions automatically liquidated when thresholds are reached  
**So that** I maximize profit by selling losers and holding winners

**Acceptance Criteria:**
- When stop-loss threshold reached, bot automatically sells the losing side only
- When take-profit threshold reached, bot automatically sells the winning side only
- Opposite side held until bet resolution (or manual intervention)
- Example: 50$ YES + 50$ NO → YES rises to 70$, NO falls to 30$ → Sell NO (recover 30$), hold YES to 100$ (gain 50$)
- Liquidation executed immediately upon threshold breach
- Liquidation transaction confirmed before position updated
- Partial liquidation tracked separately in database

#### US-3.4: Manual Position Close
**As a** trader  
**I want to** manually close any active position  
**So that** I can override the bot when needed

**Acceptance Criteria:**
- Dashboard shows "Close" button for each active position
- Clicking close liquidates both YES and NO sides
- Confirmation dialog before closing
- Position removed from active list after close

### Epic 4: Dashboard & Monitoring

#### US-4.1: Capital Overview
**As a** trader  
**I want to** see my current capital and performance  
**So that** I can track profitability

**Acceptance Criteria:**
- Dashboard shows total capital (wallet balance)
- Shows capital allocated to active positions
- Shows available capital for new positions
- Shows overall P&L (profit/loss)

#### US-4.2: Active Positions Display
**As a** trader  
**I want to** see all active positions  
**So that** I can monitor current trades

**Acceptance Criteria:**
- Table/list of all active positions
- Each position shows: market name, entry time, current YES/NO prices, P&L
- Real-time updates (no manual refresh needed)
- Ability to sort/filter positions

#### US-4.3: Opportunity Table
**As a** trader  
**I want to** see detected opportunities with scores  
**So that** I can review potential trades

**Acceptance Criteria:**
- Table showing all detected opportunities
- Columns: market name, opportunity score, liquidity, whale activity
- Sorted by score (highest first)
- Indicates which opportunities meet auto-trade threshold
- Refresh button to manually trigger scan

#### US-4.4: Information Scanner
**As a** trader  
**I want to** see aggregated market information  
**So that** I can stay informed

**Acceptance Criteria:**
- Section displaying recent news/events
- Shows whale movements
- Shows market trends
- Timestamps for all information
- Scrollable/paginated for large datasets

### Epic 5: Historical Tracking

#### US-5.1: Trade History
**As a** trader  
**I want to** see all past trades  
**So that** I can analyze performance

**Acceptance Criteria:**
- Dedicated history page/tab
- Shows all closed positions
- Each entry shows: market, entry/exit times, entry/exit prices, P&L
- Filterable by date range, market, outcome
- Exportable to CSV

#### US-5.2: Performance Analytics
**As a** trader  
**I want to** see performance metrics  
**So that** I can understand strategy effectiveness

**Acceptance Criteria:**
- Win rate (% of profitable trades)
- Average P&L per trade
- Total P&L over time (chart)
- Best/worst performing markets
- Opportunity score correlation with outcomes

---

## Functional Requirements

### FR-1: Trading Strategy
- Bot must support configurable entry ratios per bet (default: 50% YES / 50% NO)
- Bot must support custom ratios (e.g., 60/40, 70/30, 100/0)
- Bot must monitor positions every 30 seconds (configurable)
- Bot must support configurable stop-loss thresholds (default: 0% = disabled)
- Bot must support configurable take-profit thresholds (default: 0% = disabled)
- Bot must support single threshold OR separate YES/NO thresholds
- Bot must liquidate only the side that reaches threshold (losing or winning)
- Bot must hold opposite side until bet resolution or manual close
- Liquidation logic: sell declining side, ride winning side to maximize profit

### FR-2: Risk Management
- Configurable stop-loss and take-profit (default: 0% = disabled)
- Option for single threshold OR separate YES/NO thresholds
- Configurable entry ratio per bet (default: 50/50)
- Configurable position limits (1-10 concurrent positions)
- Configurable per-bet capital allocation (percentage)
- All settings persist across restarts unless reset
- Manual override capability for all positions (full close)

### FR-3: Opportunity Detection
- Continuous market scanning
- Multi-factor opportunity scoring (1-10 scale)
- Whale tracking and analysis
- News and on-chain data integration

### FR-4: User Interface
- Real-time dashboard with capital, positions, opportunities
- Configuration settings page
- Historical trades page
- Information scanner display

### FR-5: Data Persistence
- All trades logged to database
- Configuration settings persisted
- Historical data retained indefinitely
- State recovery after restart

---

## Non-Functional Requirements

### Performance
- Dashboard updates within 2 seconds of state change
- Market scanning completes within 60 seconds
- Trade execution within 10 seconds of decision

### Security
- Wallet credentials encrypted at rest
- API keys stored securely
- No exposure of private keys in logs
- Secure communication with Polymarket API

### Reliability
- 99% uptime for monitoring active positions
- Automatic reconnection on network failures
- Transaction retry logic with exponential backoff
- State persistence prevents data loss

### Usability
- Intuitive configuration with sensible defaults
- Clear error messages
- Responsive design for desktop use
- No manual refresh required for dashboard

---

## Out of Scope

### Explicitly Excluded
- Paper trading / simulation mode
- Mobile application
- Multi-user support
- Advanced charting/technical analysis
- Automated strategy optimization
- Support for other prediction markets (only Polymarket)

---

## Technical Constraints

### Platform
- Polymarket API integration required
- Web-based dashboard (browser access)
- Backend service for trading logic

### Integrations
- Polymarket API for market data and trading
- News APIs for information aggregation
- On-chain data sources for whale tracking

### Data
- Database for trade history and configuration
- Real-time data streaming for price updates

---

## Dependencies

### External
- Polymarket API availability and rate limits
- Wallet/blockchain network availability
- News API availability

### Internal
- Secure wallet integration
- Database setup
- API rate limiting compliance

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| API rate limiting | High | Medium | Implement caching, request throttling |
| Network failures during trade | High | Low | Retry logic, transaction confirmation |
| Incorrect opportunity scoring | Medium | Medium | Transparent scoring, manual override |
| Wallet security breach | Critical | Low | Encryption, secure key management |
| Insufficient liquidity | Medium | Medium | Liquidity checks before entry |

---

## Assumptions

1. User has Polymarket account and wallet with funds
2. User understands equilibrage trading strategy
3. Polymarket API provides necessary data and trading capabilities
4. Markets have sufficient liquidity for strategy execution
5. User has technical capability to configure and run the bot

---

## Review & Acceptance Checklist

- [ ] All user stories have clear acceptance criteria
- [ ] Functional requirements are testable
- [ ] Non-functional requirements are measurable
- [ ] Out of scope items are explicitly listed
- [ ] Risks identified with mitigations
- [ ] Dependencies documented
- [ ] Technical constraints understood
- [ ] Success metrics defined
- [ ] Stakeholder review completed
- [ ] Ready for technical planning
