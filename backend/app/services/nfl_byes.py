"""
NFL Bye Week Intelligence & Roster Collision Protection.
Guarantees verified 32-team bye schedules and evaluates roster collisions.
"""
from typing import Dict, Any, List, Optional

# Official NFL regular season Bye Weeks by Team
NFL_TEAM_BYES: Dict[str, int] = {
    "DET": 5, "PHI": 5, "LAC": 5, "TEN": 5,
    "KC": 6, "LAR": 6, "MIA": 6, "MIN": 6,
    "CHI": 7, "DAL": 7,
    "PIT": 9, "SF": 9,
    "CLE": 10, "GB": 10, "LV": 10, "SEA": 10,
    "ARI": 11, "CAR": 11, "NYG": 11, "TB": 11,
    "ATL": 12, "BUF": 12, "CIN": 12, "JAX": 12, "NO": 12, "NYJ": 12,
    "BAL": 14, "DEN": 14, "HOU": 14, "IND": 14, "NE": 14, "WAS": 14
}

def get_team_bye_week(team: Optional[str]) -> Optional[int]:
    if not team:
        return None
    return NFL_TEAM_BYES.get(team.upper().strip(), None)

def evaluate_bye_conflicts(roster: List[Dict[str, Any]], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates whether drafting the candidate player creates a bye week collision with the current roster.
    
    Rules:
    1. Single-starter positions (QB, TE, K, DEF):
       - If you already have 1+ QB/TE and the candidate shares the identical bye week,
         this is a CRITICAL clash (leaving you with 0 active starters during that week).
    2. Multi-starter positions (RB, WR):
       - If you already have 2+ RBs on the same bye week, adding a 3rd creates an RB cluster.
       - If you already have 3+ WRs on the same bye week, adding a 4th creates a WR cluster.
    """
    cand_pos = candidate.get("position", "")
    cand_team = candidate.get("team", "")
    cand_bye = candidate.get("bye_week") or get_team_bye_week(cand_team)
    
    if not cand_bye:
        return {
            "has_conflict": False,
            "conflict_type": None,
            "multiplier": 1.0,
            "warning": None,
            "badge": None,
            "badge_class": None,
            "bye_week": None
        }

    # Analyze existing roster at this position
    same_pos_players = [p for p in roster if p.get("position") == cand_pos]
    same_bye_same_pos = [
        p for p in same_pos_players 
        if (p.get("bye_week") or get_team_bye_week(p.get("team"))) == cand_bye
    ]
    
    # 1. Single-Starter Positions (QB, TE, K, DEF)
    if cand_pos in ["QB", "TE", "K", "DEF"]:
        if len(same_pos_players) >= 1 and len(same_bye_same_pos) >= 1:
            starter = same_bye_same_pos[0]
            starter_name = starter.get("name", f"your {cand_pos}1")
            return {
                "has_conflict": True,
                "conflict_type": "CLASH",
                "multiplier": 0.40,  # Heavy penalty for same-bye backup
                "warning": f"CRITICAL BYE CLASH: Shares Week {cand_bye} Bye with {starter_name}! Both QBs/TEs will be inactive simultaneously.",
                "badge": f"⚠️ BYE CLASH (Wk {cand_bye})",
                "badge_class": "bye-clash",
                "bye_week": cand_bye
            }

    # 2. Multi-Starter Positions (RB)
    if cand_pos == "RB":
        if len(same_bye_same_pos) >= 2:
            return {
                "has_conflict": True,
                "conflict_type": "CLUSTER",
                "multiplier": 0.82,  # Roster cluster penalty
                "warning": f"Bye Clustering Alert: You already have {len(same_bye_same_pos)} RBs on Week {cand_bye} Bye. Roster depth crunch risk.",
                "badge": f"⚠️ BYE CLUSTER (Wk {cand_bye})",
                "badge_class": "bye-cluster",
                "bye_week": cand_bye
            }

    # 3. Multi-Starter Positions (WR)
    if cand_pos == "WR":
        if len(same_bye_same_pos) >= 3:
            return {
                "has_conflict": True,
                "conflict_type": "CLUSTER",
                "multiplier": 0.80,
                "warning": f"Bye Clustering Alert: You already have {len(same_bye_same_pos)} WRs on Week {cand_bye} Bye. Severe starting lineup deficit in Week {cand_bye}.",
                "badge": f"⚠️ BYE CLUSTER (Wk {cand_bye})",
                "badge_class": "bye-cluster",
                "bye_week": cand_bye
            }

    return {
        "has_conflict": False,
        "conflict_type": None,
        "multiplier": 1.0,
        "warning": None,
        "badge": None,
        "badge_class": None,
        "bye_week": cand_bye
    }
