from typing import List, Dict, Any, Optional
import pulp
from backend.app.services.nfl_stats_service import nfl_stats_service

class LineupOptimizer:
    def __init__(self):
        pass

    def solve_optimal_lineup(
        self, 
        roster_pool: List[Dict[str, Any]], 
        mode: str = "balanced" # "balanced", "ceiling", "floor"
    ) -> Dict[str, Any]:
        """
        Runs Integer Linear Programming (ILP) via PuLP to determine the mathematically optimal
        starting lineup for a 10-team Full-PPR roster (1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX [RB/WR/TE], 1 K, 1 DEF).
        """
        if not roster_pool:
            return {"error": "Roster pool is empty", "starters": [], "bench": [], "total_projected": 0.0}

        # Determine metric key based on mode
        metric_key = "contextual_proj"
        if mode == "ceiling":
            metric_key = "ceiling_proj"
        elif mode == "floor":
            metric_key = "floor_proj"

        # Filter active players and normalize data
        players = []
        for p in roster_pool:
            # Enriched data if partial
            full_data = nfl_stats_service.get_player(p.get("id")) or p
            item = dict(full_data)
            item["score"] = item.get(metric_key, item.get("projected_week", 10.0))
            players.append(item)

        prob = pulp.LpProblem("Fantasy_Lineup_Optimization", pulp.LpMaximize)

        # Decision variables: x[i] = 1 if player i starts, 0 otherwise
        # flex[i] = 1 if player i is placed in the FLEX slot
        x = {i: pulp.LpVariable(f"start_{i}", cat="Binary") for i in range(len(players))}
        flex = {i: pulp.LpVariable(f"flex_{i}", cat="Binary") for i in range(len(players))}

        # Objective Function: Maximize sum of scores for starting players
        prob += pulp.lpSum([players[i]["score"] * x[i] for i in range(len(players))])

        # Positional constraints
        qbs = [i for i, p in enumerate(players) if p["position"] == "QB"]
        rbs = [i for i, p in enumerate(players) if p["position"] == "RB"]
        wrs = [i for i, p in enumerate(players) if p["position"] == "WR"]
        tes = [i for i, p in enumerate(players) if p["position"] == "TE"]
        ks = [i for i, p in enumerate(players) if p["position"] == "K"]
        defs = [i for i, p in enumerate(players) if p["position"] == "DEF"]
        flex_eligible = [i for i, p in enumerate(players) if p["position"] in ["RB", "WR", "TE"]]

        # Slots:
        # QB == 1 (if available)
        if qbs:
            prob += pulp.lpSum([x[i] for i in qbs]) == min(1, len(qbs))
        
        # K == 1 (if available)
        if ks:
            prob += pulp.lpSum([x[i] for i in ks]) == min(1, len(ks))

        # DEF == 1 (if available)
        if defs:
            prob += pulp.lpSum([x[i] for i in defs]) == min(1, len(defs))

        # Flex constraint: Exactly 1 FLEX starter among eligible players
        if flex_eligible:
            prob += pulp.lpSum([flex[i] for i in flex_eligible]) == min(1, len(flex_eligible))

        for i in range(len(players)):
            # A player can only be in FLEX if they are also starting
            prob += flex[i] <= x[i]
            # If not flex eligible, flex is 0
            if i not in flex_eligible:
                prob += flex[i] == 0

        # Dedicated RB starters = 2 + flex
        if rbs:
            prob += pulp.lpSum([x[i] - flex[i] for i in rbs]) <= 2
            prob += pulp.lpSum([x[i] for i in rbs]) <= min(3, len(rbs))

        # Dedicated WR starters = 2 + flex
        if wrs:
            prob += pulp.lpSum([x[i] - flex[i] for i in wrs]) <= 2
            prob += pulp.lpSum([x[i] for i in wrs]) <= min(3, len(wrs))

        # Dedicated TE starters = 1 + flex
        if tes:
            prob += pulp.lpSum([x[i] - flex[i] for i in tes]) <= 1
            prob += pulp.lpSum([x[i] for i in tes]) <= min(2, len(tes))

        # Total starters <= 9
        prob += pulp.lpSum([x[i] for i in range(len(players))]) <= min(9, len(players))

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=0))

        # Extract results
        starters = []
        bench = []
        total_score = 0.0

        for i, p in enumerate(players):
            is_starting = (pulp.value(x[i]) or 0) > 0.5
            is_flex = (pulp.value(flex[i]) or 0) > 0.5
            
            p_res = dict(p)
            if is_starting:
                if is_flex:
                    p_res["assigned_slot"] = "FLEX"
                else:
                    p_res["assigned_slot"] = p["position"]
                starters.append(p_res)
                total_score += p_res["score"]
            else:
                p_res["assigned_slot"] = "BENCH"
                bench.append(p_res)

        # Sort starters by slot hierarchy: QB, RB, RB, WR, WR, TE, FLEX, K, DEF
        slot_order = {"QB": 1, "RB": 2, "WR": 3, "TE": 4, "FLEX": 5, "K": 6, "DEF": 7, "BENCH": 8}
        starters.sort(key=lambda item: slot_order.get(item["assigned_slot"], 9))
        bench.sort(key=lambda item: item.get("score", 0), reverse=True)

        return {
            "mode": mode,
            "total_projected": round(total_score, 1),
            "starters_count": len(starters),
            "bench_count": len(bench),
            "starters": starters,
            "bench": bench
        }

    def compare_sit_start(self, player_id_a: str, player_id_b: str) -> Dict[str, Any]:
        """Performs advanced contextual head-to-head sit/start comparison."""
        p_a = nfl_stats_service.get_player(player_id_a)
        p_b = nfl_stats_service.get_player(player_id_b)
        
        if not p_a or not p_b:
            raise ValueError("Invalid player IDs provided for comparison")

        score_a = p_a["contextual_proj"]
        score_b = p_b["contextual_proj"]
        delta = round(abs(score_a - score_b), 1)

        winner = p_a if score_a >= score_b else p_b
        loser = p_b if score_a >= score_b else p_a
        win_margin_pct = round((delta / max(0.1, min(score_a, score_b))) * 100, 1)

        reasons = []
        if winner["xfp"] > loser["xfp"]:
            reasons.append(f"Higher base volume & Expected Fantasy Points ({winner['xfp']} xFP vs {loser['xfp']} xFP)")
        if winner.get("route_participation", 0) > loser.get("route_participation", 0):
            reasons.append(f"Superior Route Participation ({int(winner['route_participation']*100)}% vs {int(loser['route_participation']*100)}%)")
        if winner.get("implied_team_pts", 20) > loser.get("implied_team_pts", 20):
            reasons.append(f"More favorable Vegas Implied Team Total ({winner['implied_team_pts']} pts vs {loser['implied_team_pts']} pts)")
        if winner.get("opp_rank_vs_pos", 16) > loser.get("opp_rank_vs_pos", 16):
            reasons.append(f"Softer matchup defense rank (#{winner['opp_rank_vs_pos']} vs #{loser['opp_rank_vs_pos']})")
        if not reasons:
            reasons.append("Better contextual efficiency and touchdown probability in current game script.")

        return {
            "winner_id": winner["id"],
            "winner_name": winner["name"],
            "loser_id": loser["id"],
            "loser_name": loser["name"],
            "delta_points": delta,
            "win_margin_pct": win_margin_pct,
            "recommendation": f"START {winner['name']} over {loser['name']} (+{delta} pts projected)",
            "key_advantages": reasons,
            "player_a": p_a,
            "player_b": p_b
        }

lineup_optimizer = LineupOptimizer()
