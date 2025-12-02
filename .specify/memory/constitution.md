# Polymarket Equilibrage Bot - Project Constitution

## Core Principles

### 1. Trading Safety & Risk Management
- **Capital Protection First**: All trading operations must include configurable stop-loss and take-profit mechanisms
- **Position Limits**: Strict enforcement of maximum concurrent positions (1-10 configurable)
- **Capital Allocation**: Per-bet capital allocation must be percentage-based and user-configurable
- **Manual Override**: Users must always be able to manually close positions
- **No Paper Trading**: All operations are live trading only - test thoroughly before deployment

### 2. Code Quality & Architecture
- **Modularity**: Separate concerns into distinct modules (scanner, trading engine, dashboard, configuration)
- **Type Safety**: Use TypeScript for frontend and Python type hints for backend
- **Error Handling**: Comprehensive error handling with detailed logging
- **Testing**: Unit tests for core logic, integration tests for API interactions
- **Documentation**: Clear inline documentation and API documentation

### 3. User Experience
- **Real-time Updates**: Dashboard must reflect current state without manual refresh
- **Transparency**: All bot decisions (opportunity scores, trades) must be visible and explainable
- **Configuration Clarity**: Settings must be intuitive with sensible defaults
- **Historical Tracking**: Complete audit trail of all trades and decisions
- **Performance Metrics**: Clear display of capital, active positions, and performance

### 4. Data & Intelligence
- **Multi-source Analysis**: Integrate multiple data sources (whale tracking, news, on-chain data)
- **Opportunity Scoring**: Transparent 1-10 scoring system for bet opportunities
- **Configurable Thresholds**: User-defined minimum opportunity score for auto-trading
- **Information Scanner**: Aggregate and display relevant market information
- **Whale Detection**: Track and analyze large trader movements

### 5. Technical Standards
- **API-First Design**: RESTful API for all bot operations
- **Wallet Security**: Secure wallet integration with private key management
- **Rate Limiting**: Respect Polymarket API rate limits
- **State Management**: Persistent state across restarts
- **Scalability**: Design for handling multiple concurrent positions efficiently

### 6. Development Workflow
- **Spec-Driven**: Follow Spec Kit methodology for all features
- **Version Control**: Git-based workflow with feature branches
- **Incremental Delivery**: Build and test features incrementally
- **Code Review**: All changes reviewed before merge
- **Deployment Safety**: Staging environment testing before production

## Governance

### Decision-Making Framework
When making technical decisions, prioritize in this order:
1. **Safety**: Does this protect user capital and prevent losses?
2. **Reliability**: Will this work consistently under various market conditions?
3. **Transparency**: Can users understand what the bot is doing and why?
4. **Performance**: Does this execute efficiently without unnecessary overhead?
5. **Maintainability**: Can this be easily updated and debugged?

### Trade-offs
- **Speed vs Safety**: Always choose safety over execution speed
- **Automation vs Control**: Provide automation with manual override capabilities
- **Complexity vs Clarity**: Prefer simple, understandable solutions over complex optimizations
- **Features vs Stability**: Prioritize stable core functionality over feature breadth

## Non-Negotiables
1. No trading without explicit user wallet configuration
2. No position taking beyond configured limits
3. No silent failures - all errors must be logged and visible
4. No data loss - all trades and decisions must be persisted
5. No security shortcuts - proper authentication and authorization always
