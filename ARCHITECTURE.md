# Fantasy Dominator Architecture

## Data Sources & Information Hierarchy

### 1. **ESPN API** — Real-Time League Intelligence
**Certainty Grade: 8/10** *(Official source, minor delay in injury updates)*

#### Available Data
- League metadata (teams, rosters, scoring settings)
- Current season injury statuses (ACTIVE, QUESTIONABLE, OUT, IR, PUP)
- Week-to-week player matchups & opponent strength
- Projected points & ownership %
- Live-draft tracking (pick order, selections in real-time)

#### What We Pull
- `espn_ownership` — league-wide ownership % (used to identify available talent)
- `espn_proj` — ESPN's own weekly projection (for comparative analysis)
- Current injury status from official NFL reports
- Opponent strength metrics for weekly projections

**Why 8/10:** Official source but inherits delays from NFL reporting timelines. Injury data sometimes lags 24-48 hours behind practice reports.

---

### 2. **Sleeper API** — Transaction Detection & Roster State
**Certainty Grade: 9/10** *(Real-time roster state, industry standard)*

#### Available Data
- Roster snapshots (which players on which rosters)
- Transaction history (trades, free agent pickups, drops)
- Player availability detection (`team=null` indicates cut/waived)
- Bye weeks by team
- Keeper league eligibility rules

#### What We Pull
- Current roster composition (who owns which player)
- **Cut/Waived detection:** Players with `team=null` are flagged as CUT status
- Trade detection for real-time roster reshuffling
- Bye week calendar for schedule compatibility checks

**Why 9/10:** Gold standard for current roster state. Sleeper owns the source of truth for "who is available." Only potential issue: if a player is officially cut but Sleeper's sync hasn't updated yet (rare, <1 hour lag).

---

### 3. **Injury Database** — Real-Time Status & Severity (Synced from Sources)
**Certainty Grade: 9/10** *(Pulled from ESPN, calculated from injury type)*

#### Available Data
- Current injury status (ACTIVE, QUESTIONABLE, DOUBTFUL, OUT, IR, PUP, SUSPENDED, CUT)
- Injury type/body part (Hamstring, Calf, Knee, Illness, etc.)
- Return timeline from ESPN (Day-to-day, Weeks 1-4, etc.)
- Discount factor **calculated** from injury type + status combination

#### What We Pull (Real-Time)
- `status` — From ESPN API (QUESTIONABLE, OUT, IR, etc.) OR Sleeper API (team=null → CUT)
- `body_part` — From ESPN API (Hamstring, Calf, Illness, etc.)
- `timeline` — From ESPN API (Day-to-day, Weeks 1-4, etc.)
- `discount_factor` — **CALCULATED** based on body_part + status, NOT hardcoded

#### Data Flow
```
ESPN API Sync (hourly/on-refresh):
  └─ Pulls player status + body_part + timeline
      └─ Database updates: injury_record[player_id]
          └─ Discount factor calculated from injury type
              └─ App displays current state

Sleeper API Sync (hourly/on-refresh):
  └─ Detects team=null (cut players)
      └─ Database updates: status = CUT, discount = 0.0
```

#### Calculation Rules (No Hardcoding)
```
IF body_part contains ["hamstring", "calf", "groin", "quad"]:
  discount_factor = 0.88  (12% hit)
ELSE IF body_part contains ["ankle", "foot", "toe"]:
  discount_factor = 0.90  (10% hit)
ELSE IF body_part contains ["knee", "shoulder", "ribs"]:
  discount_factor = 0.92  (8% hit)
ELSE IF body_part contains ["illness", "rest", "maintenance", "precaution"]:
  discount_factor = 0.95  (5% hit)
ELSE IF status in ["OUT", "IR", "PUP"]:
  discount_factor = 0.0   (100% unavailable)
ELSE IF status == "SUSPENDED" OR status == "CUT":
  discount_factor = 0.0   (100% unavailable)
ELSE IF status == "DOUBTFUL":
  discount_factor = 0.40  (60% hit)
ELSE:  // QUESTIONABLE or unknown
  discount_factor = 0.90  (default 10% hit)
```

