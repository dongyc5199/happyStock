# Feature Specification: AI-Enhanced Trading Simulation with User Integration

**Feature Branch**: `001-ai-user-order-matching`
**Created**: 2025-11-11
**Status**: Draft
**Input**: User description: "根据刚才你了解的情况，我准备继续打磨sim模块，需要让AI自己下单，并结合用户下单，综合进行价格撮合，把挂单深度调整为50，增加AI的目标（机构、游资目标是挣钱，散户虽然目标是挣钱但是经常处于跟风状态）"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real User Participates in AI-Driven Market (Priority: P1)

A real user (investor) logs into the simulation platform and wants to place buy/sell orders in a realistic market environment where other participants are AI agents creating authentic market dynamics.

**Why this priority**: This is the core value proposition - users need a realistic trading environment to practice. Without AI participants creating market depth and price movement, the simulation would be empty and unrealistic.

**Independent Test**: Can be fully tested by having a user place a market or limit order and observing that it gets matched against AI-generated orders with realistic price discovery, delivering a functioning trading simulation experience.

**Acceptance Scenarios**:

1. **Given** a user has logged in and selected a stock to trade, **When** they place a limit buy order at 100.50 yuan, **Then** the order appears in the order book alongside AI-generated orders and can be matched with AI sell orders at that price level
2. **Given** the market has AI traders actively placing orders, **When** a user places a market sell order for 100 shares, **Then** the order immediately matches against the best available AI buy orders and the user sees their position updated with the executed trade price
3. **Given** a user has an open limit order in the book, **When** AI traders create price movement through their trading activity, **Then** the user's order may get filled if the market price reaches their limit price
4. **Given** multiple users and AI agents are trading, **When** orders are submitted simultaneously, **Then** all orders are processed through a unified matching engine that maintains fair price-time priority for both human and AI participants

---

### User Story 2 - AI Agents with Behavioral Objectives (Priority: P1)

The simulation includes different types of AI trading agents that exhibit realistic trading behaviors: institutional traders and prop traders (proprietary trading firms) that actively seek profitable opportunities, while retail traders tend to follow market trends and momentum.

**Why this priority**: This is equally critical because realistic agent behavior creates authentic market dynamics. Without differentiated agent behaviors, the market would feel artificial and wouldn't teach users about real market psychology and dynamics.

**Independent Test**: Can be independently tested by observing AI agent trading patterns over multiple simulation ticks - institutional/prop agents should demonstrate profit-seeking strategies (arbitrage, mean reversion) while retail agents should show trend-following and herd behavior, measurable through their order patterns and timing.

**Acceptance Scenarios**:

1. **Given** the simulation is running with a stock showing upward price momentum, **When** monitoring retail agent behavior, **Then** retail agents place predominantly buy orders following the trend with smaller order sizes
2. **Given** institutional agents detect a price discrepancy or opportunity, **When** they evaluate market conditions, **Then** they place strategic orders aimed at capturing profit (e.g., buying dips, selling rallies) with larger order sizes
3. **Given** prop traders identify momentum signals, **When** market volatility increases, **Then** they adjust their trading frequency and position sizes to maximize profit while managing risk
4. **Given** retail traders observe other participants' behavior, **When** there's a surge in buying activity, **Then** retail agents exhibit herding behavior by joining the buying trend with a slight delay
5. **Given** the market reaches an equilibrium price, **When** no clear trend is visible, **Then** retail agents reduce trading activity while institutional/prop agents continue seeking arbitrage opportunities

---

### User Story 3 - Enhanced Order Book Depth (Priority: P2)

Users and system observers can view a deep order book showing up to 50 price levels on both the buy and sell sides, providing comprehensive market depth information that reflects realistic liquidity distribution.

**Why this priority**: Deep order book visibility is important for advanced traders to understand market structure, but the simulation can function with less depth initially. This enhances realism and allows users to practice reading market depth.

**Independent Test**: Can be tested by querying the order book state and verifying it displays up to 50 levels of bids and asks with aggregated quantities at each price level, delivering professional-grade market depth information.

**Acceptance Scenarios**:

