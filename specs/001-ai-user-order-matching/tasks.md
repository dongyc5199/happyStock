# Tasks: AI-Enhanced Trading Simulation with User Integration

**Input**: Design documents from `/specs/001-ai-user-order-matching/`
**Prerequisites**: plan.md -> spec.md -> research.md -> data-model.md -> contracts/

**Tests**: Covered by the feature spec; follow the described unit, integration, and performance suites.

**Organization**: Tasks are grouped by user story so each story can be delivered and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can be executed in parallel (different files, no dependency).
- **[Story]**: User story (US1, US2, US3, US4).
- Every task lists the exact file path.

## Path Conventions

**Backend**: `backend/sim/`, `backend/routers/`, `backend/tests/`
**Frontend**: `frontend/src/` (not part of this feature)
**DB migrations**: `backend/sim/migrations/`

---

## Phase 1: Setup (shared infrastructure)

**Goal**: project bootstrap and dependency hygiene.

- [x] T001 Validate Python 3.13 and Pipenv environment
- [x] T002 [P] Add new dependencies (if any) to `backend/Pipfile`
- [x] T003 [P] Create `backend/sim/migrations/` if it does not exist
- [x] T004 Create `backend/pytest.ini` if missing (pytest config)

**Checkpoint**: baseline environment ready.

---

## Phase 2: Foundational (blocking prerequisites)

**Goal**: core infrastructure required before any user story work.

**WARNING Critical**: do not start user-story work until this phase is done.

### Database migrations

- [x] T005 Create `backend/sim/migrations/0004_user_orders.sql` (UserOrder table)
- [x] T006 Create `backend/sim/migrations/0005_agent_behavior_params.sql` (AI behavior params)
- [x] T007 Create `backend/sim/migrations/0006_trade_participant_types.sql` (trade participant types)
- [x] T008 Run migration scripts and verify schema (use `run_migrations.sh` / `.ps1`)

### Core data models

- [x] T009 [P] In `backend/sim/types.py` add `UserOrder` dataclass
- [x] T010 [P] In `backend/sim/types.py` add `OrderStatus` enum (supports PENDING)
- [x] T011 [P] In `backend/sim/schemas.py` add `OrderRequest` Pydantic model
- [x] T012 [P] In `backend/sim/schemas.py` add `OrderAcceptedResponse` model

### Price mechanism validation

- [x] T013a [P] Confirm `backend/sim/` no longer uses `PriceGenerator`
- [x] T013b [P] Confirm `backend/sim/services.py` fetches price from trades (`trades[-1].price`)
- [x] T013c Update `backend/sim/services.py` to use session `initial_price` instead of hard-coded `100.0`
- [x] T013d Update `backend/sim/auto_runner.py` so SimulationAutoRunner accepts configurable `bootstrap_price`
- [x] T013e [P] Document the price mechanism in `specs/001-ai-user-order-matching/docs/price-mechanism.md`

### Order book depth expansion

- [x] T014 Update `backend/sim/engine.py` OrderBook with `max_depth` argument (default 50)
- [x] T015 Update OrderBook `_add_to_book()` with depth limiting logic
- [x] T016 Add `get_depth_snapshot()` to OrderBook returning aggregated levels

### Repository layer

- [x] T017 In `backend/sim/repositories.py` add `UserOrderRepository`
- [x] T018 Implement `UserOrderRepository.create_order()`
- [x] T019 Implement `UserOrderRepository.get_order()`
- [x] T020 Implement `UserOrderRepository.list_orders()`
- [x] T021 Implement `UserOrderRepository.update_order_status()`
- [x] T022 Implement `UserOrderRepository.cancel_order()`
- [x] T023 [P] Implement `SimulationRepository.batch_create_participants()` (performance)
- [x] T024 [P] Extend `MarketStateRepository` to persist buyer_type / seller_type

### Redis cache extensions

- [x] T025 In `backend/sim/cache.py` add `push_pending_user_order()`
- [x] T026 Add `pop_pending_user_orders()`
- [x] T027 [P] Add `cache_orderbook_snapshot()`

**Checkpoint**: infrastructure ready, user stories can proceed in parallel.

---

## Phase 3: User Story 4 - Unified Price Matching (Priority: P1)

**Goal**: unify matching so AI and user orders share the same price/time priority.

