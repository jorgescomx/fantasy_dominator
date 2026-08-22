from typing import Dict, Any, List, Optional
import logging
from backend.app.core.config import settings
from backend.app.services.nfl_stats_service import nfl_stats_service

logger = logging.getLogger(__name__)

# 10-Team League real baseline structure
MOCK_TEAMS = [
    {"id": 1, "name": "Franja Broncos V", "owner": "Bernardo", "standing": 1, "wins": 0, "losses": 0},
    {"id": 2, "name": "Totopo", "owner": "Edgar Josue", "standing": 2, "wins": 0, "losses": 0},
    {"id": 3, "name": "Zapaton", "owner": "Manager", "standing": 3, "wins": 0, "losses": 0},
    {"id": 4, "name": "GoldenRuster", "owner": "Manager", "standing": 4, "wins": 0, "losses": 0},
    {"id": 5, "name": "Team 5", "owner": "Manager", "standing": 5, "wins": 0, "losses": 0},
    {"id": 6, "name": "Hastalavictoriasiempre", "owner": "A", "standing": 6, "wins": 0, "losses": 0},
    {"id": 7, "name": "Chiapas", "owner": "Manager", "standing": 7, "wins": 0, "losses": 0},
    {"id": 8, "name": "Good2Dream", "owner": "Jorge", "standing": 8, "wins": 0, "losses": 0},
    {"id": 9, "name": "Fins up", "owner": "Manager", "standing": 9, "wins": 0, "losses": 0},
    {"id": 10, "name": "Raidersito", "owner": "Manager", "standing": 10, "wins": 0, "losses": 0}
]

