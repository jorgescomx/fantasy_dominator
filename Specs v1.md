---
name: nfl-fantasy-dominator
description: Complete specification and implementation blueprint for building an AI-driven, 10-team full-PPR NFL fantasy football web app with live draft optimization, weekly sit/start solvers, and waiver opportunity arbitrage.
mainAgent: true
permissionMode: acceptEdits
commandExecutionPolicy: auto
---

# NFL Fantasy Dominator — System Architecture & Specification

## 1. Project Overview & Objectives
Build a full-stack data ingestion pipeline, predictive algorithm engine, and interactive dashboard tailored exclusively to dominate a **10-Team, Full-PPR (Point Per Reception)** fantasy football league.

### Core Modules
1. **Live Draft Assistant:** Real-time Dynamic Value Over Replacement Player (VORP) calculator, tier-drop alerts, opponent roster sniffer, and rookie upside modeling.
2. **Weekly Lineup Optimizer:** Contextual expected fantasy points (`xFP`) simulator, ceiling/floor solver based on projected game script/spread, and weather wind threshold adjustments.
3. **Waiver & Trade Arbitrage Radar:** Detection of leading indicators (Route Participation spikes, High-Value Touch share, Red Zone usage) before box scores reflect breakouts; drop-candidate delta evaluator; consensus market mispricing index.
4. **League State Manager:** Manual 10-team roster and waiver wire tracker with persistent SQLite database state.

---

## 2. Technical Stack
* **Language & Runtime:** Python 3.11+ / FastAPI (Backend) + TypeScript / Next.js 14+ (App Router) or Streamlit (Rapid Prototype)
* **Mathematical & Linear Solvers:** `numpy`, `pandas`, `scipy.optimize`, `pulp`, `scikit-learn`, `xgboost`
* **Data Sources & Client Libraries:**
  * `nflreadpy` (NFLverse Python client): Play-by-play, xFP, PROE, player stats, weekly depth charts, injury reports.
  * Sleeper API (`https://api.sleeper.app/v1/`): Real-time player database, depth chart order, active status.
  * The Odds API: Live NFL game spreads, over/under totals, and implied team points.
  * OpenWeatherMap / NWS API: Stadium weather tracking with sustained wind filters.
* **Storage:** SQLite (via SQLAlchemy or DuckDB) for local persistence of the 10 teams, draft board, and cached weekly stats.

---

## 3. Data Ingestion Architecture & Endpoints

### 3.1 Data Pipeline Sources