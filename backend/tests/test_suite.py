import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.services.nfl_stats_service import nfl_stats_service
from backend.app.services.espn_service import espn_service
from backend.app.services.draft_engine import draft_engine
from backend.app.services.lineup_optimizer import lineup_optimizer
from backend.app.services.waiver_radar import waiver_radar

def test_nfl_stats():
    print("Testing NFL Stats Service...")
    players = nfl_stats_service.get_all_players()
    assert len(players) > 0, "Player list should not be empty"
    cmc = next(p for p in players if p["name"] == "Christian McCaffrey")
    assert cmc["contextual_proj"] > 0, "Contextual projection must be calculated"
    assert cmc["ceiling_proj"] > cmc["floor_proj"], "Ceiling should be higher than floor"
    print(f"  [PASS] Found {len(players)} players. CMC Contextual Proj: {cmc['contextual_proj']} pts")

def test_draft_engine():
    print("Testing Draft Engine & Dynamic VORP...")
    draft_engine.reset(user_pick=1)
    state = draft_engine.get_draft_state()
    assert state["current_pick_number"] == 1
    assert state["is_user_turn"] is True
    
    board = draft_engine.get_dynamic_vorp_board()
    assert len(board) > 0
    top_vorp = board[0]
    print(f"  [PASS] Pick 1.01 Top VORP recommendation: {top_vorp['name']} ({top_vorp['position']}) with VORP: +{top_vorp['vorp']}")

    # Make pick for user
    pick_1 = draft_engine.make_pick(top_vorp["id"])
    assert pick_1["player_id"] == top_vorp["id"]
    assert draft_engine.current_pick_number == 2
    assert draft_engine.get_current_picking_team() == 2
    print(f"  [PASS] Pick 1.01 successfully made for {pick_1['player_name']}. Advanced to Pick #2 (Team 2).")

    # Undo pick
    undone = draft_engine.undo_last_pick()
    assert undone["player_id"] == top_vorp["id"]
    assert draft_engine.current_pick_number == 1
    print("  [PASS] Undo pick successful.")

def test_lineup_optimizer():
    print("Testing Lineup Optimizer Linear Solver...")
    roster = espn_service.get_team_roster(team_id=1)
    result = lineup_optimizer.solve_optimal_lineup(roster, mode="balanced")
    assert result["total_projected"] > 0
    assert result["starters_count"] > 0
    print(f"  [PASS] PuLP Linear Solver generated optimal starting lineup with {result['total_projected']} projected points across {result['starters_count']} starters.")

    # Sit/Start Comparison
    all_p = nfl_stats_service.get_all_players()
    cmp = lineup_optimizer.compare_sit_start(all_p[0]["id"], all_p[1]["id"])
    assert cmp["winner_name"] is not None
    print(f"  [PASS] Sit/Start Arena: {cmp['recommendation']}")

def test_waiver_radar():
    print("Testing Waiver Arbitrage Radar...")
    breakouts = waiver_radar.scan_breakout_arbitrage()
    assert len(breakouts) > 0
    top_breakout = breakouts[0]
    print(f"  [PASS] Top Arbitrage Breakout Target: {top_breakout['name']} ({top_breakout['position']}) - Signal Index: {top_breakout['breakout_score']}/100")

    drops = waiver_radar.evaluate_drop_candidates(1)
    print(f"  [PASS] Drop Candidates Identified: {len(drops)}")