**Why 9/10:** Pure API-sourced data. Only limitation: ESPN sometimes lacks detailed body-part info, forcing us to use status-only fallback.

---

### 4. **INITIAL_PLAYERS** — Base Player Pool (Static, No Injury Data)
**Certainty Grade: 7/10** *(Preseason roster data, updated seasonally)*

#### Available Data
- ADP (Average Draft Position) from major platforms
- Positional tier assignments
- Archetype classifications
- Base offense metrics (Vegas line, bye week)
- ADP-ranked starting player pool (1019 top prospects)

#### What We Store (NO Injury Data)
- `adp` — Where player is being drafted across platforms
- `tier` — Draft priority tier (1-5, where Tier 1 = elite studs)
- `position`, `team` — Position & NFL team
- `projected_season`, `projected_week` — PPR projections (starting estimates)
- `bye_week` — Team bye week (static)
- `archetype` — Role description ("Elite PPR Weapon", "Red Zone Specialist", etc.)
- Vegas environment: `implied_team_pts`, `spread`, `wind_mph`, `is_dome`

#### What We DO NOT Store
- ❌ `injury_status` — pulled live from ESPN/Sleeper
- ❌ `injury_type` — pulled live from ESPN
- ❌ `injury_timeline` — pulled live from ESPN
- ❌ `injury_notes` — pulled live from ESPN
- ❌ `discount_factor` — calculated from live injury data

**Why 7/10:** Preseason ADP/tiers get stale as season progresses. Used as baseline only; live APIs override. Injury data ONLY comes from real-time sources.

---

### 5. **Advanced Metrics** — Granular Role Analysis
**Certainty Grade: 8/10** *(Statsbomb/NGS sourced, league-wide consensus)*

#### Available Data
- Route participation % (volume reliability)
- High-value touches (red zone + target depth)
- Red zone opportunity share
- Expected fantasy points (xFP) via play-by-play simulation
- PROE (Points Over Expected) — luck-adjusted efficiency
- Target share & route participation by team

#### What We Pull
- `route_participation` — % of team passing plays (0.0-1.0)
- `high_value_touches` — Avg red zone touches + deep targets per game
- `red_zone_share` — % of team RZ opportunities
- `xfp` — Expected fantasy points per game (simulated)
- `target_share`, `proe` — Target rate & touchdown regression

**Why 8/10:** Derived from official play-by-play data (NGS) but filtered through third-party providers. Highly predictive but subject to model assumptions.

---

## Data Sync Flow (Zero Hardcoding)

```
┌─────────────────────────────────────────────────────────────┐
│         /refresh/teams-and-players Endpoint (User Click)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌──────────────┐        ┌──────────────┐
    │   ESPN API   │        │  Sleeper API │
    │   Pulls:     │        │   Pulls:     │
    │ • Status     │        │ • Rosters    │
    │ • Body Part  │        │ • Cuts       │
    │ • Timeline   │        │ • Trades     │
    └────┬─────────┘        └────┬─────────┘
         │                       │
         ▼                       ▼
    ┌──────────────────────────────────┐
    │  Database: injury_records        │
    │  ────────────────────────────    │
    │  player_id, status, body_part,   │
    │  timeline, last_updated_at       │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │  Calculate Discount Factor       │
    │  ────────────────────────────    │
    │  IF body_part = "hamstring"      │
    │    THEN factor = 0.88            │
    │  ELSE IF status = "OUT"          │
    │    THEN factor = 0.0             │
    │  (etc — no hardcoding)           │
    └────┬─────────────────────────────┘
         │
         ▼
    ┌──────────────────────────────────┐
    │  Player Board + Discounts        │
    │  Ready for Display               │
    └──────────────────────────────────┘
```

