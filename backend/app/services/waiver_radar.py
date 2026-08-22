from typing import List, Dict, Any, Optional
from backend.app.services.nfl_stats_service import nfl_stats_service
from backend.app.services.espn_service import espn_service

class WaiverRadar:
    def __init__(self):
        pass

    def scan_breakout_arbitrage(self) -> List[Dict[str, Any]]:
        """
        Scans all available free agents for leading indicators and market mispricing.
        Identifies high-value breakouts before they reflect in public consensus or box scores.
        """
        free_agents = espn_service.get_free_agents()
        breakout_targets = []

        for p in free_agents:
            full_data = nfl_stats_service.get_player(p["id"]) or p
            route_pct = full_data.get("route_participation", 0.0)
            hv_touches = full_data.get("high_value_touches", 0.0)
            rz_share = full_data.get("red_zone_share", 0.0)
            ownership = full_data.get("espn_ownership", 0.0)
            delta = full_data.get("arbitrage_delta", 0.0)
            pos = full_data.get("position", "")

            # Calculate composite Breakout Signal Index (0 to 100)
            # High weight on Route % (WR/TE), High-Value Touches (RB), and Arbitrage Delta
            score = 0.0
            signals = []

            if pos in ["WR", "TE"] and route_pct >= 0.80:
                score += 35.0
                signals.append(f"Elite Route Participation ({int(route_pct*100)}%)")
            elif pos in ["WR", "TE"] and route_pct >= 0.70:
                score += 20.0
                signals.append(f"Strong Route Participation ({int(route_pct*100)}%)")

            if hv_touches >= 3.0:
                score += 30.0
                signals.append(f"High-Value Touches: {hv_touches}/gm (Red Zone + Targets)")
            elif hv_touches >= 2.0:
                score += 15.0
                signals.append(f"Emerging High-Value Touch Share ({hv_touches}/gm)")

            if rz_share >= 0.20:
                score += 20.0
                signals.append(f"High Red Zone Opportunity Share ({int(rz_share*100)}%)")

            if delta >= 2.0:
                score += 25.0
                signals.append(f"ESPN Under-Projecting by +{delta} pts/week")

            # Bonus for low ownership (high arbitrage opportunity)
            if ownership <= 50.0:
                score += 10.0

            composite_score = min(100.0, round(score, 1))

            if composite_score >= 40.0 or delta >= 1.5:
                target_record = dict(full_data)
                target_record["breakout_score"] = composite_score
                target_record["breakout_signals"] = signals
                target_record["urgency"] = "HIGH PRIORITY" if composite_score >= 65 else "MODERATE TARGET"
                breakout_targets.append(target_record)

        return sorted(breakout_targets, key=lambda x: x["breakout_score"], reverse=True)

    def evaluate_drop_candidates(self, user_team_id: int = 1) -> List[Dict[str, Any]]:
        """
        Evaluates user's roster for potential drop candidates to free up bench spots for high-upside waiver targets.
        """
        roster = espn_service.get_team_roster(user_team_id)
        drop_candidates = []

        for p in roster:
            full_data = nfl_stats_service.get_player(p.get("id")) or p
            pos = full_data.get("position", "")
            route_pct = full_data.get("route_participation", 0.0)
            proj = full_data.get("contextual_proj", full_data.get("projected_week", 10.0))
            ownership = full_data.get("espn_ownership", 100.0)

            # Do not recommend dropping studs or starters
            if ownership > 90.0 or proj >= 15.0:
                continue

            # Drop vulnerability metrics
            reasons = []
            drop_score = 0.0

            if pos in ["WR", "TE"] and route_pct < 0.60:
                drop_score += 40.0
                reasons.append(f"Low route participation ({int(route_pct*100)}%)")
            if proj < 10.0:
                drop_score += 30.0
                reasons.append(f"Sub-10 PPG baseline projection ({proj} pts)")
            if full_data.get("high_value_touches", 0.0) < 1.5:
                drop_score += 20.0
                reasons.append("Minimal red zone and high-value touch involvement")

            if drop_score >= 30.0:
                candidate = dict(full_data)
                candidate["drop_vulnerability_score"] = drop_score
                candidate["drop_reasons"] = reasons
                drop_candidates.append(candidate)

        return sorted(drop_candidates, key=lambda x: x["drop_vulnerability_score"], reverse=True)

waiver_radar = WaiverRadar()
