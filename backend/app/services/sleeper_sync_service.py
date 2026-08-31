"""
Sleeper API sync service.
Primary source for: injuries, rosters, depth charts, transactions.
All data flows from Sleeper API only - no hardcoding.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal, DBInjuryRecord
import logging

logger = logging.getLogger(__name__)

SLEEPER_API_BASE = "https://api.sleeper.app/v1"

def get_sleeper_players() -> Dict[str, Any]:
    """Fetch all NFL players from Sleeper."""
    try:
        url = f"{SLEEPER_API_BASE}/players/nfl"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch Sleeper players: {resp.status_code}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching Sleeper players: {e}")
        return {}

def sync_sleeper_injuries() -> Dict[str, Any]:
    """
    Sync injury data from Sleeper API.
    Updates injury_records table with Sleeper as source.
    """
    db = SessionLocal()
    try:
        players = get_sleeper_players()
        if not players:
            return {"status": "error", "message": "Failed to fetch Sleeper players"}

        synced_count = 0
        errors = []

        for player_id, player_data in players.items():
            try:
                player_name = player_data.get("full_name", "")
                injury_status = player_data.get("injury_status", "ACTIVE")

                # Only sync if there's an injury status
                if not injury_status or injury_status.upper() == "ACTIVE":
                    continue

                body_part = player_data.get("injury_body_part")
                notes = player_data.get("injury_notes", "")

                # Calculate discount factor from status + body_part
                from backend.app.services.injury_records_service import calculate_discount_factor
                discount_factor = calculate_discount_factor(injury_status, body_part)

                # Upsert into database
                record = db.query(DBInjuryRecord).filter(
                    DBInjuryRecord.player_id == player_id
                ).first()

                if record:
                    record.status = injury_status
                    record.body_part = body_part
                    record.discount_factor = discount_factor
                    record.source = "Sleeper"
                    record.notes = f"Sleeper sync: {notes}" if notes else ""
                    record.last_updated_at = datetime.utcnow()
                else:
                    record = DBInjuryRecord(
                        player_id=player_id,
                        player_name=player_name,
                        status=injury_status,
                        body_part=body_part,
                        discount_factor=discount_factor,
                        source="Sleeper",
                        notes=f"Sleeper sync: {notes}" if notes else ""
                    )
                    db.add(record)

                synced_count += 1

            except Exception as e:
                errors.append(f"Error syncing {player_name}: {str(e)}")
                logger.error(f"Error syncing player {player_id}: {e}")

        db.commit()

        return {
            "status": "success",
            "sleeper_injuries_synced": synced_count,
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Sleeper sync error: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()

def get_player_injury_from_sleeper(player_id: str) -> Optional[Dict[str, Any]]:
    """
    Get injury data for a specific player from Sleeper.
    Direct lookup without database query.
    """
    try:
        players = get_sleeper_players()
        if player_id not in players:
            return None

        player = players[player_id]
        injury_status = player.get("injury_status", "ACTIVE")

        if not injury_status or injury_status.upper() == "ACTIVE":
            return None

        body_part = player.get("injury_body_part")
        notes = player.get("injury_notes", "")

        from backend.app.services.injury_records_service import calculate_discount_factor
        discount_factor = calculate_discount_factor(injury_status, body_part)

        return {
            "player_id": player_id,
            "player_name": player.get("full_name", ""),
            "status": injury_status,
            "body_part": body_part,
            "discount_factor": discount_factor,
            "notes": notes,
            "source": "Sleeper"
        }

    except Exception as e:
        logger.error(f"Error fetching Sleeper injury for {player_id}: {e}")
        return None

def get_sleeper_roster(league_id: str) -> Dict[str, Any]:
    """Fetch rosters from Sleeper league."""
    try:
        url = f"{SLEEPER_API_BASE}/league/{league_id}/rosters"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch Sleeper rosters: {resp.status_code}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching Sleeper rosters: {e}")
        return {}

def get_sleeper_users(league_id: str) -> Dict[str, Any]:
    """Fetch users from Sleeper league."""
    try:
        url = f"{SLEEPER_API_BASE}/league/{league_id}/users"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch Sleeper users: {resp.status_code}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching Sleeper users: {e}")
        return {}

def get_sleeper_matchups(league_id: str, week: int) -> List[Dict[str, Any]]:
    """Fetch matchups from Sleeper league for a specific week."""
    try:
        url = f"{SLEEPER_API_BASE}/league/{league_id}/matchups/{week}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch Sleeper matchups: {resp.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Sleeper matchups: {e}")
        return []

def get_sleeper_transactions(league_id: str, round_num: int = 1) -> List[Dict[str, Any]]:
    """Fetch transactions (trades, pickups) from Sleeper league."""
    try:
        url = f"{SLEEPER_API_BASE}/league/{league_id}/transactions/{round_num}"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.error(f"Failed to fetch Sleeper transactions: {resp.status_code}")
        return []
    except Exception as e:
        logger.error(f"Error fetching Sleeper transactions: {e}")
        return []