1. **Given** the simulation has been running and orders have accumulated, **When** a user requests the order book for a stock, **Then** the system displays up to 50 bid levels and 50 ask levels with price and quantity information
2. **Given** multiple AI agents and users have placed limit orders at various price points, **When** the order book is displayed, **Then** orders at the same price level are aggregated showing total quantity available at each level
3. **Given** orders are being matched and filled, **When** the order book updates, **Then** filled orders are removed and the depth information reflects the current available liquidity across all 50 levels
4. **Given** most liquidity is concentrated near the current market price, **When** viewing the order book, **Then** users can see progressively thinner liquidity as price levels move further from the market price, reflecting realistic depth distribution

---

### User Story 4 - Unified Price Matching for All Participants (Priority: P1)

The matching engine processes orders from both AI agents and real users through a single, fair matching algorithm that ensures price-time priority regardless of the order source.

**Why this priority**: Fair matching is fundamental to market integrity and user trust. Users must be confident that their orders are treated fairly alongside AI orders - this is a core requirement for a credible simulation.

**Independent Test**: Can be tested by placing user orders and AI orders at the same price level with different timestamps, then verifying that order fill priority follows strict time precedence, delivering fair market access.

**Acceptance Scenarios**:

1. **Given** an AI agent places a buy limit order at 100.00 yuan at timestamp T1, **When** a user places a buy limit order at 100.00 yuan at timestamp T2, and a sell order arrives at 100.00, **Then** the AI order at T1 gets filled first due to time priority
2. **Given** orders at multiple price levels exist in the book, **When** a large market order is submitted, **Then** the matching engine fills orders starting from the best price level and proceeding to worse prices until the order is completely filled
3. **Given** partial fills are required, **When** an incoming order quantity exceeds available quantity at the best price, **Then** the engine fills what's available at that level and continues to the next price level for both AI and user orders equally
4. **Given** both AI and user orders are entering the system rapidly, **When** the matching engine processes them, **Then** all orders maintain their submission timestamp integrity and matching follows strict price-time priority without bias

---

### Edge Cases

- What happens when a user places an order size that exceeds the combined depth of all 50 levels in the order book?
- How does the system handle a scenario where AI agents dominate one side of the market (e.g., all AI agents want to sell), leaving no counterparty for user orders?
- What occurs when retail AI agents exhibit extreme herding behavior and all try to execute orders at the same time, potentially creating unrealistic volatility?
- How does the matching engine handle orders when the simulation is paused or restarted mid-tick?
- What happens to pending limit orders from both users and AI agents when a simulation session ends?
- How does the system ensure AI trading behavior doesn't inadvertently disadvantage real users (e.g., AI front-running or predatory trading)?
- What happens when institutional AI agents have accumulated very large positions and need to unwind them - could this create unrealistic market impact?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow real users to place market and limit orders (buy/sell) that are submitted to the same matching engine as AI-generated orders
- **FR-002**: System MUST include AI trading agents representing at least three behavioral categories: institutional traders, proprietary traders (prop/游资), and retail traders
- **FR-003**: Institutional and prop AI agents MUST implement profit-seeking strategies that analyze market conditions and place orders intended to capture trading opportunities
- **FR-004**: Retail AI agents MUST implement trend-following and herding behaviors that react to recent price movements and other participants' trading activity with a behavioral bias toward joining momentum
- **FR-005**: System MUST maintain an order book supporting up to 50 price levels on both bid and ask sides
- **FR-006**: System MUST aggregate order quantities at each price level when displaying market depth information
- **FR-007**: Matching engine MUST process all orders (user and AI) through a unified algorithm that maintains strict price-time priority
- **FR-008**: System MUST ensure that orders submitted earlier at the same price level are filled before orders submitted later, regardless of whether they originated from AI or human users
- **FR-009**: System MUST update order book depth in real-time as orders are placed, matched, and filled
- **FR-010**: System MUST prevent AI agents from accessing information or advantages not available to real users (fair information access)
- **FR-011**: AI agent trading objectives MUST be configurable to allow adjustment of their profit targets, risk tolerance, and behavioral parameters
- **FR-012**: System MUST track and expose each AI agent's trading performance (P&L, win rate, positions) for simulation transparency
- **FR-013**: Retail AI agents MUST demonstrate measurably different behavior patterns from institutional/prop agents in terms of order timing, size distribution, and reaction to market events
- **FR-014**: System MUST handle scenarios where order book depth approaches or reaches the 50-level limit by maintaining only the best 50 levels and rejecting or queuing orders beyond that depth
- **FR-015**: System MUST provide users with visibility into the order book depth showing all available price levels up to 50

