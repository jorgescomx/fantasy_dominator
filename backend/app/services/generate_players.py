"""
Script to expand INITIAL_PLAYERS in nfl_stats_service.py with:
- All 32 NFL Starting Quarterbacks
- 60+ Running Backs (Starters, Handcuffs, 2025 Rookies)
- 75+ Wide Receivers (Alphas, Slots, Deep Threats, 2025 Rookies)
- 30+ Tight Ends (Elite T1/T2, Sleepers, 2025 Rookies)
- 20+ Starting Kickers
- 20+ NFL Team Defenses
"""

import json

EXPANDED_PLAYERS = [
    # ================= 32 NFL STARTING QUARTERBACKS =================
    {
        "id": "qb-lamar", "name": "Lamar Jackson", "position": "QB", "team": "BAL",
        "adp": 32.0, "tier": 1, "projected_season": 375.0, "projected_week": 23.4,
        "xfp": 23.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.05, "injury_status": "ACTIVE", "espn_ownership": 100.0, "espn_proj": 22.8,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 28, "archetype": "Elite Dual-Threat / MVP Ceiling"
    },
    {
        "id": "qb-allen", "name": "Josh Allen", "position": "QB", "team": "BUF",
        "adp": 34.0, "tier": 1, "projected_season": 370.0, "projected_week": 23.1,
        "xfp": 22.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 100.0, "espn_proj": 22.5,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 26, "archetype": "Goal-Line TD Juggernaut"
    },
    {
        "id": "qb-hurts", "name": "Jalen Hurts", "position": "QB", "team": "PHI",
        "adp": 42.0, "tier": 1, "projected_season": 355.0, "projected_week": 22.2,
        "xfp": 21.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 99.8, "espn_proj": 21.6,
        "bye_week": 5, "opponent": "WAS", "implied_team_pts": 28.5, "spread": -8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 30, "archetype": "Tush Push Rushing TD Machine"
    },
    {
        "id": "qb-daniels", "name": "Jayden Daniels", "position": "QB", "team": "WAS",
        "adp": 45.0, "tier": 1, "projected_season": 350.0, "projected_week": 21.9,
        "xfp": 21.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 99.5, "espn_proj": 21.0,
        "bye_week": 14, "opponent": "PHI", "implied_team_pts": 22.5, "spread": 8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 16, "archetype": "Electric Dual-Threat Konami Phenom"
    },
    {
        "id": "qb-mahomes", "name": "Patrick Mahomes", "position": "QB", "team": "KC",
        "adp": 50.0, "tier": 2, "projected_season": 340.0, "projected_week": 21.2,
        "xfp": 20.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.08, "injury_status": "ACTIVE", "espn_ownership": 99.8, "espn_proj": 20.8,
        "bye_week": 6, "opponent": "LAC", "implied_team_pts": 26.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "Generational Pass-Volume Maestro"
    },
    {
        "id": "qb-burrow", "name": "Joe Burrow", "position": "QB", "team": "CIN",
        "adp": 55.0, "tier": 2, "projected_season": 338.0, "projected_week": 21.1,
        "xfp": 20.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.09, "injury_status": "ACTIVE", "espn_ownership": 99.6, "espn_proj": 20.5,
        "bye_week": 12, "opponent": "PIT", "implied_team_pts": 26.5, "spread": -3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "High-Volume Pocket Passer & Deep Ball Sniper"
    },
    {
        "id": "qb-stroud", "name": "C.J. Stroud", "position": "QB", "team": "HOU",
        "adp": 65.0, "tier": 2, "projected_season": 325.0, "projected_week": 20.3,
        "xfp": 19.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 98.9, "espn_proj": 19.8,
        "bye_week": 14, "opponent": "IND", "implied_team_pts": 26.0, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Explosive Downfield Distributor"
    },
    {
        "id": "qb-kyler", "name": "Kyler Murray", "position": "QB", "team": "ARI",
        "adp": 68.0, "tier": 2, "projected_season": 320.0, "projected_week": 20.0,
        "xfp": 19.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 98.0, "espn_proj": 19.4,
        "bye_week": 11, "opponent": "SF", "implied_team_pts": 23.5, "spread": 6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 17, "archetype": "High-Ceiling Scrambler"
    },
    {
        "id": "qb-love", "name": "Jordan Love", "position": "QB", "team": "GB",
        "adp": 75.0, "tier": 3, "projected_season": 315.0, "projected_week": 19.7,
        "xfp": 19.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 19.0,
        "bye_week": 10, "opponent": "DET", "implied_team_pts": 25.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 21, "archetype": "Red Zone TD Machine"
    },
    {
        "id": "qb-baker", "name": "Baker Mayfield", "position": "QB", "team": "TB",
        "adp": 80.0, "tier": 3, "projected_season": 310.0, "projected_week": 19.4,
        "xfp": 18.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.05, "injury_status": "ACTIVE", "espn_ownership": 94.0, "espn_proj": 18.8,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 23, "archetype": "Gunslinger Volume Floor"
    },
    {
        "id": "qb-purdy", "name": "Brock Purdy", "position": "QB", "team": "SF",
        "adp": 85.0, "tier": 3, "projected_season": 305.0, "projected_week": 19.1,
        "xfp": 18.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.02, "injury_status": "ACTIVE", "espn_ownership": 93.0, "espn_proj": 18.5,
        "bye_week": 9, "opponent": "ARI", "implied_team_pts": 26.0, "spread": -6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Hyper-Efficient Play-Action Sniper"
    },
    {
        "id": "qb-caleb", "name": "Caleb Williams", "position": "QB", "team": "CHI",
        "adp": 88.0, "tier": 3, "projected_season": 300.0, "projected_week": 18.8,
        "xfp": 18.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 91.0, "espn_proj": 18.0,
        "bye_week": 7, "opponent": "MIN", "implied_team_pts": 23.5, "spread": 2.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 19, "archetype": "Year 2 Breakout Playmaker"
    },
    {
        "id": "qb-goff", "name": "Jared Goff", "position": "QB", "team": "DET",
        "adp": 92.0, "tier": 3, "projected_season": 295.0, "projected_week": 18.4,
        "xfp": 18.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 89.0, "espn_proj": 17.9,
        "bye_week": 5, "opponent": "GB", "implied_team_pts": 27.5, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 22, "archetype": "Dome Environment Volume Machine"
    },
    {
        "id": "qb-dak", "name": "Dak Prescott", "position": "QB", "team": "DAL",
        "adp": 96.0, "tier": 3, "projected_season": 290.0, "projected_week": 18.1,
        "xfp": 17.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.07, "injury_status": "ACTIVE", "espn_ownership": 88.0, "espn_proj": 17.6,
        "bye_week": 7, "opponent": "NYG", "implied_team_pts": 26.5, "spread": -6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 26, "archetype": "High-Volume Pass Heavy Scheme"
    },
    {
        "id": "qb-arich", "name": "Anthony Richardson", "position": "QB", "team": "IND",
        "adp": 100.0, "tier": 4, "projected_season": 285.0, "projected_week": 17.8,
        "xfp": 18.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.03, "injury_status": "ACTIVE", "espn_ownership": 85.0, "espn_proj": 17.2,
        "bye_week": 14, "opponent": "HOU", "implied_team_pts": 22.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 19, "archetype": "Elite Athletic Rushing Boom/Bust"
    },
    {
        "id": "qb-nix", "name": "Bo Nix", "position": "QB", "team": "DEN",
        "adp": 105.0, "tier": 4, "projected_season": 280.0, "projected_week": 17.5,
        "xfp": 17.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 82.0, "espn_proj": 16.9,
        "bye_week": 14, "opponent": "LVR", "implied_team_pts": 23.5, "spread": -2.5, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 25, "archetype": "Sean Payton Rushing Scrambler"
    },
    {
        "id": "qb-tua", "name": "Tua Tagovailoa", "position": "QB", "team": "ATL",
        "adp": 108.0, "tier": 4, "projected_season": 278.0, "projected_week": 17.4,
        "xfp": 17.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 82.0, "espn_proj": 16.9,
        "bye_week": 12, "opponent": "CAR", "implied_team_pts": 25.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 30, "archetype": "Falcons Starting QB / Fresh Start with London, Pitts & Bijan"
    },
    {
        "id": "qb-willis", "name": "Malik Willis", "position": "QB", "team": "MIA",
        "adp": 115.0, "tier": 4, "projected_season": 272.0, "projected_week": 17.0,
        "xfp": 16.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 72.0, "espn_proj": 16.2,
        "bye_week": 6, "opponent": "BUF", "implied_team_pts": 21.5, "spread": 7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 15, "archetype": "Dolphins Starting Dual-Threat QB / Explosive Rushing Scrambler"
    },
    {
        "id": "qb-penix", "name": "Michael Penix Jr.", "position": "QB", "team": "ATL",
        "adp": 142.0, "tier": 5, "projected_season": 210.0, "projected_week": 13.1,
        "xfp": 13.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "QUESTIONABLE", "espn_ownership": 40.0, "espn_proj": 12.5,
        "bye_week": 12, "opponent": "CAR", "implied_team_pts": 25.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 30, "archetype": "Falcons 1st-Round Big-Arm QB (Recovering from Knee Surgery)"
    },
    {
        "id": "qb-herbert", "name": "Justin Herbert", "position": "QB", "team": "LAC",
        "adp": 112.0, "tier": 4, "projected_season": 272.0, "projected_week": 17.0,
        "xfp": 16.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.06, "injury_status": "ACTIVE", "espn_ownership": 78.0, "espn_proj": 16.5,
        "bye_week": 5, "opponent": "KC", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 16, "archetype": "Elite Arm in Harbaugh Run Scheme"
    },
    {
        "id": "qb-maye", "name": "Drake Maye", "position": "QB", "team": "NE",
        "adp": 115.0, "tier": 4, "projected_season": 268.0, "projected_week": 16.8,
        "xfp": 16.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 70.0, "espn_proj": 16.0,
        "bye_week": 14, "opponent": "NYJ", "implied_team_pts": 20.0, "spread": 5.5, "wind_mph": 11, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "Big-Arm Rushing Upside Rookie"
    },
    {
        "id": "qb-tlaw", "name": "Trevor Lawrence", "position": "QB", "team": "JAX",
        "adp": 118.0, "tier": 4, "projected_season": 265.0, "projected_week": 16.5,
        "xfp": 16.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 68.0, "espn_proj": 15.9,
        "bye_week": 12, "opponent": "TEN", "implied_team_pts": 23.5, "spread": -2.5, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "Gunslinger with BTJ Deep Target"
    },
    {
        "id": "qb-stafford", "name": "Matthew Stafford", "position": "QB", "team": "LAR",
        "adp": 122.0, "tier": 4, "projected_season": 260.0, "projected_week": 16.2,
        "xfp": 16.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 65.0, "espn_proj": 15.6,
        "bye_week": 6, "opponent": "SF", "implied_team_pts": 22.0, "spread": 4.0, "wind_mph": 4, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "Puka & Kupp Volume Distributor"
    },
    {
        "id": "qb-geno", "name": "Geno Smith", "position": "QB", "team": "SEA",
        "adp": 125.0, "tier": 4, "projected_season": 258.0, "projected_week": 16.1,
        "xfp": 15.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 60.0, "espn_proj": 15.4,
        "bye_week": 10, "opponent": "ARI", "implied_team_pts": 24.5, "spread": -3.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Ryan Grubb High-Volume Passer"
    },
    {
        "id": "qb-kirk", "name": "Kirk Cousins", "position": "QB", "team": "ATL",
        "adp": 128.0, "tier": 4, "projected_season": 255.0, "projected_week": 15.9,
        "xfp": 15.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 55.0, "espn_proj": 15.2,
        "bye_week": 12, "opponent": "CAR", "implied_team_pts": 25.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 30, "archetype": "Dome Pocket Passer with London & Bijan"
    },
    {
        "id": "qb-rodgers", "name": "Aaron Rodgers", "position": "QB", "team": "NYJ",
        "adp": 132.0, "tier": 5, "projected_season": 250.0, "projected_week": 15.6,
        "xfp": 15.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 50.0, "espn_proj": 15.0,
        "bye_week": 12, "opponent": "NE", "implied_team_pts": 23.0, "spread": -5.5, "wind_mph": 11, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Veteran Pocket Commander"
    },
    {
        "id": "qb-russell", "name": "Russell Wilson", "position": "QB", "team": "PIT",
        "adp": 136.0, "tier": 5, "projected_season": 245.0, "projected_week": 15.3,
        "xfp": 15.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 45.0, "espn_proj": 14.8,
        "bye_week": 9, "opponent": "CIN", "implied_team_pts": 23.0, "spread": 3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "Deep Ball Moonball Specialist"
    },
    {
        "id": "qb-bryce", "name": "Bryce Young", "position": "QB", "team": "CAR",
        "adp": 140.0, "tier": 5, "projected_season": 240.0, "projected_week": 15.0,
        "xfp": 15.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 38.0, "espn_proj": 14.5,
        "bye_week": 11, "opponent": "ATL", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 25, "archetype": "Dave Canales Resurgence Candidate"
    },
    {
        "id": "qb-levis", "name": "Will Levis", "position": "QB", "team": "TEN",
        "adp": 144.0, "tier": 5, "projected_season": 235.0, "projected_week": 14.7,
        "xfp": 14.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 30.0, "espn_proj": 14.2,
        "bye_week": 5, "opponent": "JAX", "implied_team_pts": 20.5, "spread": 2.5, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 27, "archetype": "Big Cannon Arm Downfield"
    },
    {
        "id": "qb-carr", "name": "Derek Carr", "position": "QB", "team": "NO",
        "adp": 148.0, "tier": 5, "projected_season": 230.0, "projected_week": 14.4,
        "xfp": 14.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.00, "injury_status": "ACTIVE", "espn_ownership": 28.0, "espn_proj": 14.0,
        "bye_week": 12, "opponent": "TB", "implied_team_pts": 21.5, "spread": 4.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 23, "archetype": "Dome Game Manager"
    },
    {
        "id": "qb-watson", "name": "Deshaun Watson", "position": "QB", "team": "CLE",
        "adp": 150.0, "tier": 5, "projected_season": 225.0, "projected_week": 14.0,
        "xfp": 14.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.01, "injury_status": "QUESTIONABLE", "espn_ownership": 25.0, "espn_proj": 13.8,
        "bye_week": 10, "opponent": "BAL", "implied_team_pts": 20.5, "spread": 6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 16, "archetype": "Injury Comeback Quarterback"
    },
    {
        "id": "qb-camward", "name": "Cam Ward", "position": "QB", "team": "NYG",
        "adp": 152.0, "tier": 5, "projected_season": 230.0, "projected_week": 14.4,
        "xfp": 14.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 35.0, "espn_proj": 14.0,
        "bye_week": 11, "opponent": "DAL", "implied_team_pts": 21.0, "spread": 6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "2025 Dynamic Rookie Playmaker"
    },
    {
        "id": "qb-shedeur", "name": "Shedeur Sanders", "position": "QB", "team": "LVR",
        "adp": 155.0, "tier": 5, "projected_season": 228.0, "projected_week": 14.2,
        "xfp": 14.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 32.0, "espn_proj": 13.9,
        "bye_week": 10, "opponent": "DEN", "implied_team_pts": 22.0, "spread": -1.5, "wind_mph": 7, "is_dome": True,
        "opp_rank_vs_pos": 18, "archetype": "2025 Accurate Pocket Rookie"
    },
    {
        "id": "qb-djones", "name": "Daniel Jones", "position": "QB", "team": "FA",
        "adp": 160.0, "tier": 5, "projected_season": 200.0, "projected_week": 12.5,
        "xfp": 12.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": -0.01, "injury_status": "ACTIVE", "espn_ownership": 15.0, "espn_proj": 12.0,
        "bye_week": 11, "opponent": "DAL", "implied_team_pts": 20.0, "spread": 7.0, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 15, "archetype": "Veteran Scrambler Backup"
    },

    # ================= 20 TOP NFL KICKERS =================
    {
        "id": "k-aubrey", "name": "Brandon Aubrey", "position": "K", "team": "DAL",
        "adp": 120.0, "tier": 1, "projected_season": 165.0, "projected_week": 10.3,
        "xfp": 10.1, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 99.8, "espn_proj": 9.8,
        "bye_week": 7, "opponent": "NYG", "implied_team_pts": 26.5, "spread": -6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 25, "archetype": "Elite 50+ & 60+ Yard Weapon"
    },
    {
        "id": "k-boswell", "name": "Chris Boswell", "position": "K", "team": "PIT",
        "adp": 126.0, "tier": 1, "projected_season": 158.0, "projected_week": 9.9,
        "xfp": 9.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 9.4,
        "bye_week": 9, "opponent": "CIN", "implied_team_pts": 23.0, "spread": 3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "High-Volume Field Goal Specialist"
    },
    {
        "id": "k-butker", "name": "Harrison Butker", "position": "K", "team": "KC",
        "adp": 128.0, "tier": 1, "projected_season": 154.0, "projected_week": 9.6,
        "xfp": 9.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 95.0, "espn_proj": 9.2,
        "bye_week": 6, "opponent": "LAC", "implied_team_pts": 26.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "High Scoring Offense Kicker"
    },
    {
        "id": "k-tucker", "name": "Justin Tucker", "position": "K", "team": "BAL",
        "adp": 130.0, "tier": 1, "projected_season": 152.0, "projected_week": 9.5,
        "xfp": 9.3, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 94.0, "espn_proj": 9.1,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Legendary Clutch Specialist"
    },
    {
        "id": "k-fairbairn", "name": "Ka'imi Fairbairn", "position": "K", "team": "HOU",
        "adp": 134.0, "tier": 2, "projected_season": 148.0, "projected_week": 9.2,
        "xfp": 9.1, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 91.0, "espn_proj": 8.9,
        "bye_week": 14, "opponent": "IND", "implied_team_pts": 26.0, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Dome Scoring Weapon"
    },
    {
        "id": "k-dicker", "name": "Cameron Dicker", "position": "K", "team": "LAC",
        "adp": 137.0, "tier": 2, "projected_season": 145.0, "projected_week": 9.1,
        "xfp": 9.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 88.0, "espn_proj": 8.8,
        "bye_week": 5, "opponent": "KC", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 19, "archetype": "High Accuracy Specialist"
    },
    {
        "id": "k-moody", "name": "Jake Moody", "position": "K", "team": "SF",
        "adp": 139.0, "tier": 2, "projected_season": 144.0, "projected_week": 9.0,
        "xfp": 8.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 86.0, "espn_proj": 8.7,
        "bye_week": 9, "opponent": "ARI", "implied_team_pts": 26.0, "spread": -6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 23, "archetype": "49ers High-Powered Offense"
    },
    {
        "id": "k-elliott", "name": "Jake Elliott", "position": "K", "team": "PHI",
        "adp": 141.0, "tier": 2, "projected_season": 142.0, "projected_week": 8.9,
        "xfp": 8.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 85.0, "espn_proj": 8.6,
        "bye_week": 5, "opponent": "WAS", "implied_team_pts": 28.5, "spread": -8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 26, "archetype": "High XP & FG Floor"
    },
    {
        "id": "k-bass", "name": "Tyler Bass", "position": "K", "team": "BUF",
        "adp": 143.0, "tier": 2, "projected_season": 140.0, "projected_week": 8.8,
        "xfp": 8.7, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 82.0, "espn_proj": 8.5,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Bills Scoring Floor"
    },
    {
        "id": "k-koo", "name": "Younghoe Koo", "position": "K", "team": "ATL",
        "adp": 145.0, "tier": 2, "projected_season": 138.0, "projected_week": 8.6,
        "xfp": 8.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 80.0, "espn_proj": 8.4,
        "bye_week": 12, "opponent": "CAR", "implied_team_pts": 25.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 28, "archetype": "Dome Environment Field Goal Volume"
    },
    {
        "id": "k-sanders", "name": "Jason Sanders", "position": "K", "team": "MIA",
        "adp": 147.0, "tier": 3, "projected_season": 135.0, "projected_week": 8.4,
        "xfp": 8.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 75.0, "espn_proj": 8.2,
        "bye_week": 6, "opponent": "BUF", "implied_team_pts": 21.5, "spread": 7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "Long Range Scoring Weapon"
    },
    {
        "id": "k-mcpherson", "name": "Evan McPherson", "position": "K", "team": "CIN",
        "adp": 149.0, "tier": 3, "projected_season": 134.0, "projected_week": 8.4,
        "xfp": 8.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 73.0, "espn_proj": 8.1,
        "bye_week": 12, "opponent": "PIT", "implied_team_pts": 26.5, "spread": -3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "High-Scoring Bengals Offense"
    },
    {
        "id": "k-mclaughlin", "name": "Chase McLaughlin", "position": "K", "team": "TB",
        "adp": 151.0, "tier": 3, "projected_season": 132.0, "projected_week": 8.2,
        "xfp": 8.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 68.0, "espn_proj": 8.0,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "50+ Yard Accuracy Leader"
    },
    {
        "id": "k-lutz", "name": "Wil Lutz", "position": "K", "team": "DEN",
        "adp": 153.0, "tier": 3, "projected_season": 130.0, "projected_week": 8.1,
        "xfp": 8.1, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 65.0, "espn_proj": 7.9,
        "bye_week": 14, "opponent": "LVR", "implied_team_pts": 23.5, "spread": -2.5, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Mile High Altitude Field Goals"
    },
    {
        "id": "k-hopkins", "name": "Dustin Hopkins", "position": "K", "team": "CLE",
        "adp": 155.0, "tier": 3, "projected_season": 128.0, "projected_week": 8.0,
        "xfp": 8.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 60.0, "espn_proj": 7.8,
        "bye_week": 10, "opponent": "BAL", "implied_team_pts": 20.5, "spread": 6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 19, "archetype": "Long Range FG Specialist"
    },
    {
        "id": "k-santos", "name": "Cairo Santos", "position": "K", "team": "CHI",
        "adp": 157.0, "tier": 3, "projected_season": 126.0, "projected_week": 7.9,
        "xfp": 7.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 55.0, "espn_proj": 7.7,
        "bye_week": 7, "opponent": "MIN", "implied_team_pts": 23.5, "spread": 2.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Steady Soldier Field Veteran"
    },
    {
        "id": "k-grupe", "name": "Blake Grupe", "position": "K", "team": "NO",
        "adp": 159.0, "tier": 4, "projected_season": 124.0, "projected_week": 7.8,
        "xfp": 7.7, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 48.0, "espn_proj": 7.6,
        "bye_week": 12, "opponent": "TB", "implied_team_pts": 21.5, "spread": 4.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "Superdome Kicker"
    },
    {
        "id": "k-pineiro", "name": "Eddy Pineiro", "position": "K", "team": "CAR",
        "adp": 161.0, "tier": 4, "projected_season": 122.0, "projected_week": 7.6,
        "xfp": 7.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 40.0, "espn_proj": 7.4,
        "bye_week": 11, "opponent": "ATL", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 22, "archetype": "High Accuracy Percentage"
    },
    {
        "id": "k-prater", "name": "Matt Prater", "position": "K", "team": "ARI",
        "adp": 163.0, "tier": 4, "projected_season": 120.0, "projected_week": 7.5,
        "xfp": 7.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 35.0, "espn_proj": 7.3,
        "bye_week": 11, "opponent": "SF", "implied_team_pts": 23.5, "spread": 6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 18, "archetype": "Veteran Cannon Leg"
    },
    {
        "id": "k-joseph", "name": "Greg Joseph", "position": "K", "team": "NYG",
        "adp": 165.0, "tier": 4, "projected_season": 118.0, "projected_week": 7.4,
        "xfp": 7.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 30.0, "espn_proj": 7.1,
        "bye_week": 11, "opponent": "DAL", "implied_team_pts": 21.0, "spread": 6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 19, "archetype": "FG Volume Option"
    },

    # ================= 20 TOP NFL TEAM DEFENSES =================
    {
        "id": "def-vikings", "name": "Minnesota Vikings D/ST", "position": "DEF", "team": "MIN",
        "adp": 124.0, "tier": 1, "projected_season": 145.0, "projected_week": 9.1,
        "xfp": 9.3, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 98.0, "espn_proj": 8.8,
        "bye_week": 6, "opponent": "CHI", "implied_team_pts": 24.5, "spread": -2.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 31, "archetype": "Brian Flores Blitz / Turnover & Sack Dominator"
    },
    {
        "id": "def-eagles", "name": "Philadelphia Eagles D/ST", "position": "DEF", "team": "PHI",
        "adp": 127.0, "tier": 1, "projected_season": 140.0, "projected_week": 8.8,
        "xfp": 8.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 8.6,
        "bye_week": 5, "opponent": "WAS", "implied_team_pts": 28.5, "spread": -8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 28, "archetype": "Fangio Pass Rush & Secondary Studs"
    },
    {
        "id": "def-broncos", "name": "Denver Broncos D/ST", "position": "DEF", "team": "DEN",
        "adp": 129.0, "tier": 1, "projected_season": 138.0, "projected_week": 8.6,
        "xfp": 8.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 95.0, "espn_proj": 8.4,
        "bye_week": 14, "opponent": "LVR", "implied_team_pts": 23.5, "spread": -2.5, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 29, "archetype": "Vance Joseph High Pressure Sacks & Surtain Lock"
    },
    {
        "id": "def-steelers", "name": "Pittsburgh Steelers D/ST", "position": "DEF", "team": "PIT",
        "adp": 131.0, "tier": 1, "projected_season": 136.0, "projected_week": 8.5,
        "xfp": 8.7, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 94.0, "espn_proj": 8.3,
        "bye_week": 9, "opponent": "CIN", "implied_team_pts": 23.0, "spread": 3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 26, "archetype": "TJ Watt Strip-Sack & Turnover Heavy"
    },
    {
        "id": "def-ravens", "name": "Baltimore Ravens D/ST", "position": "DEF", "team": "BAL",
        "adp": 133.0, "tier": 1, "projected_season": 134.0, "projected_week": 8.4,
        "xfp": 8.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 92.0, "espn_proj": 8.2,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 27, "archetype": "Physical Run Stuff & Roquan Smith Anchor"
    },
    {
        "id": "def-49ers", "name": "San Francisco 49ers D/ST", "position": "DEF", "team": "SF",
        "adp": 135.0, "tier": 2, "projected_season": 132.0, "projected_week": 8.3,
        "xfp": 8.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 90.0, "espn_proj": 8.0,
        "bye_week": 9, "opponent": "ARI", "implied_team_pts": 26.0, "spread": -6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Nick Bosa Pass Rush & Warner Coverage"
    },
    {
        "id": "def-texans", "name": "Houston Texans D/ST", "position": "DEF", "team": "HOU",
        "adp": 138.0, "tier": 2, "projected_season": 130.0, "projected_week": 8.1,
        "xfp": 8.3, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 88.0, "espn_proj": 7.9,
        "bye_week": 14, "opponent": "IND", "implied_team_pts": 26.0, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 25, "archetype": "DeMeco Ryans High-Pressure Defense"
    },
    {
        "id": "def-jets", "name": "New York Jets D/ST", "position": "DEF", "team": "NYJ",
        "adp": 140.0, "tier": 2, "projected_season": 128.0, "projected_week": 8.0,
        "xfp": 8.1, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 85.0, "espn_proj": 7.8,
        "bye_week": 12, "opponent": "NE", "implied_team_pts": 23.0, "spread": -5.5, "wind_mph": 11, "is_dome": False,
        "opp_rank_vs_pos": 26, "archetype": "Sauce Gardner Lockdown Secondary"
    },
    {
        "id": "def-lions", "name": "Detroit Lions D/ST", "position": "DEF", "team": "DET",
        "adp": 142.0, "tier": 2, "projected_season": 126.0, "projected_week": 7.9,
        "xfp": 8.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 84.0, "espn_proj": 7.7,
        "bye_week": 5, "opponent": "GB", "implied_team_pts": 27.5, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 22, "archetype": "Aidan Hutchinson Edge Rush & Aggressive Front"
    },
    {
        "id": "def-chiefs", "name": "Kansas City Chiefs D/ST", "position": "DEF", "team": "KC",
        "adp": 144.0, "tier": 2, "projected_season": 125.0, "projected_week": 7.8,
        "xfp": 7.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 82.0, "espn_proj": 7.6,
        "bye_week": 6, "opponent": "LAC", "implied_team_pts": 26.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 23, "archetype": "Spagnuolo Blitz Package"
    },
    {
        "id": "def-bills", "name": "Buffalo Bills D/ST", "position": "DEF", "team": "BUF",
        "adp": 146.0, "tier": 3, "projected_season": 122.0, "projected_week": 7.6,
        "xfp": 7.8, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 80.0, "espn_proj": 7.5,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "McDermott Discipline & Turnover Ball"
    },
    {
        "id": "def-packers", "name": "Green Bay Packers D/ST", "position": "DEF", "team": "GB",
        "adp": 148.0, "tier": 3, "projected_season": 120.0, "projected_week": 7.5,
        "xfp": 7.6, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 78.0, "espn_proj": 7.3,
        "bye_week": 10, "opponent": "DET", "implied_team_pts": 25.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "Xavier McKinney Turnover Ball Hawk"
    },
    {
        "id": "def-chargers", "name": "Los Angeles Chargers D/ST", "position": "DEF", "team": "LAC",
        "adp": 150.0, "tier": 3, "projected_season": 118.0, "projected_week": 7.4,
        "xfp": 7.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 75.0, "espn_proj": 7.2,
        "bye_week": 5, "opponent": "KC", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 19, "archetype": "Jesse Minter Defensive Mastermind"
    },
    {
        "id": "def-bears", "name": "Chicago Bears D/ST", "position": "DEF", "team": "CHI",
        "adp": 152.0, "tier": 3, "projected_season": 116.0, "projected_week": 7.3,
        "xfp": 7.4, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 70.0, "espn_proj": 7.0,
        "bye_week": 7, "opponent": "MIN", "implied_team_pts": 23.5, "spread": 2.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "Montez Sweat Edge & High Interception Rate"
    },
    {
        "id": "def-cowboys", "name": "Dallas Cowboys D/ST", "position": "DEF", "team": "DAL",
        "adp": 154.0, "tier": 3, "projected_season": 115.0, "projected_week": 7.2,
        "xfp": 7.3, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 68.0, "espn_proj": 6.9,
        "bye_week": 7, "opponent": "NYG", "implied_team_pts": 26.5, "spread": -6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Micah Parsons Sack Artist"
    },
    {
        "id": "def-browns", "name": "Cleveland Browns D/ST", "position": "DEF", "team": "CLE",
        "adp": 156.0, "tier": 4, "projected_season": 112.0, "projected_week": 7.0,
        "xfp": 7.2, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 62.0, "espn_proj": 6.8,
        "bye_week": 10, "opponent": "BAL", "implied_team_pts": 20.5, "spread": 6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "Myles Garrett DPOY Pass Rush"
    },
    {
        "id": "def-seahawks", "name": "Seattle Seahawks D/ST", "position": "DEF", "team": "SEA",
        "adp": 158.0, "tier": 4, "projected_season": 110.0, "projected_week": 6.9,
        "xfp": 7.0, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 55.0, "espn_proj": 6.7,
        "bye_week": 10, "opponent": "ARI", "implied_team_pts": 24.5, "spread": -3.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Mike Macdonald Scheme"
    },
    {
        "id": "def-bucs", "name": "Tampa Bay Buccaneers D/ST", "position": "DEF", "team": "TB",
        "adp": 160.0, "tier": 4, "projected_season": 108.0, "projected_week": 6.8,
        "xfp": 6.9, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 50.0, "espn_proj": 6.5,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "Todd Bowles Blitz System"
    },
    {
        "id": "def-dolphins", "name": "Miami Dolphins D/ST", "position": "DEF", "team": "MIA",
        "adp": 162.0, "tier": 4, "projected_season": 105.0, "projected_week": 6.6,
        "xfp": 6.7, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 45.0, "espn_proj": 6.4,
        "bye_week": 6, "opponent": "BUF", "implied_team_pts": 21.5, "spread": 7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 17, "archetype": "Anthony Weaver Front"
    },
    {
        "id": "def-colts", "name": "Indianapolis Colts D/ST", "position": "DEF", "team": "IND",
        "adp": 164.0, "tier": 4, "projected_season": 102.0, "projected_week": 6.4,
        "xfp": 6.5, "route_participation": 0.0, "high_value_touches": 0.0, "red_zone_share": 0.0,
        "target_share": 0.0, "proe": 0.0, "injury_status": "ACTIVE", "espn_ownership": 40.0, "espn_proj": 6.2,
        "bye_week": 14, "opponent": "HOU", "implied_team_pts": 22.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 18, "archetype": "Turnover Opportunistic Unit"
    }
]
