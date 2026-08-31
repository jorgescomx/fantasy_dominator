from typing import List, Dict, Any, Optional
import math
from backend.app.services.nfl_stats_service import nfl_stats_service
from backend.app.services.espn_service import MOCK_TEAMS
from backend.app.services.injury_registry import get_injury_details
from backend.app.services.nfl_byes import evaluate_bye_conflicts, get_team_bye_week

class DraftEngine:
    def __init__(self, num_teams: int = 10, total_rounds: int = 15, user_pick: int = 1):
        self.num_teams = num_teams
        self.total_rounds = total_rounds
        self.user_pick = user_pick
        self.current_pick_number = 1
        self.draft_history: List[Dict[str, Any]] = []
        self.team_rosters: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(1, num_teams + 1)}

    def reset(self, user_pick: Optional[int] = None):
        if user_pick is not None:
            self.user_pick = user_pick
        self.current_pick_number = 1
        self.draft_history = []
        self.team_rosters = {i: [] for i in range(1, self.num_teams + 1)}

    def get_current_picking_team(self) -> int:
        """Calculates which team is currently picking in a standard snake draft."""
        round_num = ((self.current_pick_number - 1) // self.num_teams) + 1
        pick_in_round = ((self.current_pick_number - 1) % self.num_teams) + 1
        if round_num % 2 == 1:
            # Odd round: 1, 2, ..., 10
            return pick_in_round
        else:
            # Even round (snake): 10, 9, ..., 1
            return self.num_teams - pick_in_round + 1

    def get_league_teams(self) -> List[Dict[str, Any]]:
        from backend.app.services.espn_service import espn_service
        overview = espn_service.get_league_overview()
        return overview.get("teams", MOCK_TEAMS)

    def get_team_name(self, team_id: int) -> str:
        teams = self.get_league_teams()
        for t in teams:
            if t.get("id") == team_id:
                return t.get("name", f"Team {team_id}")
        return f"Team {team_id}"

    def make_pick(self, player_id: str, team_id: Optional[int] = None) -> Dict[str, Any]:
        """Records a draft pick and advances the draft."""
        all_players = {p["id"]: p for p in nfl_stats_service.get_all_players()}
        player = all_players.get(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        # Ensure not already drafted
        if any(h["player_id"] == player_id for h in self.draft_history):
            raise ValueError(f"Player {player['name']} has already been drafted")

        acting_team = team_id or self.get_current_picking_team()
        round_num = ((self.current_pick_number - 1) // self.num_teams) + 1
        pick_in_round = ((self.current_pick_number - 1) % self.num_teams) + 1

        pick_record = {
            "pick_overall": self.current_pick_number,
            "round": round_num,
            "pick_in_round": pick_in_round,
            "team_id": acting_team,
            "team_name": self.get_team_name(acting_team),
            "player_id": player["id"],
            "player_name": player["name"],
            "position": player["position"],
            "team": player["team"],
            "tier": player["tier"],
            "injury_status": player.get("injury_status", "ACTIVE"),
            "projected_season": player["projected_season"],
            "xfp": player["xfp"]
        }

        self.draft_history.append(pick_record)
        self.team_rosters[acting_team].append(player)
        self.current_pick_number += 1
        return pick_record

    def undo_last_pick(self) -> Optional[Dict[str, Any]]:
        if not self.draft_history:
            return None
        last_pick = self.draft_history.pop()
        self.current_pick_number = max(1, self.current_pick_number - 1)
        team_id = last_pick["team_id"]
        self.team_rosters[team_id] = [p for p in self.team_rosters[team_id] if p["id"] != last_pick["player_id"]]
        return last_pick

    def sync_live_espn_picks(self) -> Dict[str, Any]:
        """Automatically checks ESPN draft room and incorporates all picks made by other managers in real-time."""
        from backend.app.services.espn_service import espn_service
        espn_picks = espn_service.get_live_draft_picks()
        if not espn_picks:
            return {"new_picks_count": 0, "total_picks": len(self.draft_history)}

        all_players = nfl_stats_service.get_all_players()
        name_map = {p["name"].lower().replace(".", "").replace("'", "").replace("-", " ").strip(): p for p in all_players}

        existing_drafted_names = {h["player_name"].lower().replace(".", "").replace("'", "").replace("-", " ").strip() for h in self.draft_history}
        new_picks = 0

        for ep in espn_picks:
            p_name = ep.get("player_name", "")
            norm_name = p_name.lower().replace(".", "").replace("'", "").replace("-", " ").strip()
            if norm_name in existing_drafted_names:
                continue

            match = name_map.get(norm_name)
            if match:
                team_id = ep.get("team_id", self.get_current_picking_team())
                try:
                    self.make_pick(player_id=match["id"], team_id=team_id)
                    existing_drafted_names.add(norm_name)
                    new_picks += 1
                except Exception:
                    pass

        return {"new_picks_count": new_picks, "total_picks": len(self.draft_history)}

    def get_dynamic_vorp_board(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculates Dynamic VORP (Value Over Replacement Player) tailored for 10-team Full PPR.
        Replacement baseline dynamically recalibrates based on remaining undrafted players.
        """
        all_players = nfl_stats_service.get_all_players()
        drafted_ids = {h["player_id"] for h in self.draft_history}
        available_players = [p for p in all_players if p["id"] not in drafted_ids]

        # Positional starter baseline thresholds for 10-team league
        # 10 starters for QB/TE/K/DEF; ~25 starters for RB/WR (including FLEX allocation)
        position_baselines = {
            "QB": 10,
            "RB": 25,
            "WR": 25,
            "TE": 10,
            "K": 10,
            "DEF": 10
        }

        # Get context-adjusted projections for all players
        from backend.app.services.context_continuity_service import get_player_context

        # Calculate replacement level points for each position among remaining/all pool
        replacement_points: Dict[str, float] = {}
        for pos, baseline_rank in position_baselines.items():
            pos_players = [p for p in all_players if p["position"] == pos]
            # Use context-adjusted projections
            pos_players_with_context = []
            for p in pos_players:
                context = get_player_context(p["id"])
                context_factor = context.get("context_certainty", 1.0) if context else 1.0
                adjusted_proj = p.get("projected_season", 0.0) * context_factor
                pos_players_with_context.append((p, adjusted_proj))

            pos_players_sorted = sorted(pos_players_with_context, key=lambda x: x[1], reverse=True)
            if len(pos_players_sorted) >= baseline_rank:
                replacement_points[pos] = pos_players_sorted[baseline_rank - 1][1]
            elif pos_players_sorted:
                replacement_points[pos] = pos_players_sorted[-1][1]
            else:
                replacement_points[pos] = 0.0

        # Group available by position to detect tier cliffs
        pos_available: Dict[str, List[Dict[str, Any]]] = {}
        for p in available_players:
            pos = p["position"]
            if pos not in pos_available:
                pos_available[pos] = []
            pos_available[pos].append(p)

        target_team = team_id or self.get_current_picking_team()
        current_round = ((self.current_pick_number - 1) // self.num_teams) + 1
        roster_held = self.team_rosters.get(target_team, [])

        annotated_board = []
        for p in available_players:
            item = dict(p)
            pos = item["position"]

            # Get context-adjusted projection
            context = get_player_context(p["id"])
            context_factor = context.get("context_certainty", 1.0) if context else 1.0

            # Get injury discount factor
            from backend.app.services.injury_records_service import get_injury_record
            injury = get_injury_record(p["id"])
            injury_factor = injury.get("discount_factor", 1.0) if injury else 1.0

            # Apply both factors: context × injury
            base_projected = p.get("projected_season", 0.0)
            adjusted_projected_season = base_projected * context_factor * injury_factor

            base_pts = replacement_points.get(pos, 0.0)
            item["vorp"] = round(adjusted_projected_season - base_pts, 1)
            item["vorp_per_week"] = round(item["vorp"] / 16.0, 1)
            item["context_certainty"] = context_factor
            item["injury_discount"] = injury_factor
            item["projected_season_adjusted"] = adjusted_projected_season
            item["injury_status"] = injury.get("status", "ACTIVE") if injury else "ACTIVE"
            
            # Tier Cliff Detection
            tier = item["tier"]
            same_tier_remaining = [other for other in pos_available.get(pos, []) if other["tier"] == tier]
            if len(same_tier_remaining) == 1:
                item["tier_cliff_warning"] = f"CRITICAL: Last Tier {tier} {pos} remaining! Tier cliff ahead."
            elif len(same_tier_remaining) == 2:
                item["tier_cliff_warning"] = f"Warning: Only 2 Tier {tier} {pos}s left."
            else:
                item["tier_cliff_warning"] = None

            # Roster Need & Balance Multiplier
            need_info = self._calculate_roster_need(roster_held, pos, current_round)
            
            # Smart Bye Week Conflict Protection
            bye_info = evaluate_bye_conflicts(roster_held, item)
            item["bye_week"] = bye_info["bye_week"] or get_team_bye_week(item.get("team"))
            item["has_bye_conflict"] = bye_info["has_conflict"]
            item["bye_conflict_type"] = bye_info["conflict_type"]
            item["bye_conflict_warning"] = bye_info["warning"]
            item["bye_badge"] = bye_info["badge"]
            item["bye_badge_class"] = bye_info["badge_class"]

            # Combine positional need with bye collision factor
            combined_multiplier = round(need_info["multiplier"] * bye_info["multiplier"], 2)
            item["need_multiplier"] = combined_multiplier

            if bye_info["conflict_type"] == "CLASH":
                item["need_badge"] = bye_info["badge"]
                item["need_badge_class"] = "need-cap"
                item["need_rationale"] = bye_info["warning"]
            elif bye_info["conflict_type"] == "CLUSTER":
                item["need_badge"] = bye_info["badge"]
                item["need_badge_class"] = "need-low"
                item["need_rationale"] = f"{need_info['rationale']} | {bye_info['warning']}"
            else:
                item["need_badge"] = need_info["badge"]
                item["need_badge_class"] = need_info["badge_class"]
                item["need_rationale"] = need_info["rationale"]
            
            # Need-Adjusted Score: Balances raw VORP with structural roster requirements & Bye protection
            item["need_adjusted_score"] = round((item["vorp"] + 50.0) * combined_multiplier, 1)

            annotated_board.append(item)

        # Sort by Balanced Need-Adjusted Score (ensuring balanced roster construction)
        return sorted(annotated_board, key=lambda x: x["need_adjusted_score"], reverse=True)

    def _calculate_roster_need(self, roster: List[Dict[str, Any]], pos: str, current_round: int) -> Dict[str, Any]:
        """
        Calculates position-specific need factor based on current team composition.
        Prevents hoarding 5 WRs/RBs and enforces balanced starting lineups for 10-team PPR.
        """
        positions_held = [p["position"] for p in roster]
        qb_count = positions_held.count("QB")
        rb_count = positions_held.count("RB")
        wr_count = positions_held.count("WR")
        te_count = positions_held.count("TE")
        k_count = positions_held.count("K")
        def_count = positions_held.count("DEF")

        # 1. QUARTERBACK LOGIC
        if pos == "QB":
            if qb_count == 0:
                if current_round in [3, 4, 5]: # Elite QB window (Lamar/Allen/Jayden/Hurts)
                    return {"multiplier": 1.25, "badge": "ELITE QB FIT", "badge_class": "need-high", "rationale": "Perfect window to secure an elite Konami-code rushing QB."}
                elif current_round >= 6:
                    return {"multiplier": 1.15, "badge": "STARTING QB NEED", "badge_class": "need-high", "rationale": "QB1 starter slot is open."}
                else:
                    return {"multiplier": 0.95, "badge": "EARLY QB OPTION", "badge_class": "need-med", "rationale": "Viable early stud, but WR/RB foundation takes slight priority."}
            elif qb_count == 1:
                if current_round >= 11:
                    return {"multiplier": 0.50, "badge": "BACKUP QB DEPTH", "badge_class": "need-low", "rationale": "QB1 already locked. High-upside backup depth only."}
                else:
                    return {"multiplier": 0.25, "badge": "QB SET", "badge_class": "need-low", "rationale": "You already have your starting QB. Prioritize WR/RB/TE."}
            else:
                return {"multiplier": 0.05, "badge": "QB ROOM FULL", "badge_class": "need-cap", "rationale": "Hard cap reached (2 QBs). Do NOT draft more QBs."}

        # 2. TIGHT END LOGIC
        if pos == "TE":
            if te_count == 0:
                if current_round in [2, 3, 4]: # Elite TE window (Bowers / McBride)
                    return {"multiplier": 1.25, "badge": "ELITE TE LEVERAGE", "badge_class": "need-high", "rationale": "Secures huge positional advantage at TE over the league."}
                elif current_round >= 5:
                    return {"multiplier": 1.15, "badge": "STARTING TE NEED", "badge_class": "need-high", "rationale": "Starting TE slot open."}
                else:
                    return {"multiplier": 1.0, "badge": "OPEN TE SLOT", "badge_class": "need-med", "rationale": "Starter TE available."}
            elif te_count == 1:
                if current_round >= 11:
                    return {"multiplier": 0.50, "badge": "BACKUP TE DEPTH", "badge_class": "need-low", "rationale": "Backup TE depth for bye weeks."}
                else:
                    return {"multiplier": 0.25, "badge": "TE SET", "badge_class": "need-low", "rationale": "Starter TE locked. Focus on RB/WR."}
            else:
                return {"multiplier": 0.05, "badge": "TE ROOM FULL", "badge_class": "need-cap", "rationale": "Hard cap reached (2 TEs). Do NOT draft more TEs."}

        # 3. RUNNING BACK LOGIC
        if pos == "RB":
            if rb_count == 0:
                if wr_count >= 2:
                    return {"multiplier": 1.40, "badge": "URGENT RB1 NEED", "badge_class": "need-high", "rationale": "You have 2+ WRs and 0 RBs. Anchor RB urgently required."}
                return {"multiplier": 1.15, "badge": "ANCHOR RB1", "badge_class": "need-high", "rationale": "Secures your starting RB1."}
            elif rb_count == 1:
                if wr_count >= 3:
                    return {"multiplier": 1.35, "badge": "CRITICAL RB2 NEED", "badge_class": "need-high", "rationale": "Need RB2 to balance heavy WR start."}
                return {"multiplier": 1.10, "badge": "STARTING RB2", "badge_class": "need-high", "rationale": "Completes your starting RB backfield."}
            elif rb_count == 2:
                if wr_count < 2:
                    return {"multiplier": 0.70, "badge": "WR TAKES PRIORITY", "badge_class": "need-low", "rationale": "You have 2 RBs. WR starter slots need immediate attention."}
                return {"multiplier": 1.0, "badge": "FLEX / RB3 DEPTH", "badge_class": "need-med", "rationale": "Solid FLEX starter or premium bench depth."}
            elif rb_count in [3, 4]:
                if wr_count < 3 or qb_count == 0 or te_count == 0:
                    return {"multiplier": 0.60, "badge": "BALANCE OTHER SLOTS", "badge_class": "need-low", "rationale": "RBs well-stocked. Address remaining starting slots."}
                return {"multiplier": 0.75, "badge": "RB BENCH VALUE", "badge_class": "need-low", "rationale": "High-upside contingency/handcuff depth."}
            else: # 5+ RBs
                return {"multiplier": 0.10, "badge": "RB ROOM SATURATED", "badge_class": "need-cap", "rationale": "Maximum RB capacity (5+ RBs). Draft other positions."}

        # 4. WIDE RECEIVER LOGIC
        if pos == "WR":
            if wr_count == 0:
                if rb_count >= 2:
                    return {"multiplier": 1.40, "badge": "URGENT WR1 NEED", "badge_class": "need-high", "rationale": "You have 2+ RBs and 0 WRs. Target Alpha WR urgently."}
                return {"multiplier": 1.15, "badge": "ALPHA WR1", "badge_class": "need-high", "rationale": "Foundational Alpha target earner."}
            elif wr_count == 1:
                if rb_count >= 3:
                    return {"multiplier": 1.35, "badge": "CRITICAL WR2 NEED", "badge_class": "need-high", "rationale": "Need WR2 to balance heavy RB start."}
                return {"multiplier": 1.10, "badge": "STARTING WR2", "badge_class": "need-high", "rationale": "Completes starting WR duo."}
            elif wr_count == 2:
                if rb_count < 2:
                    return {"multiplier": 0.70, "badge": "RB TAKES PRIORITY", "badge_class": "need-low", "rationale": "You have 2 WRs. RB starting slots need attention."}
                return {"multiplier": 1.0, "badge": "PPR FLEX / WR3", "badge_class": "need-med", "rationale": "High-volume PPR FLEX option."}
            elif wr_count in [3, 4]:
                if rb_count < 3 or qb_count == 0 or te_count == 0:
                    return {"multiplier": 0.60, "badge": "BALANCE OTHER SLOTS", "badge_class": "need-low", "rationale": "WRs well-stocked. Address remaining starting slots."}
                return {"multiplier": 0.75, "badge": "WR BENCH VALUE", "badge_class": "need-low", "rationale": "High-upside bench WR."}
            else: # 5+ WRs
                return {"multiplier": 0.10, "badge": "WR ROOM SATURATED", "badge_class": "need-cap", "rationale": "Maximum WR capacity (5+ WRs). Draft other positions."}

        # 5. KICKER & DEFENSE LOGIC
        if pos in ["K", "DEF"]:
            if current_round < 14:
                return {"multiplier": 0.05, "badge": "DO NOT DRAFT YET", "badge_class": "need-cap", "rationale": "Never draft K/DEF before rounds 14-15."}
            else:
                existing = k_count if pos == "K" else def_count
                if existing == 0:
                    return {"multiplier": 1.10, "badge": f"FILL {pos} STARTER", "badge_class": "need-high", "rationale": f"Draft starting {pos} for Round {current_round}."}
                else:
                    return {"multiplier": 0.05, "badge": f"{pos} FULL", "badge_class": "need-cap", "rationale": f"Never draft backup {pos}s."}

        return {"multiplier": 1.0, "badge": "STANDARD", "badge_class": "need-med", "rationale": "Standard pick."}




    def _calculate_picks_until_turn(self, current_overall: int, user_slot: int) -> int:
        if current_overall > self.num_teams * self.total_rounds:
            return 0
        for offset in range(0, self.num_teams * 2):
            target_pick = current_overall + offset
            target_round = ((target_pick - 1) // self.num_teams) + 1
            target_in_round = ((target_pick - 1) % self.num_teams) + 1
            team = target_in_round if (target_round % 2 == 1) else (self.num_teams - target_in_round + 1)
            if team == user_slot:
                return offset
        return 0

    def _sniff_opponent_needs(self) -> List[Dict[str, Any]]:
        """Identifies which positions opponent teams picking before your next turn desperately need."""
        threats = []

        # Calculate how many picks until user's turn from current pick
        picks_until_user = self._calculate_picks_until_turn(self.current_pick_number, self.user_pick)
        # Show all opponents until (but not including) user's next turn
        picks_to_check = min(8, picks_until_user)

        for offset in range(picks_to_check):
            p_num = self.current_pick_number + offset
            rnd = ((p_num - 1) // self.num_teams) + 1
            pin_rnd = ((p_num - 1) % self.num_teams) + 1
            t_id = pin_rnd if (rnd % 2 == 1) else (self.num_teams - pin_rnd + 1)
            
            if t_id == self.user_pick:
                continue
                
            roster = self.team_rosters.get(t_id, [])
            positions_held = [p["position"] for p in roster]
            
            # Simple need evaluation: if team has 0 WRs and 2 RBs, they have an acute WR need
            rb_count = positions_held.count("RB")
            wr_count = positions_held.count("WR")
            qb_count = positions_held.count("QB")
            te_count = positions_held.count("TE")

            primary_need = "FLEX / Best Available"
            if wr_count == 0 and rb_count > 0:
                primary_need = "High Target WR"
            elif rb_count == 0 and wr_count > 0:
                primary_need = "Anchor RB"
            elif qb_count == 0 and rnd >= 5:
                primary_need = "Elite QB"
            elif te_count == 0 and rnd >= 4:
                primary_need = "Top Tier TE"

            threats.append({
                "team_id": t_id,
                "team_name": self.get_team_name(t_id),
                "pick_number": p_num,
                "round": rnd,
                "picks_away": offset + 1,
                "urgent_need": primary_need
            })
        return threats

    def get_draft_state(self) -> Dict[str, Any]:
        """Returns comprehensive draft telemetry for the frontend."""
        current_team = self.get_current_picking_team()
        round_num = ((self.current_pick_number - 1) // self.num_teams) + 1
        pick_in_round = ((self.current_pick_number - 1) % self.num_teams) + 1
        picks_until_user = self._calculate_picks_until_turn(self.current_pick_number, self.user_pick)
        opponent_threats = self._sniff_opponent_needs()
        board = self.get_dynamic_vorp_board(team_id=current_team)
        top_balanced_pick = board[0] if board else None
        league_teams = self.get_league_teams()

        return {
            "current_pick_number": self.current_pick_number,
            "round": round_num,
            "pick_in_round": pick_in_round,
            "current_team_id": current_team,
            "current_team_name": self.get_team_name(current_team),
            "is_user_turn": (current_team == self.user_pick),
            "user_pick": self.user_pick,
            "user_team_name": self.get_team_name(self.user_pick),
            "picks_until_user": picks_until_user,
            "opponent_threats": opponent_threats,
            "draft_history": self.draft_history,
            "user_roster": self.team_rosters.get(self.user_pick, []),
            "all_team_rosters": self.team_rosters,
            "top_balanced_recommendation": top_balanced_pick,
            "recommended_board": board,
            "league_teams": league_teams
        }

    def get_player_rating_breakdown(self, player_id: str) -> Dict[str, Any]:
        """Generates full analytical explanation behind a player's VORP and rating."""
        all_board = self.get_dynamic_vorp_board()
        player = next((p for p in all_board if p["id"] == player_id), None)
        if not player:
            player = nfl_stats_service.get_player(player_id)
            if not player:
                raise ValueError(f"Player {player_id} not found")

        pos = player["position"]
        pos_rankings = [p for p in all_board if p["position"] == pos]
        pos_rank = next((idx + 1 for idx, p in enumerate(pos_rankings) if p["id"] == player_id), 1)

        position_baselines = {"QB": 10, "RB": 25, "WR": 25, "TE": 10, "K": 10, "DEF": 10}
        baseline_num = position_baselines.get(pos, 10)

        # Get context and metrics data for three-column display
        from backend.app.services.context_continuity_service import get_player_context, get_player_metrics

        player_context = get_player_context(player_id)
        player_metrics_data = get_player_metrics(player_id)

        context_certainty = 1.0
        if player_context:
            context_certainty = player_context.get("context_certainty", 1.0)

        # Build detailed metric cards with context adjustment
        metrics = []

        # Context Certainty Card (if changed)
        if player_context and context_certainty < 1.0:
            changes = player_context.get("context_changes", {})
            warnings = []
            if changes.get("qb_changed"):
                warnings.append("QB changed")
            if changes.get("oc_changed"):
                warnings.append("OC changed")
            if changes.get("hc_changed"):
                warnings.append("HC changed")

            metrics.append({
                "metric": "Context Continuity",
                "value": f"{int(context_certainty * 100)}%",
                "rating": "Stable" if context_certainty >= 0.9 else ("Adjusted" if context_certainty >= 0.7 else "Uncertain"),
                "explanation": f"Environmental stability: {', '.join(warnings) if warnings else 'No changes'}. Metrics adjusted for {int((1 - context_certainty) * 100)}% environmental risk.",
                "context_changes": changes
            })

        # 1. Expected Fantasy Points (xFP) - THREE COLUMN FORMAT
        xfp_projected = player.get("xfp", 10.0)
        xfp_recalculated = xfp_projected * context_certainty if player_metrics_data else xfp_projected

        metrics.append({
            "metric": "Expected Fantasy Points (xFP)",
            "projected": f"{xfp_projected} xFP/gm (2025)",
            "context_factor": f"{context_certainty}",
            "recalculated": f"{round(xfp_recalculated, 2)} xFP/gm (2026)",
            "rating": "Elite" if xfp_recalculated >= 18.0 else ("Strong" if xfp_recalculated >= 14.0 else "Solid"),
            "explanation": "Simulates expected fantasy scoring based on granular play-by-play volume. 2025 baseline adjusted for QB/OC/HC changes."
        })

        # 2. Route Participation % - THREE COLUMN FORMAT
        if pos in ["WR", "TE", "RB"]:
            route_pct_projected = player.get("route_participation", 0.0)
            route_pct_recalculated = route_pct_projected * context_certainty

            metrics.append({
                "metric": "Route Participation Rate",
                "projected": f"{int(route_pct_projected * 100)}% (2025)",
                "context_factor": f"{context_certainty}",
                "recalculated": f"{int(route_pct_recalculated * 100)}% (2026)",
                "rating": "Alpha (90%+)" if route_pct_recalculated >= 0.90 else ("Full-Time (80%+)" if route_pct_recalculated >= 0.80 else "Part-Time"),
                "explanation": "Percentage of team passing plays. Adjusted for QB change impact on target distribution."
            })

        # 3. High-Value Touches - THREE COLUMN FORMAT
        hv_projected = player.get("high_value_touches", 0.0)
        hv_recalculated = hv_projected * context_certainty

        metrics.append({
            "metric": "High-Value Touches (HVTs)",
            "projected": f"{round(hv_projected, 2)}/game (2025)",
            "context_factor": f"{context_certainty}",
            "recalculated": f"{round(hv_recalculated, 2)}/game (2026)",
            "rating": "Elite" if hv_recalculated >= 5.0 else ("High" if hv_recalculated >= 3.5 else "Moderate"),
            "explanation": "Targets + carries in scoring zone. Adjusted for offensive system changes."
        })

        # 4. Red Zone Share - THREE COLUMN FORMAT
        rz_projected = player.get("red_zone_share", 0.0)
        rz_recalculated = rz_projected * context_certainty

        metrics.append({
            "metric": "Red Zone Opportunity Share",
            "projected": f"{int(rz_projected * 100)}% (2025)",
            "context_factor": f"{context_certainty}",
            "recalculated": f"{int(rz_recalculated * 100)}% (2026)",
            "rating": "Dominant" if rz_recalculated >= 0.35 else ("Strong" if rz_recalculated >= 0.25 else "Moderate"),
            "explanation": "Share of team RZ opportunities. Adjusted for coaching staff changes."
        })

        # 5. Vegas Environment
        implied = player.get("implied_team_pts", 22.0)
        metrics.append({
            "metric": "Vegas Implied Team Total",
            "value": f"{implied} pts (Spread: {player.get('spread', 0.0)})",
            "rating": "High-Powered" if implied >= 25.0 else "Average",
            "explanation": "Betting market consensus on offensive scoring volume. High implied totals create 15-30% more red zone visits and scoring drives."
        })

        # 6. Injury Intelligence & Availability Analysis
        injury_info = None
        inj_details = get_injury_details(player["name"], player.get("injury_status"), player.get("injury_body_part"), player.get("injury_notes"))
        if inj_details:
            injury_info = {
                "status": inj_details["status"],
                "type": inj_details["type"],
                "time_away": inj_details["timeline"],
                "notes": inj_details["notes"],
                "impact_summary": inj_details["impact_summary"]
            }

            rating_label = "Monitoring" if inj_details["status"] in ["QUESTIONABLE", "Q"] else "Availability Alert"
            explanation = f"{inj_details['type']} — {inj_details['timeline']}. {inj_details['impact_summary']}."
            metrics.insert(0, {
                "metric": "Injury & Availability Status",
                "value": inj_details["status"],
                "rating": rating_label,
                "explanation": explanation
            })

        # 7. Bye Week & Roster Schedule Compatibility
        current_team = self.get_current_picking_team()
        current_round = ((self.current_pick_number - 1) // self.num_teams) + 1
        roster_held = self.team_rosters.get(current_team, [])
        bye_eval = evaluate_bye_conflicts(roster_held, player)
        cand_bye = bye_eval["bye_week"] or player.get("bye_week") or get_team_bye_week(player.get("team"))
        
        if bye_eval["conflict_type"] == "CLASH":
            bye_rating = "Critical Clash"
            bye_exp = bye_eval["warning"]
        elif bye_eval["conflict_type"] == "CLUSTER":
            bye_rating = "Cluster Alert"
            bye_exp = bye_eval["warning"]
        else:
            bye_rating = "No Conflict"
            bye_exp = f"NFL Bye Week {cand_bye} creates zero scheduling collisions with your drafted roster."

        metrics.append({
            "metric": "NFL Bye Week Compatibility",
            "value": f"Week {cand_bye}" if cand_bye else "N/A",
            "rating": bye_rating,
            "explanation": bye_exp
        })

        # Roster Need Analysis for Current Team
        need_info = self._calculate_roster_need(roster_held, pos, current_round)

        # Generate contextual scouting takeaway
        vorp_val = player.get("vorp", 0.0)
        vorp_wk = player.get("vorp_per_week", 0.0)

        takeaway = (
            f"{player['name']} is rated as the #{pos_rank} {pos} (Tier {player.get('tier', 1)}) in our 10-Team Full-PPR model. "
            f"With a Dynamic VORP of +{vorp_val} pts (+{vorp_wk} pts/week above the #{baseline_num} starter cutoff), "
            f"their elite volume profile ({player.get('xfp', 0.0)} xFP) and {player.get('archetype', 'Role Player')} role "
            f"provides high positional leverage. "
            f"Team Construction Fit: {need_info['badge']} — {need_info['rationale']}"
        )

        return {
            "player": player,
            "position_rank": pos_rank,
            "baseline_threshold": baseline_num,
            "vorp_points": vorp_val,
            "vorp_per_week": vorp_wk,
            "roster_need": need_info,
            "scouting_takeaway": takeaway,
            "metrics": metrics,
            "injury_info": injury_info
        }

    def refresh_available_players(self) -> None:
        """Refresh player data - called when teams/rosters are updated"""
        nfl_stats_service.refresh_players()

draft_engine = DraftEngine(user_pick=1)