**Key Principle:** Every data point (status, injury type, timeline) originates from ESPN or Sleeper. Nothing is hardcoded. Discount factors are **calculated** from injury patterns, not manually assigned.

**Data Freshness:**
- ESPN sync: On `/refresh` click (captures current status + body part)
- Sleeper sync: On `/refresh` click (captures cuts, trades, team changes)
- Discount calculation: Real-time when board is generated
- Database: Single source of truth for all player injury state

---

## Player Value Calculation

### Overview
Player value is calculated using a **Dynamic VORP (Value Over Replacement Player)** system that combines:
1. **Context-Adjusted Projections** (2025 metrics adjusted for QB/OC changes)
2. **Baseline Comparisons** (position-specific replacement level)
3. **Injury Discounting** (availability & role uncertainty)
4. **Roster Context** (what positions your team still needs)
5. **Bye Week Collision Protection** (schedule compatibility)

---

### Step 1: Position Replacement Baseline

For each position, we establish a "replacement threshold" based on typical 10-team PPR roster construction:

| Position | Starter Count | Baseline Rank |
|----------|---------------|---------------|
| QB       | 10            | 10th-ranked QB |
| RB       | 25            | 25th-ranked RB |
| WR       | 25            | 25th-ranked WR |
| TE       | 10            | 10th-ranked TE |
| K        | 10            | 10th-ranked K  |
| DEF      | 10            | 10th-ranked DEF|

**Formula:**
```
replacement_points[pos] = projected_season of player ranked at position_baseline
```

**Example:** If 25th-ranked WR has 270 season PPR points, replacement_points["WR"] = 270.

---

### Step 2: Raw VORP Calculation

```
VORP = projected_season - replacement_points[position]
VORP_per_week = VORP / 16.0
```

**Example:**
- Player: Tyreek Hill (projected_season = 280)
- Position: WR, replacement_points = 270
- VORP = 280 - 270 = +10 points
- VORP_per_week = 10 / 16 = +0.625 pts/week above the 25th-ranked WR

---

### Step 3: Context Certainty Factor (Historical Metric Adjustment)

**Problem:** Historical metrics (2025 stats) assume environment is stable. If a player's QB changed, their route participation may not transfer.

**Solution:** Apply context certainty factor to all 2025-derived metrics.

#### Context Stability Scoring

```
Context Certainty = base score from continuity checks

Scoring:
├─ QB same (2025 → 2026)? → +0.30 (highest weight)
├─ OC (Offensive Coordinator) same? → +0.20
├─ HC (Head Coach) same? → +0.20
├─ Key supporting cast same? → +0.15
└─ Same offensive role/target distribution? → +0.15
    = Combined certainty (0.0-1.0, minimum floor 0.40)
```

#### Examples

| Scenario | QB | OC | HC | Certainty | Impact |
|----------|----|----|----|-----------|----|
| Njigba (no change) | ✅ | ✅ | ✅ | 1.0 | Use 16.0 xFP as-is |
| Jefferson (QB only) | ❌ | ✅ | ✅ | 0.70 | Adjust 17.0 xFP → 11.9 (70% weight) |
| Player (major overhaul) | ❌ | ❌ | ✅ | 0.50 | Adjust 15.0 xFP → 7.5 (50% weight) |
| Rookie (no history) | N/A | N/A | N/A | 0.40 | Fall back to preseason projections |

#### Three-Column Display

For each historical metric, show:

```
Metric Name:
  Projected (2025):    17.0 xFP/gm
  Context Factor:      0.7 ⚠️ (QB changed)
  Recalculated (2026): 11.9 xFP/gm
```

**Where Recalculated Value is Used:**
- VORP calculation (replaces projected value)
- Positional ranking
- Draft board sorting

**Where Projected Value is Kept:**
- Transparency (shows historical baseline)
- Manual override (user can adjust factor)
- Audit trail (source of 2025 data)

#### Metrics Subject to Context Certainty

