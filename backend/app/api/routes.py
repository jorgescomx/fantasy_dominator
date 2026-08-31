from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from backend.app.services.nfl_stats_service import nfl_stats_service
from backend.app.services.espn_service import espn_service
from backend.app.services.draft_engine import draft_engine
from backend.app.services.lineup_optimizer import lineup_optimizer
from backend.app.services.waiver_radar import waiver_radar

router = APIRouter()

# --- Request / Response Models ---
class ESPNConnectRequest(BaseModel):
    league_id: str = Field(default="", max_length=32, pattern=r"^\d*$")
    year: int = Field(default=2024, ge=2000, le=2100)
    espn_s2: Optional[str] = Field(default="", max_length=4096)
    swid: Optional[str] = Field(default="", max_length=256)

class DraftPickRequest(BaseModel):
    player_id: str = Field(min_length=1, max_length=128)
    team_id: Optional[int] = Field(default=None, ge=1, le=100)

class DraftResetRequest(BaseModel):
    user_pick: Optional[int] = Field(default=1, ge=1, le=100)

class LineupOptimizeRequest(BaseModel):
    team_id: Optional[int] = Field(default=1, ge=1, le=100)
    mode: Optional[str] = Field(default="balanced", pattern=r"^(balanced|ceiling|floor)$")

class SitStartCompareRequest(BaseModel):
    player_id_a: str = Field(min_length=1, max_length=128)
    player_id_b: str = Field(min_length=1, max_length=128)

# --- Endpoints ---

@router.get("/health")
def health_check():
    return {"status": "ok", "app": "NFL Fantasy Dominator", "version": "2.0.0"}

@router.get("/players")
def get_players(position: Optional[str] = None):
    players = nfl_stats_service.get_all_players()
    if position:
        players = [p for p in players if p["position"].upper() == position.upper()]
    return {"count": len(players), "players": players}

@router.get("/players/{player_id}/rating-breakdown")
def get_player_rating_breakdown(player_id: str):
    try:
        breakdown = draft_engine.get_player_rating_breakdown(player_id)
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/league/overview")
def get_league_overview():
    return espn_service.get_league_overview()

@router.post("/league/connect")
def connect_espn(req: ESPNConnectRequest):
    result = espn_service.connect(
        league_id=req.league_id,
        year=req.year,
        espn_s2=req.espn_s2 or "",
        swid=req.swid or ""
    )
    return result

@router.get("/league/roster/{team_id}")
def get_team_roster(team_id: int):
    roster = espn_service.get_team_roster(team_id)
    return {"team_id": team_id, "roster": roster}

# --- Draft Engine Endpoints ---

@router.get("/draft/state")
def get_draft_state():
    return draft_engine.get_draft_state()

@router.post("/draft/pick")
def make_draft_pick(req: DraftPickRequest):
    try:
        pick = draft_engine.make_pick(player_id=req.player_id, team_id=req.team_id)
        return {"success": True, "pick": pick, "next_state": draft_engine.get_draft_state()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/draft/undo")
def undo_draft_pick():
    undone = draft_engine.undo_last_pick()
    if not undone:
        raise HTTPException(status_code=400, detail="No picks to undo")
    return {"success": True, "undone_pick": undone, "next_state": draft_engine.get_draft_state()}

@router.post("/draft/reset")
def reset_draft(req: DraftResetRequest):
    draft_engine.reset(user_pick=req.user_pick)
    return {"success": True, "message": "Draft reset successfully", "next_state": draft_engine.get_draft_state()}

@router.post("/draft/sync-espn")
def sync_espn_draft_picks():
    stats = draft_engine.sync_live_espn_picks()
    return {"success": True, "sync_stats": stats, "next_state": draft_engine.get_draft_state()}

# --- Lineup Optimizer Endpoints ---

@router.post("/lineup/optimize")
def optimize_lineup(req: LineupOptimizeRequest):
    roster = espn_service.get_team_roster(req.team_id or 1)
    result = lineup_optimizer.solve_optimal_lineup(roster_pool=roster, mode=req.mode or "balanced")
    return result

@router.post("/lineup/compare")
def compare_sit_start(req: SitStartCompareRequest):
    try:
        comparison = lineup_optimizer.compare_sit_start(req.player_id_a, req.player_id_b)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Waiver Radar Endpoints ---

@router.get("/waiver/radar")
def get_waiver_radar():
    breakouts = waiver_radar.scan_breakout_arbitrage()
    return {"count": len(breakouts), "breakout_targets": breakouts}

@router.get("/waiver/drop-candidates")
def get_drop_candidates(team_id: Optional[int] = 1):
    candidates = waiver_radar.evaluate_drop_candidates(team_id or 1)
    return {"count": len(candidates), "drop_candidates": candidates}

# --- Data Refresh Endpoints ---

@router.post("/refresh/teams-and-players")
def refresh_teams_and_players():
    """Refresh all team rosters and player information from latest data"""
    from datetime import datetime
    try:
        espn_service.refresh_all_data()
        nfl_sync_result = nfl_stats_service.sync_with_live_nfl_feed()
        draft_engine.refresh_available_players()
        return {
            "success": True,
            "message": "Teams, rosters, and player information refreshed successfully",
            "timestamp": datetime.now().isoformat(),
            "sync_details": nfl_sync_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