### Key Entities

- **User Order**: Represents a buy or sell order placed by a real human user, including side (buy/sell), type (market/limit), quantity, price (for limit orders), timestamp, and user identifier
- **AI Agent Order**: Represents a buy or sell order generated by an AI trading agent, structurally identical to user orders but tagged with agent type (institutional, prop, retail) and agent identifier
- **Order Book**: Aggregated view of all active limit orders organized by price level, showing up to 50 bid levels and 50 ask levels with total quantities at each level
- **AI Agent Profile**: Configuration defining an AI agent's behavioral category (institutional/prop/retail), trading objectives (profit target, risk parameters), strategy parameters (momentum sensitivity, herd behavior strength), and performance metrics
- **Trade Execution**: Record of a matched trade including buyer order, seller order, execution price, quantity, timestamp, and participant types (user or AI agent type)
- **Market State**: Current snapshot of market conditions including last price, volume, order book depth, and recent price movement that AI agents analyze to make trading decisions

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can place orders that execute against AI-generated orders with realistic price discovery, with 95% of market orders filling within 1 second
- **SC-002**: Order book displays up to 50 bid and ask levels with accurate aggregated quantities, refreshing within 500 milliseconds of order book changes
- **SC-003**: AI institutional and prop agents demonstrate profit-seeking behavior with at least 55% of their trades resulting in profitable outcomes over a simulation session
- **SC-004**: AI retail agents exhibit measurable trend-following behavior with order timing correlation coefficient of at least 0.6 with recent price momentum
- **SC-005**: Matching engine processes at least 1,000 combined user and AI orders per second while maintaining price-time priority fairness
- **SC-006**: Users report increased perception of market realism compared to previous AI-less simulation, with satisfaction scores improving by at least 30%
- **SC-007**: Order book depth distribution shows realistic liquidity profile with 70% of liquidity concentrated in the nearest 10 levels from current market price
- **SC-008**: No measurable bias exists in fill rates or execution quality between user orders and AI orders at the same price-time priority (verified through statistical testing)
- **SC-009**: Retail AI agents demonstrate herding behavior with at least 60% of their orders placed in the direction of the prevailing 5-minute trend
- **SC-010**: Simulation runs continuously for at least 8 hours with AI agents and user orders without performance degradation or matching errors

## Assumptions

- Users have basic understanding of market orders, limit orders, and order book concepts
- The simulation operates in discrete time intervals (ticks) as per the existing sim module architecture
- AI agents have access to the same market data (order book, recent trades, prices) that would be available to real users
- The existing sim module infrastructure (matching engine, repositories, services) can be extended to accommodate the enhanced order book depth and AI agent integration
- Users understand this is a simulated environment and AI agent behavior is modeled rather than representing real institutional/retail trader strategies
- The system will use reasonable default parameters for AI agent behavior that can be tuned based on observed market dynamics
- Order book depth of 50 levels is sufficient for realistic simulation - deeper books would not significantly enhance user experience
- The feature targets the Chinese market context where 游资 (prop/speculative traders) are a recognized market participant category distinct from institutional investors

## Dependencies

- Existing sim module matching engine (backend/sim/engine.py) must be evaluated for order book depth capacity
- AI agent framework (backend/sim/agents/) requires enhancement to implement profit-seeking and trend-following behavioral models
- Feature service (backend/sim/feature_service.py) may need to provide additional market signals for AI agents to analyze
- Order book data structure and APIs must be capable of efficiently storing and querying 50 levels of depth
- Real-time order book updates require efficient data propagation mechanism (likely WebSocket) to frontend clients
- User authentication and session management must be integrated to distinguish user orders from AI orders

## Out of Scope

- Integration with real market data feeds or real trading APIs - this remains a pure simulation
- Machine learning-based AI agent strategies - initial implementation will use rule-based behavioral models
- Backtesting historical market scenarios with AI agents
- Multi-asset trading - feature focuses on single-stock simulation
- Advanced order types beyond market and limit orders (stop-loss, iceberg, etc.)
- Cross-session persistence of AI agent learning or strategy adaptation
- Portfolio-level risk management for AI agents across multiple stocks
- Regulatory compliance features (trading halts, price limits) - assumes simplified market rules