All 2025-derived statistics are adjusted:
- `xfp` — Expected Fantasy Points per game
- `route_participation` — % of team passing plays
- `high_value_touches` — Red zone + deep targets per game
- `red_zone_share` — % of team RZ opportunities
- `target_share` — % of team targets
- `proe` — Points Over Expected (luck-adjusted efficiency)

#### Metrics NOT Affected

Static or current data are not adjusted:
- `adp` — Historical but stable
- `bye_week` — Team schedule (doesn't change)
- `espn_ownership` — Current league behavior
- `implied_team_pts` — Current week's Vegas line
- Injury status — Current (real-time)

---

### Step 3b: Injury Discount Factor Application

**Data Source:** ESPN API `status` + `body_part`

Each injury status maps to a multiplier that scales projected value:

| Status | Discount Factor | Scenario |
|--------|-----------------|----------|
| ACTIVE | 1.0 | Healthy, no restrictions |
| QUESTIONABLE | 0.88-0.95 | Soft-tissue tightness or precaution |
| DOUBTFUL | 0.40 | Likely out, emergency backup only |
| OUT / IR / PUP | 0.0 | Unavailable for play (reserve list) |
| SUSPENDED | 0.0 | Administrative unavailability |
| CUT | 0.0 | No longer on active roster |

**Formula:**
```
injury_discounted_value = projected_season * discount_factor
```

**Example:**
- Player: Christian McCaffrey (projected_season = 285, status = QUESTIONABLE, discount_factor = 0.88)
- Injury-adjusted projected = 285 * 0.88 = 251 points
- Injury impact: -34 points (-12% reduction)

---

### Step 4: Roster Need Multiplier

Based on your team's current composition and draft round, the system calculates a **need multiplier** for each position:

#### Running Back Logic
```
if rb_count == 0:
    if wr_count >= 2:
        multiplier = 1.40  // URGENT RB need + heavy WR start
    else:
        multiplier = 1.15  // Anchor RB1
elif rb_count == 1:
    if wr_count >= 3:
        multiplier = 1.35  // Critical RB2 to balance WRs
    else:
        multiplier = 1.10  // Completing RB duo
elif rb_count == 2:
    if wr_count < 2:
        multiplier = 0.70  // WR takes priority
    else:
        multiplier = 1.0   // FLEX or RB3 depth
elif rb_count in [3, 4]:
    if wr_count < 3 or qb_count == 0 or te_count == 0:
        multiplier = 0.60  // Balance other slots
    else:
        multiplier = 0.75  // Bench depth
else:  // 5+ RBs
    multiplier = 0.10  // Hard cap (saturated)
```

**Logic:** Prevents you from hoarding 5 WRs when you need a starting RB.

#### Wide Receiver Logic
Same inverse logic (high multiplier when WR count = 0 and RB count >= 2, etc.)

#### Tight End & QB Logic
- **Elite Window:** Rounds 2-4 for TE (elite studs), Rounds 3-5 for QB
- **Diminishing Returns:** After 1 starter, backup drafting is severely penalized (0.25-0.50 multiplier)

#### Kicker & Defense
- **Anti-Early Draft:** 0.05 multiplier until Round 14
- **Anti-Double-Stack:** After 1 starter, 0.05 multiplier (never draft backup K/DEF)

---

### Step 5: Bye Week Collision Multiplier

The system detects three bye-week scenarios:

| Type | Multiplier | Scenario |
|------|-----------|----------|
| No Conflict | 1.0 | Player's bye ≠ any teammate's bye |
| CLUSTER | 0.85 | 2+ teammates share same bye (manageable) |
| CLASH | 0.60 | 3+ teammates share same bye (critical problem) |

**Formula:**
```
bye_multiplier = {
    1.0 if no conflict,
    0.85 if CLUSTER (warn but allow),
    0.60 if CLASH (strong discouragement)
}
```

---

### Step 6: Combined Need-Adjusted Score

```
need_adjusted_score = (VORP + 50.0) * roster_need_multiplier * bye_week_multiplier
```

The `+ 50.0` baseline ensures all players have a positive base score (prevents negative values for late-round options).

**Example:**
- VORP: +10 points
- Roster need multiplier: 1.40 (URGENT RB need, heavy WR start)
- Bye week multiplier: 1.0 (no conflict)
- **need_adjusted_score = (10 + 50) * 1.40 * 1.0 = 84.0**

---

### Step 7: Positional Tier Cliff Detection

The system flags when you're approaching a **tier cliff**:

```
tier_cliff_warning = {
    "CRITICAL" if same_tier_remaining == 1,
    "Warning" if same_tier_remaining == 2,
    None otherwise
}
```

This alerts you: "Only 1 Tier 2 RB left — once taken, RB value drops to Tier 3."

---

## Metric Definitions (Rating Breakdown)

When you click "Why is this player rated X?" you get detailed metric cards:

### 1. Expected Fantasy Points (xFP)
- **Data:** Advanced play-by-play simulation
- **Formula:** Simulates average touches/targets across same role distribution
- **Rating Scale:** Elite (18+ xFP/gm) → Strong (14-18) → Solid (<14)
- **Impact:** 30% of overall value (primary predictor)

### 2. Route Participation %
- **Data:** % of team's passing plays where player runs a route
- **Why It Matters:** Elite WRs = 90%+ route rate (consistent touches)
- **Impact:** 20% of overall value

### 3. High-Value Touches (HVTs)
- **Data:** Targets + carries inside opponent's 10-yard line per game
- **Why It Matters:** HVTs worth ~2.5x more fantasy points than standard touches
- **Impact:** 20% of overall value

### 4. Red Zone Share
- **Data:** % of team's red zone touches/targets
- **Why It Matters:** Single highest predictor of TD ceiling
- **Impact:** 15% of overall value

### 5. Vegas Environment
- **Data:** Implied team total points & Vegas spread
- **Why It Matters:** High implied totals (25+ pts) = 15-30% more scoring drives
- **Impact:** 10% of overall value

### 6. Injury & Availability Status
- **Data:** INJURY_REGISTRY lookup
- **Scale:** Critical Injury → Monitoring → No Concerns
- **Impact:** Modulates all projections via discount_factor

### 7. Bye Week Compatibility
- **Data:** Player bye vs your team's bye schedule
- **Scale:** Critical Clash (3+) → Cluster Alert (2+) → No Conflict
- **Impact:** Reduces tier cliff urgency or increases it

---

## Architecture Decision Log

### Core Principle: Zero Hardcoding, Source-Driven Data
**All injury data originates from ESPN/Sleeper APIs. Nothing is manually curated or hardcoded in the codebase.**

```
❌ WRONG: "christian_mccaffrey" hardcoded in INJURY_REGISTRY with discount=0.88
✅ RIGHT: ESPN says "QUESTIONABLE, Calf" → Database calculates discount=0.88
```

This ensures:
- CMC shows ACTIVE the moment ESPN updates (no deploy needed)
- A new injury appears instantly when ESPN reports it
- If ESPN doesn't have injury data, player shows ACTIVE (not guessed)
- Discount factors are derived from injury type, not editorialized

---

### Why 10-Team Full PPR Baselines?
- 10 starting QBs, 25 RBs/WRs, 10 TEs, 10 K/DEF per league
- Prevents over-drafting depth at any position
- Ensures balanced roster construction over 15 rounds

### Why VORP Over ADP-Only?
- ADP is historical (last year's league behavior, shifted by injuries/retirements)
- VORP is contextual (your roster + current league state)
- Example: CMC falls to Round 3 due to injury concern → VORP adjusts down automatically

### Why Discount Factors Are Calculated, Not Hardcoded
- Injury type (hamstring vs calf vs illness) drives the discount
- Status (QUESTIONABLE vs OUT) provides fallback severity
- Example: "Hamstring + QUESTIONABLE" always → 0.88, never varies by editorializing
- Allows algorithm to scale to all 1000+ players without manual entry

### Why ESPN/Sleeper Are Single Sources of Truth
- QUESTIONABLE = ESPN/Sleeper says so, not our guess
- CUT = Sleeper says team=null, not our hardcoded list
- Injury type = ESPN body_part field, not our interpretation
- This is the only way to guarantee real-time accuracy

---

## Data Freshness & Sync Intervals

| Source | Sync Frequency | Update Method |
|--------|----------------|---------------|
| ESPN (Injuries) | On `/refresh/teams-and-players` click | Live API pull |
| Sleeper (Rosters) | On `/refresh/teams-and-players` click | Live API pull |
| INJURY_REGISTRY | Manual editorial updates | Deployed with app |
| Player Projections | Once per app start | Static JSON seed |
| Vegas Metrics | Once per app start | Static JSON seed |

---

## Quality Gates & Verification

### Before Each Calculation:
1. ✅ Player exists in INITIAL_PLAYERS
2. ✅ No duplicate drafting (draft_history check)
3. ✅ Injury status resolved (ESPN → Sleeper → Registry)
4. ✅ Discount factor applied correctly (0.0-1.0 range)
5. ✅ Bye week collision detected (roster cross-check)

### Before Display:
6. ✅ Sorted by need_adjusted_score (descending)
7. ✅ Tier cliff warnings generated
8. ✅ Opponent threats identified (picks before yours)
9. ✅ Scouting takeaway generated with live tier + role context

---

## Data Sourcing Checklist (Zero Hardcoding Verification)

Every piece of injury/status data must pass this checklist:

| Data Point | Source | How to Verify | Should Be Hardcoded? |
|-----------|--------|---------------|----------------------|
| Player status (ACTIVE, QUESTIONABLE, OUT) | ESPN API | Check `espn_service.get_league_overview()` | ❌ NO — pull from ESPN |
| Player on roster? | Sleeper API | Check `team` field in roster response | ❌ NO — pull from Sleeper |
| Player cut? | Sleeper API | Check `team=null` in Sleeper rosters | ❌ NO — pull from Sleeper |
| Injury body part (Hamstring, Calf) | ESPN API | Check ESPN injury report field | ❌ NO — pull from ESPN |
| Injury timeline (Day-to-day, Weeks 1-4) | ESPN API | Check ESPN injury report field | ❌ NO — pull from ESPN |
| Discount factor (0.88, 0.95, 0.0) | **Calculated** from body_part + status | Algorithm in discount_engine.py | ❌ NO — calculate, never hardcode |
| Player ADP (12.5) | INITIAL_PLAYERS | Static database seed | ✅ YES — stable across season |
| Player tier (Tier 1, 2, 3) | INITIAL_PLAYERS | Static database seed | ✅ YES — stable across season |
| Player position (RB, WR) | INITIAL_PLAYERS | Static database seed | ✅ YES — stable across season |
| Bye week (Week 9) | INITIAL_PLAYERS | Static database seed | ✅ YES — stable across season |

**The Rule:** If it changes during the season (injury, roster status), pull from API. If it's static (ADP, position, bye), seed once.

---

## Known Limitations & Edge Cases

### ESPN Data Completeness
**Problem:** ESPN sometimes doesn't provide `body_part` field for injuries.  
**Impact:** We fall back to status-only discount (0.90 for QUESTIONABLE instead of body-part-specific 0.88-0.95).  
**Mitigation:** Accept lower precision; ESPN status is still accurate.

### Sleeper Roster Sync Lag
**Problem:** Cut detection relies on Sleeper's roster sync (typically <1hr, rarely 2-4 hours).  
**Impact:** Recently-cut player might still show as ACTIVE for up to 4 hours.  
**Mitigation:** User can manually override status via API if they know a cut before Sleeper updates.

### Injury Report Timing
**Problem:** NFL team injury reports release ~15min before games; preseason/offseason can be sporadic.  
**Impact:** You might miss an injury reported during trading/draft windows.  
**Mitigation:** Monitor ESPN/Sleeper during live draft; use `/refresh` aggressively before picks.

### Projection Model Drift
**Problem:** Preseason projections diverge from reality by Week 3-4.  
**Impact:** A player with 280 projected_season is overestimated by Week 5+.  
**Mitigation:** Projections reset seasonally; VORP still works because replacement_points adjust proportionally.

### ADP Inflation
**Problem:** Some players drafted higher than VORP justifies (hype, media buzz).  
**Impact:** VORP board ignores ADP noise, focuses on role quality instead.  
**Mitigation:** This is intentional; VORP is more predictive than ADP inflation.

---

## Next Steps for Rework

### Phase 1: Database Schema & API Sync
1. **Create injury_records table**
   - Columns: player_id, status, body_part, timeline, source (espn/sleeper), last_updated_at
   - No manual editing; only programmatic updates from API syncs

2. **Implement real-time ESPN injury sync**
   - Pull player status + body_part on each `/refresh`
   - Update injury_records with ESPN data
   - Calculate discount_factor from body_part

3. **Implement real-time Sleeper cut detection**
   - Detect team=null in Sleeper rosters
   - Update injury_records: status=CUT, discount=0.0

4. **Remove all hardcoded INJURY_REGISTRY entries**
   - Delete injury_registry.py dictionary
   - Replace with database queries

### Phase 2: Context Certainty & Metric Adjustment
5. **Build context continuity detection**
   - Detect QB changes (2025 → 2026)
   - Detect OC/HC changes
   - Detect key player departures (WR1, pass-catching RB, etc.)
   - Calculate context_certainty_factor (0.4-1.0)

6. **Implement metric recalculation engine**
   - Input: projected_metric (xFP, route_pct, etc.), context_certainty
   - Output: recalculated_metric = projected × certainty
   - Store both values (projected + recalculated)
   - Display three-column format (Projected | Factor | Recalculated)

7. **Validate context factors against preseason consensus**
   - Do Jefferson's metrics drop when QB changes?
   - Do high-certainty players (no change) match 2025 performance?

### Phase 3: Injury Discount Factor Calculation
8. **Implement injury discount calculation engine**
   - Input: status, body_part (from database)
   - Output: discount_factor (0.0-1.0)
   - Rules: no hardcoding, purely algorithmic

9. **Validate discount factors against real data**
   - Week 1-4: Do QUESTIONABLE players match 0.88-0.95 performance?
   - Week 5+: Do DOUBTFUL players match 0.40 performance?

### Phase 4: Testing & Validation
10. **Test ESPN/Sleeper sync in local environment**
    - Verify status updates propagate correctly
    - Verify cuts are detected within 4 hours
    - Verify discount factors recalculate on each sync

11. **Test context certainty in local environment**
    - Verify QB changes are detected
    - Verify context_certainty scores calculate correctly
    - Verify recalculated metrics display (Projected | Factor | Recalculated)

12. **Test edge cases**
    - Player goes QUESTIONABLE → ACTIVE → OUT (multiple state changes)
    - Player cut then re-signed (Sleeper sync catches both)
    - ESPN missing body_part field (fallback to status-only)
    - Rookie with no 2025 history (falls back to preseason projections)
    - Player with multiple roster changes (QB, OC, HC all changed)

13. **Live draft testing**
    - Run `/refresh` during live draft
    - Verify opponent picks sync in real-time
    - Verify injuries update during draft window
    - Verify context certainty factors display in rating breakdown

---

## Real-World Data Flow Examples

### Scenario 1: Player Reports Hamstring Tightness
```
Day 1, 10:00am:
  └─ ESPN reports: "CMC listed QUESTIONABLE, Hamstring"
      └─ /refresh endpoint syncs ESPN
          └─ Database updates: injury_records[cmccaffrey] = {
               status: QUESTIONABLE,
               body_part: Hamstring,
               timeline: Day-to-day,
               source: ESPN,
               last_updated: 2026-09-15 10:00
             }
          └─ Discount engine calculates: body_part=Hamstring → 0.88
              └─ App displays: "CMC — Hamstring (Tightness) — 0.88 discount"

Day 2, 8:00am:
  └─ ESPN reports: "CMC cleared, ACTIVE"
      └─ /refresh endpoint syncs ESPN
          └─ Database updates: injury_records[cmccaffrey] = {
               status: ACTIVE,
               body_part: null,
               source: ESPN,
               last_updated: 2026-09-16 08:00
             }
          └─ Discount engine calculates: status=ACTIVE → 1.0
              └─ App displays: "CMC — Healthy — 1.0 discount"
```
**Zero deployment needed. Zero manual edits. Data flows: ESPN → Database → App.**

---

### Scenario 2: Player Is Cut/Waived
```
Day 1, 3:00pm:
  └─ Team announces: "Player X waived"
      └─ Sleeper API updates: Player X team=null
          └─ /refresh endpoint syncs Sleeper
              └─ Database updates: injury_records[playerx] = {
                   status: CUT,
                   source: Sleeper,
                   last_updated: 2026-09-15 15:00
                 }
              └─ Discount engine calculates: status=CUT → 0.0
                  └─ App displays: "Player X — Cut — 0.0 discount (unavailable)"
```
**No hardcoded "cuts list". Sleeper tells us immediately.**

---

### Scenario 3: New Injury, No Body Part Info
```
Day 1, 2:00pm:
  └─ ESPN reports: "Backup RB listed OUT"
      └─ /refresh endpoint syncs ESPN
          └─ Database updates: injury_records[backuprb] = {
               status: OUT,
               body_part: null,  // ESPN didn't provide
               source: ESPN,
               last_updated: 2026-09-15 14:00
             }
          └─ Discount engine logic:
              IF status == "OUT" → 0.0 (immediate, no body_part needed)
              └─ App displays: "Backup RB — Out — 0.0 discount"
```
**Status is enough. We don't guess body parts.**

---

### Scenario 4: Player Goes Through Multiple State Changes
```
Week 2, Mon 10:00am:
  └─ "Star WR listed QUESTIONABLE, Ankle"
      └─ Database: {status: Q, body_part: Ankle, discount: 0.90}
          └─ App display: 0.90 discount

Week 2, Tue 2:00pm:
  └─ "Star WR upgraded to PROBABLE"
      └─ Database: {status: PROBABLE, body_part: Ankle, discount: 0.95}
          └─ App display: 0.95 discount

Week 2, Wed 9:00am:
  └─ "Star WR ACTIVE, no restrictions"
      └─ Database: {status: ACTIVE, body_part: null, discount: 1.0}
          └─ App display: 1.0 discount
```
**Each update syncs automatically. No deploy, no manual entry.**

---

## Validation Rules

Before displaying any player:

```python
# Rule 1: Status must come from ESPN or Sleeper, never hardcoded
assert player["injury_status"] in ["ACTIVE", "QUESTIONABLE", "DOUBTFUL", "OUT", "IR", "PUP", "SUSPENDED", "CUT"]
assert player["injury_source"] in ["ESPN", "Sleeper"]

# Rule 2: Body part is optional; status is mandatory
assert player["injury_status"] is not None
# injury_body_part can be null

# Rule 3: Discount factor is calculated, not stored
discount = calculate_discount(
    status=player["injury_status"],
    body_part=player["injury_body_part"]
)
assert 0.0 <= discount <= 1.0

# Rule 4: No hardcoded entries for individual players
assert not player.get("hardcoded_discount_override")
```

**These rules prevent regression back to hardcoding.**
