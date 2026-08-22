from pydantic import BaseModel
from typing import Dict, Any, List
import os
from pathlib import Path

# Load .env file
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

class LeagueSettings(BaseModel):
    num_teams: int = 10
    scoring_type: str = "PPR"
    roster_slots: Dict[str, int] = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "FLEX": 1,  # RB / WR / TE
        "K": 1,
        "DEF": 1,
        "BENCH": 7,
        "IR": 1
    }
    scoring_rules: Dict[str, float] = {
        "pass_yd": 0.04,
        "pass_td": 4.0,
        "pass_int": -2.0,
        "rush_yd": 0.1,
        "rush_td": 6.0,
        "rec": 1.0,  # Full PPR
        "rec_yd": 0.1,
        "rec_td": 6.0,
        "fumble_lost": -2.0,
        "fg_0_39": 3.0,
        "fg_40_49": 4.0,
        "fg_50_plus": 5.0,
        "pat": 1.0,
        "def_sack": 1.0,
        "def_int": 2.0,
        "def_fumble_rec": 2.0,
        "def_td": 6.0,
        "def_safety": 2.0,
        "def_pts_0": 10.0,
        "def_pts_1_6": 7.0,
        "def_pts_7_13": 4.0,
        "def_pts_14_20": 1.0,
        "def_pts_21_27": 0.0,
        "def_pts_28_34": -1.0,
        "def_pts_35_plus": -4.0,
    }

class Settings:
    PROJECT_NAME: str = "NFL Fantasy Dominator"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fantasy_dominator.db")
    ESPN_LEAGUE_ID: str = os.getenv("ESPN_LEAGUE_ID", "")
    ESPN_YEAR: int = int(os.getenv("ESPN_YEAR", "2024"))
    ESPN_S2: str = os.getenv("ESPN_S2", "")
    ESPN_SWID: str = os.getenv("ESPN_SWID", "")
    DEFAULT_LEAGUE: LeagueSettings = LeagueSettings()

settings = Settings()