**Independent test**: submit AI and user orders at the same price with different timestamps; ensure FIFO across sources.

### Matching logic

- [x] T028 [US4] In `backend/sim/services.py` read pending user orders at the start of `execute_tick()`
- [x] T029 [US4] Merge AI and user orders and sort by timestamp before submission
- [x] T030 [US4] In `backend/sim/engine.py` add `timestamp` (int64 ns) to `Order`
- [x] T031 [US4] Ensure every order sent to MatchingEngine has a valid timestamp
- [x] T032 [US4] After fills, update UserOrder `filled_quantity` and `status`

### Unit tests

- [x] T033 [P][US4] Add `backend/tests/unit/test_unified_matching.py`
- [x] T034 [P][US4] Test: AI order at T1, user order at T2, AI fills first
- [x] T035 [P][US4] Test: large order crossing multiple levels
- [x] T036 [P][US4] Test: partial fill scenarios
- [x] T037 [P][US4] Test: concurrent orders preserve timestamps

**Completion**: AI and user orders are treated fairly inside the same engine.

---

## Phase 4: User Story 1 - Real User Trading (Priority: P1)

**Goal**: allow users to submit orders and trade against AI participants.

**Independent test**: user joins a session, submits a market/limit order, sees it matched against AI orders, and queries the result.

### API endpoints

- [x] T038 [US1] Add `POST /api/sim/sessions/{session_id}/orders`
- [x] T039 [US1] Implement validation (balance, price band, quantity)
- [x] T040 [US1] Generate nanosecond timestamps and push into Redis queues
- [x] T041 [US1] Add `GET /api/sim/sessions/{session_id}/orders/{order_id}`
- [x] T042 [US1] Add `GET /api/sim/sessions/{session_id}/orders` (list)
- [x] T043 [US1] Add `DELETE /api/sim/sessions/{session_id}/orders/{order_id}` (cancel)
- [x] T044 [P][US1] Add `GET /api/sim/sessions/{session_id}/orderbook`

### User account management

- [x] T045 [US1] Add `POST /api/sim/sessions/{session_id}/join`
- [x] T046 [US1] In SimulationService add `join_session()`

### Integration tests

- [x] T047 [P][US1] Add `backend/tests/integration/test_user_orders_api.py`
- [x] T048 [P][US1] Test: limit buy returns 202
- [x] T049 [P][US1] Test: market sell queued for next tick
- [x] T050 [P][US1] Test: status transitions PENDING -> NEW -> FILLED
- [x] T051 [P][US1] Test: cancel partially filled order
- [x] T052 [P][US1] Test: end-to-end order lifecycle

### Error handling

- [x] T053 [P][US1] Insufficient funds -> 400
- [x] T054 [P][US1] Price out of band -> 400
- [x] T055 [P][US1] Session not found -> 404
- [x] T056 [P][US1] Rate limiting -> 429

**Completion**: users can trade via API, match against AI, and inspect results.

---

## Phase 5: User Story 2 - AI Behavioral Objectives (Priority: P1)

**Goal**: AI agents exhibit differentiated behavior (institutional, prop, retail).

**Independent test**: run 100 ticks without users; verify retail correlation >=0.6 and prop/institutional win rates >=55%.

### Retail agent enhancements

- [x] T057 [US2] `backend/sim/agents/retail.py`: add `herd_delay_ticks`
- [x] T058 [US2] Add `herd_trigger_volume`
- [x] T059 [US2] Add `panic_multiplier` controls
- [x] T060 [US2] Trigger herd behavior based on last tick volume
- [x] T061 [US2] Release delayed orders via `_pending_orders`
- [x] T062 [US2] Increase/dynamically adjust `follow_chance`

### Prop agent enhancements

- [x] T063 [US2] `backend/sim/agents/prop.py`: add `profit_target`
- [x] T064 [US2] Add `stop_loss`
- [x] T065 [US2] Track position cost per session
- [x] T066 [US2] Close orders when profit target reached
- [x] T067 [US2] Trigger stop-loss logic

### Institutional agent enhancements

- [x] T068 [US2] `backend/sim/agents/institutional.py`: add `mean_reversion_window`
- [x] T069 [US2] Add `rebalance_threshold`
- [x] T070 [US2] Add `max_order_size` and split order controls
- [x] T071 [US2] Implement mean-reversion triggers
- [x] T072 [US2] Implement TWAP-style splits

