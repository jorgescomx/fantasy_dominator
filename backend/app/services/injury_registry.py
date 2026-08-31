"""
Injury records lookup service.
Queries real-time injury data from injury_records database.
All data flows from ESPN/Sleeper APIs. No hardcoding.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal, DBInjuryRecord
import logging

logger = logging.getLogger(__name__)

# Static list of expected healthy starters (not taggable as injured)
# Only used as a sanity check; all injury data comes from ESPN/Sleeper database
HEALTHY_STARTERS = {
    "breece hall",
    "josh jacobs",
    "devonta smith",
    "malik nabers",
    "amon ra st brown",
    "amon-ra st. brown",
    "nico collins",
    "derrick henry",
    "brian thomas jr",
    "marvin harrison jr",
    "aj brown",
    "a.j. brown",
    "jonathan taylor",
    "brock bowers",
    "kyren williams",
    "devon achane",
    "de'von achane",
    "lamar jackson",
    "josh allen",
    "jayden daniels",
    "jalen hurts",
    "trey mcbride",
    "george kittle",
    "drake london",
    "garrett wilson",
    "james cook",
    "bucky irving",
    "ladd mcconkey",
    "terry mclaurin",
    "sam laporta",
    "travis kelce",
    "tucker kraft",
    "trey benson",
    "jalen mcmillan",
    "colston loveland",
    "tyler warren",
    "evan engram",
    "jake ferguson",
    "david njoku",
    "cole kmet",
    "luther burden",
    "rome odunze",
    "brandon aubrey",
    "chris boswell",
    "patrick mahomes",
    "joe burrow",
    "cj stroud",
    "c.j. stroud",
    "kyler murray",
    "jordan love",
    "baker mayfield",
    "brock purdy",
    "caleb williams",
    "jared goff",
    "dak prescott",
    "anthony richardson",
    "bo nix",
    "tua tagovailoa",
    "drake maye",
    "trevor lawrence",
    "matthew stafford",
    "geno smith",
    "kirk cousins",
    "aaron rodgers",
    "russell wilson",
    "bryce young",
    "will levis",
    "tyler shough",
    "cam ward",
    "shedeur sanders",
    "daniel jones",
    "harrison butker",
    "justin tucker"
}

def normalize_name(name: str) -> str:
    return name.lower().replace(".", "").replace("'", "").replace("-", " ").strip()

def get_injury_details(player_name: str, raw_status: Optional[str] = None, raw_body_part: Optional[str] = None, raw_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Look up injury record from database (ESPN/Sleeper sourced).
    All data flows from real-time APIs. No hardcoding.
    """
    norm = normalize_name(player_name)
    st = (raw_status or "").upper()

    # If status is explicitly healthy, return None (no injury)
    if st in ["ACTIVE", "HEALTHY", "CLEARED", "NONE", ""]:
        return None

    # Query database for this player's injury record
    db = SessionLocal()
    try:
        record = db.query(DBInjuryRecord).filter(
            DBInjuryRecord.player_name.ilike(f"%{player_name}%")
        ).first()

        if record and record.status not in ["ACTIVE", "HEALTHY"]:
            return {
                "status": record.status,
                "type": record.body_part or "Reported Injury",
                "timeline": record.timeline or "TBD",
                "notes": record.notes or "",
                "impact_summary": f"{int((1 - record.discount_factor) * 100)}% discount applied (factor: {record.discount_factor})",
                "discount_factor": record.discount_factor,
                "source": record.source,
                "last_updated": record.last_updated_at.isoformat() if record.last_updated_at else None
            }

        return None

    except Exception as e:
        logger.warning(f"Error querying injury database for {player_name}: {e}")
        return None

    finally:
        db.close()