class ESPNService:
    def __init__(self):
        self.is_connected = False
        self.league_id = settings.ESPN_LEAGUE_ID
        self.year = settings.ESPN_YEAR
        self.espn_s2 = settings.ESPN_S2
        self.swid = settings.ESPN_SWID
        self.espn_league_instance = None
        self._mock_rosters = self._generate_initial_mock_rosters()
        
        # Auto-connect if credentials exist in config/.env
        if self.league_id:
            try:
                self.connect(self.league_id, self.year, self.espn_s2, self.swid)
            except Exception as e:
                logger.warning(f"Auto-connect on init failed: {e}")

    def _generate_initial_mock_rosters(self) -> Dict[int, List[Dict[str, Any]]]:
        """Generates realistic 10-team rosters for initial state / demo mode."""
        all_players = nfl_stats_service.get_all_players()
        rosters: Dict[int, List[Dict[str, Any]]] = {t["id"]: [] for t in MOCK_TEAMS}
        
        # Realistically distribute top players across 10 teams
        team_assignments = {
            1: ["wr-chase", "rb-gibbs", "wr-btj", "qb-daniels", "te-mcbride", "rb-bucky", "wr-ladd", "def-vikings", "k-aubrey"], # User's dominant team
            2: ["wr-ceedee", "rb-breece", "te-bowers", "qb-allen", "rb-cook", "wr-terry"],
            3: ["rb-cmc", "wr-marv", "rb-jt", "te-kittle", "qb-hurts"],
            4: ["wr-jj", "rb-saquon", "wr-nabers", "te-laporta", "qb-lamar"],
            5: ["wr-tyreek", "rb-achane", "rb-henry", "te-kelce", "wr-london"],
            6: ["rb-saquon", "wr-amonra", "rb-kyren", "wr-gw"],
            7: ["wr-amonra", "rb-bijan", "rb-henry"],
            8: ["qb-hurts", "wr-ceedee", "rb-jt"],
            9: ["rb-bijan", "wr-nico", "rb-kyren"],
            10: ["te-bowers", "rb-jacobs", "wr-marv"]
        }

        player_map = {p["id"]: p for p in all_players}
        for team_id, p_ids in team_assignments.items():
            for pid in p_ids:
                if pid in player_map:
                    p_copy = dict(player_map[pid])
                    p_copy["lineup_slot"] = self._assign_default_slot(p_copy["position"], rosters[team_id])
                    rosters[team_id].append(p_copy)
        return rosters

    def _assign_default_slot(self, position: str, current_roster: List[Dict[str, Any]]) -> str:
        current_slots = [p.get("lineup_slot") for p in current_roster]
        if position == "QB" and "QB" not in current_slots:
            return "QB"
        if position == "RB":
            if current_slots.count("RB") < 2:
                return "RB"
            elif "FLEX" not in current_slots:
                return "FLEX"
        if position == "WR":
            if current_slots.count("WR") < 2:
                return "WR"
            elif "FLEX" not in current_slots:
                return "FLEX"
        if position == "TE":
            if "TE" not in current_slots:
                return "TE"
            elif "FLEX" not in current_slots:
                return "FLEX"
        if position == "K" and "K" not in current_slots:
            return "K"
        if position == "DEF" and "DEF" not in current_slots:
            return "DEF"
        return "BENCH"

    def connect(self, league_id: str, year: int, espn_s2: str = "", swid: str = "") -> Dict[str, Any]:
        self.league_id = league_id.strip()
        self.year = year
        self.espn_s2 = espn_s2.strip()
        self.swid = swid.strip()

        if not self.league_id:
            self.is_connected = False
            return {
                "status": "demo",
                "message": "Running in Interactive 10-Team Full-PPR Demo Mode. Connect ESPN credentials anytime.",
                "league_name": "Dominator 10-Team Demo League",
                "teams_count": 10
            }

        try:
            from espn_api.football import League
            kwargs = {}
            if self.espn_s2 and self.swid:
                kwargs["espn_s2"] = self.espn_s2
                kwargs["swid"] = self.swid

            self.espn_league_instance = League(league_id=int(self.league_id), year=self.year, **kwargs)
            self.is_connected = True
            return {
                "status": "connected",
                "message": f"Successfully connected to ESPN League: {self.espn_league_instance.settings.name}",
                "league_name": self.espn_league_instance.settings.name,
                "teams_count": len(self.espn_league_instance.teams),
                "scoring_type": "PPR"
            }
        except Exception as e:
            logger.warning(f"ESPN API Connection failed: {e}. Falling back to demo mode.")
            self.is_connected = False
            return {
                "status": "demo_fallback",
                "message": f"ESPN Auth Note: {str(e)}. Switched to 10-Team Mock Engine.",
                "league_name": f"Mock League (ID: {self.league_id})",
                "teams_count": 10
            }

    def get_league_overview(self) -> Dict[str, Any]:
        if self.is_connected and self.espn_league_instance:
            try:
                teams = []
                for idx, t in enumerate(self.espn_league_instance.teams):
                    owner_name = "Manager"
                    owners = getattr(t, 'owners', None)
                    if isinstance(owners, list) and len(owners) > 0:
                        first_owner = owners[0]
                        if isinstance(first_owner, dict):
                            owner_name = first_owner.get('firstName') or first_owner.get('displayName') or 'Manager'
                        elif isinstance(first_owner, str):
                            owner_name = first_owner
                    elif hasattr(t, 'owner') and t.owner:
                        owner_name = str(t.owner)

                    teams.append({
                        "id": getattr(t, 'team_id', idx + 1),
                        "name": getattr(t, 'team_name', f"Team {idx + 1}"),
                        "owner": owner_name,
                        "standing": getattr(t, 'standing', idx + 1),
                        "wins": getattr(t, 'wins', 0),
                        "losses": getattr(t, 'losses', 0),
                        "points_for": getattr(t, 'points_for', 0.0)
                    })
                return {
                    "is_live_espn": True,
                    "league_id": self.league_id,
                    "league_name": getattr(self.espn_league_instance.settings, 'name', 'ESPN League'),
                    "year": self.year,
                    "teams": teams
                }
            except Exception as e:
                logger.error(f"Error fetching live ESPN overview: {e}")

        return {
            "is_live_espn": False,
            "league_id": self.league_id or "DEMO-10PPR",
            "league_name": "Dominator 10-Team Demo League",
            "year": self.year,
            "teams": MOCK_TEAMS
        }

    def get_team_roster(self, team_id: int = 1) -> List[Dict[str, Any]]:
        if self.is_connected and self.espn_league_instance:
            try:
                for t in self.espn_league_instance.teams:
                    if t.team_id == team_id:
                        live_roster = []
                        for p in t.roster:
                            live_roster.append({
                                "id": str(p.playerId),
                                "name": p.name,
                                "position": p.position,
                                "team": p.proTeam,
                                "lineup_slot": p.lineupSlot,
                                "projected_week": p.projected_points,
                                "espn_proj": p.projected_points,
                                "injury_status": p.injuryStatus or "ACTIVE"
                            })
                        return live_roster
            except Exception as e:
                logger.error(f"Error fetching live roster for team {team_id}: {e}")

        return self._mock_rosters.get(team_id, self._mock_rosters[1])

    def get_free_agents(self) -> List[Dict[str, Any]]:
        all_players = nfl_stats_service.get_all_players()
        rostered_ids = set()
        for r_list in self._mock_rosters.values():
            for p in r_list:
                rostered_ids.add(p["id"])

        free_agents = [p for p in all_players if p["id"] not in rostered_ids]
        return free_agents

    def get_live_draft_picks(self) -> List[Dict[str, Any]]:
        """Fetches all completed draft picks from the live ESPN draft room."""
        if not self.is_connected or not self.espn_league_instance:
            return []
        try:
            kwargs = {}
            if self.espn_s2 and self.swid:
                kwargs["espn_s2"] = self.espn_s2
                kwargs["swid"] = self.swid

            from espn_api.football import League
            self.espn_league_instance = League(league_id=int(self.league_id), year=self.year, **kwargs)

            raw_draft = getattr(self.espn_league_instance, 'draft', [])
            picks = []
            for pick in raw_draft:
                p_name = getattr(pick, 'playerName', getattr(pick, 'player_name', ''))
                p_id = getattr(pick, 'playerId', getattr(pick, 'player_id', ''))
                p_team = getattr(pick, 'team', None)
                team_id = getattr(p_team, 'team_id', 1) if p_team else 1
                if p_name:
                    picks.append({
                        "player_name": p_name,
                        "player_id": str(p_id),
                        "team_id": team_id,
                        "round_num": getattr(pick, 'round_num', 1),
                        "round_pick": getattr(pick, 'round_pick', 1)
                    })
            return picks
        except Exception as e:
            logger.error(f"Error fetching live draft picks: {e}")
            return []

    def refresh_all_data(self) -> None:
        """Refresh all team rosters and player data"""
        if self.is_connected and self.espn_league_instance:
            try:
                self.espn_league_instance = League(league_id=int(self.league_id), year=self.year)
                logger.info("Live ESPN data refreshed successfully")
            except Exception as e:
                logger.warning(f"Failed to refresh live ESPN data: {e}")
        else:
            self._mock_rosters = self._generate_initial_mock_rosters()
            logger.info("Mock roster data refreshed successfully")

espn_service = ESPNService()