### Behavior persistence

- [x] T073 [US2] Extend `SimulationRepository.update_participant()`
- [x] T074 [US2] Add `update_avg_position_cost()`

### Agent management APIs

- [x] T075 [P][US2] `GET /api/sim/sessions/{session_id}/agents`
- [x] T076 [P][US2] `GET /api/sim/sessions/{session_id}/agents/{agent_id}`
- [x] T077 [P][US2] `PUT /api/sim/sessions/{session_id}/agents/{agent_id}/config`
- [x] T078 [P][US2] `GET /api/sim/sessions/{session_id}/agents/{agent_id}/performance`
- [x] T079 [P][US2] `GET /api/sim/sessions/{session_id}/pools`
- [x] T080 [P][US2] `GET /api/sim/sessions/{session_id}/pools/{pool_code}/stats`

### Behavior validation tests

- [x] T081 [P][US2] Add `backend/tests/integration/test_ai_behavior.py`
- [x] T082 [P][US2] Test: retail agents follow trends when >60% of flow goes one way
- [x] T083 [P][US2] Test: herd delay of >=2 ticks
- [x] T084 [P][US2] Test: prop agents hit profit target at +3%
- [x] T085 [P][US2] Test: prop agents stop-loss at -1.5%
- [x] T086 [P][US2] Test: institutional agents rebalance when deviation >2%
- [x] T087 [P][US2] Test: institutional orders respect `max_order_size`

### Performance statistics

- [x] T088 [P][US2] SimulationService: add `calculate_agent_performance()`
- [x] T089 [P][US2] Record total trades, win rate, PnL, avg trade size

**Completion**: retail correlation >=0.6, prop/institutional win rate >=55%.

---

## Phase 6: User Story 3 - 50-Level Order Book (Priority: P2)

**Goal**: expose 50-level depth via API.

**Independent test**: calling the order book API returns up to 50 bid/ask levels with aggregated quantities.

### Order book services

- [x] T090 [US3] SimulationService exposes `get_orderbook_snapshot()`
- [x] T091 [US3] SimulationService implements Redis caching (5s TTL)
- [x] T092 [US3] SimulationCache adds `get_cached_orderbook()`

### Depth unit tests

- [x] T093 [P][US3] Add `backend/tests/unit/test_orderbook_depth.py`
- [x] T094 [P][US3] Ensure only top 50 levels are returned
- [x] T095 [P][US3] Aggregate orders at the same price
- [x] T096 [P][US3] Remove price levels after fills
- [x] T097 [P][US3] Validate >=70% liquidity in the top 10 levels

### Order book API tests

- [x] T098 [P][US3] Add `backend/tests/integration/test_orderbook_api.py`
- [x] T099 [P][US3] Verify response format
- [x] T100 [P][US3] Verify `depth` parameter enforcement
- [x] T101 [P][US3] Verify cache effectiveness within 5s

**Completion**: `/orderbook` returns 50 levels with <500 ms latency.

---

## Phase 7: Integration & Performance

**Goal**: validate combined scenarios and hit latency targets.

### End-to-end integration

- [x] T102 Add `backend/tests/integration/test_full_simulation.py`
- [x] T103 Test: session creation -> user join -> AI + user trading -> queries
- [x] T104 Test: multiple users submit concurrently
- [x] T105 Test: AI stability over long runs (100+ ticks)
- [x] T106 Test: order book accuracy under high-frequency trading

### Performance benchmarks

- [x] T107 Add `backend/tests/performance/test_sim_performance.py`
- [x] T108 Benchmark ~1,000 orders/sec (AI 800 + user 200)
- [x] T109 P95 order processing latency <1s
- [x] T110 Order book query latency <500 ms
- [x] T111 Tick execution P95 <800 ms

### Performance tuning (if benchmarks fail)

- [x] T112 Implement bulk participant registration
- [x] T113 Investigate `update_tick` slow query (EXPLAIN ANALYZE)
- [x] T114 Optimize order book queries / indexes
- [x] T115 Tune Redis connection pool

### Boundary tests