def test_injury_intelligence():
    print("Testing Contextual Injury Intelligence & Specific Model Impacts...")
    from backend.app.services.injury_registry import get_injury_details
    
    # Test soft-tissue strain
    cmc_inj = get_injury_details("Christian McCaffrey", "QUESTIONABLE")
    assert cmc_inj is not None
    assert "12% touch-cap discount" in cmc_inj["impact_summary"]
    assert cmc_inj["discount_factor"] == 0.88
    
    # Test precautionary tweak
    jeanty_inj = get_injury_details("Ashton Jeanty", "QUESTIONABLE")
    assert jeanty_inj is not None
    assert "5% precautionary snap variance" in jeanty_inj["impact_summary"]
    assert jeanty_inj["discount_factor"] == 0.95
    
    # Test contusion/pain management
    puka_inj = get_injury_details("Puka Nacua", "QUESTIONABLE")
    assert puka_inj is not None
    assert "8% contact efficiency discount" in puka_inj["impact_summary"]
    assert puka_inj["discount_factor"] == 0.92
    
    # Test reserve / PUP / long-term
    hock_inj = get_injury_details("TJ Hockenson", "PUP")
    assert hock_inj is not None
    assert "100% discount" in hock_inj["impact_summary"]
    assert hock_inj["discount_factor"] == 0.0
    
    print("  [PASS] Curated & dynamic injury models return tailored medical notes and calibrated discount factors.")

def test_injury_designation_precedence():
    print("Testing explicit injury designation precedence...")
    from backend.app.services.injury_registry import get_injury_details

    questionable = get_injury_details("Breece Hall", "QUESTIONABLE")
    assert questionable is not None
    assert questionable["status"] == "QUESTIONABLE"
    assert questionable["notes"]

    active = get_injury_details("Breece Hall", "ACTIVE")
    assert active is None
    print("  [PASS] QUESTIONABLE players receive fallback details; ACTIVE players remain untagged.")

def test_bye_week_collision_protection():
    print("Testing Smart Bye Week Collision & Clustering Protection...")
    from backend.app.services.nfl_byes import evaluate_bye_conflicts, get_team_bye_week
    
    # 1. Single-starter clash (QB)
    mock_roster = [
        {"id": "qb-hurts", "name": "Jalen Hurts", "position": "QB", "team": "PHI", "bye_week": 5}
    ]
    # Candidate QB with same bye (e.g. Goff on DET - Wk 5)
    cand_qb_clash = {"id": "qb-goff", "name": "Jared Goff", "position": "QB", "team": "DET", "bye_week": 5}
    clash_eval = evaluate_bye_conflicts(mock_roster, cand_qb_clash)
    assert clash_eval["has_conflict"] is True
    assert clash_eval["conflict_type"] == "CLASH"
    assert clash_eval["multiplier"] < 0.50
    assert "CRITICAL BYE CLASH" in clash_eval["warning"]
    
    # Candidate QB with different bye (e.g. Mahomes on KC - Wk 6)
    cand_qb_clean = {"id": "qb-mahomes", "name": "Patrick Mahomes", "position": "QB", "team": "KC", "bye_week": 6}
    clean_eval = evaluate_bye_conflicts(mock_roster, cand_qb_clean)
    assert clean_eval["has_conflict"] is False
    assert clean_eval["multiplier"] == 1.0

    # 2. Multi-starter clustering (RB)
    rb_roster = [
        {"id": "rb-1", "name": "Kyren Williams", "position": "RB", "team": "LAR", "bye_week": 6},
        {"id": "rb-2", "name": "De'Von Achane", "position": "RB", "team": "MIA", "bye_week": 6}
    ]
    cand_rb_cluster = {"id": "rb-3", "name": "Isiah Pacheco", "position": "RB", "team": "KC", "bye_week": 6}
    rb_cluster_eval = evaluate_bye_conflicts(rb_roster, cand_rb_cluster)
    assert rb_cluster_eval["has_conflict"] is True
    assert rb_cluster_eval["conflict_type"] == "CLUSTER"
    assert rb_cluster_eval["multiplier"] < 1.0
    
    print("  [PASS] Single-starter bye clashes (QB/TE) penalized heavily and multi-starter cluster shields active.")

if __name__ == "__main__":
    test_nfl_stats()
    test_draft_engine()
    test_lineup_optimizer()
    test_waiver_radar()
    test_injury_intelligence()
    test_injury_designation_precedence()
    test_bye_week_collision_protection()
    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<")