- [x] T116 Order volume beyond 50 levels drops worst levels
- [x] T117 One-sided AI market still lets queued user orders match
- [x] T118 Extreme herd behavior (all retail agents submit together)
- [x] T119 Orders queued during pause/restart are processed correctly
- [x] T120 Open orders are cleared when session ends
- [x] T121 Detect AI front-running to protect fairness

---

## Phase 8: Polish & Documentation

**Goal**: observability, documentation, final UX polish.

### Logging & monitoring

- [ ] T122 [P] Add structured logs in `backend/sim/services.py`
- [ ] T123 [P] Add Prometheus metrics in `backend/sim/services.py`
- [ ] T124 [P] Add API access logging in `backend/routers/simulate.py`

### Error handling

- [ ] T125 [P] Standardize error responses (ErrorResponse schema)
- [ ] T126 [P] Add global exception handler in `backend/main.py`
- [ ] T127 [P] Document error examples for every API endpoint

### Documentation

- [ ] T128 [P] Update `backend/README.md` with user order API usage
- [ ] T129 [P] Create `doc/sim/feature_service_strategy.md`
- [ ] T130 [P] Update `doc/sim/pending_tasks.md`
- [ ] T131 [P] Generate/verify Swagger docs

### WebSocket push (optional)

- [x] T132 Add WebSocket endpoint in `backend/routers/simulate.py`
- [x] T133 Push real-time user order fill notifications
- [x] T134 Push live order book updates
- [x] T135 Test WebSocket subscriptions and message structure

---

## Dependencies & Execution Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) - must finish before user stories
    ↓
    ├─ Phase 3 (US4) - matching foundation
    │     ↓
    │   Phase 4 (US1)
    │     ↓
    └─ Phase 5 (US2)
          ↓
      Phase 6 (US3)
          ↓
      Phase 7 (Integration & Performance)
          ↓
      Phase 8 (Polish)
```

**Critical path**: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 7 -> Phase 8 (~18-22 working days).

**Parallel opportunities**:
- Phase 2 buckets: (T009-T012) || (T013a-T013e) || (T014-T016) || (T017-T024) || (T025-T027)
- Phase 4 (US1) can run alongside Phase 5 (US2)
- Phase 6 testing: T093-T097 vs T098-T101
- Phase 8 tasks are fully parallel

---

## Independent Test Criteria

### US4 - Unified Matching
1. Start a clean session
2. Submit AI order at T1
3. Submit user order at T2 at the same price
4. Trigger matching
5. Verify earlier timestamp fills first

### US1 - Real User Trading
1. User submits a limit order
2. Wait for next tick
3. Query order status (FILLED or PARTIAL)
4. Verify cash/position updates

### US2 - AI Behavioral Objectives
1. Run 100 ticks without users
2. Measure retail correlation vs. price trend
3. Measure prop/institutional profitability (both >=55%)

### US3 - Order Book Depth
1. Run simulation to build depth
2. Call GET `/orderbook`
3. Ensure up to 50 levels per side
4. Verify aggregated quantities
5. Latency <500 ms

---

## Implementation Strategy

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US4) + Phase 4 (US1)

- MVP deliverables: user submission, fair matching, fill queries, basic order book endpoint.
- Estimated MVP time: ~10-12 working days.

**Incremental delivery**:
1. Iteration 1 (10-12 days): US4 + US1
2. Iteration 2 (+6-8 days): US2
3. Iteration 3 (+4-5 days): US3 + system integration
4. Total: 20-25 working days overall

---

## Task Summary

- Total tasks: 135
- Phase breakdown: 4 / 23 / 10 / 19 / 33 / 12 / 20 / 14
- Parallelizable: ~60 tasks ([P])
- Critical path: ~74 sequential tasks

**Estimated effort**:
- Single engineer: 20-25 working days
- Two engineers: 12-15 working days
- Three engineers: 8-10 working days

---

## Format Validation

- [x] All tasks use checklist syntax
- [x] IDs follow `T###`
- [x] `[P]` indicates parallel work
- [x] Story tags `[US#]` match the spec
- [x] File paths are explicit
- [x] Descriptions are actionable

**Organization checks**:
- [x] Grouped by user story / phase
- [x] Each story has independent test criteria
- [x] Dependencies are documented
- [x] MVP scope is clear

---

**Status**: Task document generated and verified
**Next step**: run `/speckit.implement` or execute phases manually
