import json

SKILL_PLAYERS = [
    # ================= WIDE RECEIVERS =================
    {
        "id": "wr-jsn", "name": "Jaxon Smith-Njigba", "position": "WR", "team": "SEA",
        "adp": 44.0, "tier": 3, "projected_season": 255.0, "projected_week": 15.9,
        "xfp": 16.2, "route_participation": 0.94, "high_value_touches": 4.8, "red_zone_share": 0.32,
        "target_share": 0.26, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 98.0, "espn_proj": 15.4,
        "bye_week": 10, "opponent": "ARI", "implied_team_pts": 24.5, "spread": -3.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Ryan Grubb Alpha Slot/Wide Target Monster"
    },
    {
        "id": "wr-dk", "name": "DK Metcalf", "position": "WR", "team": "SEA",
        "adp": 38.0, "tier": 2, "projected_season": 265.0, "projected_week": 16.5,
        "xfp": 16.8, "route_participation": 0.93, "high_value_touches": 5.0, "red_zone_share": 0.36,
        "target_share": 0.25, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 99.0, "espn_proj": 16.0,
        "bye_week": 10, "opponent": "ARI", "implied_team_pts": 24.5, "spread": -3.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Physical Specimen / Red Zone Alpha"
    },
    {
        "id": "wr-flowers", "name": "Zay Flowers", "position": "WR", "team": "BAL",
        "adp": 40.0, "tier": 2, "projected_season": 260.0, "projected_week": 16.2,
        "xfp": 16.0, "route_participation": 0.92, "high_value_touches": 4.6, "red_zone_share": 0.28,
        "target_share": 0.27, "proe": -0.05, "injury_status": "ACTIVE", "espn_ownership": 98.5, "espn_proj": 15.8,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 28, "archetype": "Lamar Jackson Alpha YAC Magnet"
    },
    {
        "id": "wr-waddle", "name": "Jaylen Waddle", "position": "WR", "team": "MIA",
        "adp": 42.0, "tier": 3, "projected_season": 252.0, "projected_week": 15.7,
        "xfp": 15.8, "route_participation": 0.89, "high_value_touches": 4.4, "red_zone_share": 0.27,
        "target_share": 0.24, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 97.0, "espn_proj": 15.2,
        "bye_week": 6, "opponent": "BUF", "implied_team_pts": 21.5, "spread": 7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "Elite Explosive Speed Weapon"
    },
    {
        "id": "wr-devonta", "name": "DeVonta Smith", "position": "WR", "team": "PHI",
        "adp": 45.0, "tier": 3, "projected_season": 250.0, "projected_week": 15.6,
        "xfp": 15.6, "route_participation": 0.94, "high_value_touches": 4.5, "red_zone_share": 0.26,
        "target_share": 0.24, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 97.5, "espn_proj": 15.1,
        "bye_week": 5, "opponent": "WAS", "implied_team_pts": 28.5, "spread": -8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 26, "archetype": "Silky Smooth Route Technician"
    },
    {
        "id": "wr-higgins", "name": "Tee Higgins", "position": "WR", "team": "CIN",
        "adp": 46.0, "tier": 3, "projected_season": 248.0, "projected_week": 15.5,
        "xfp": 15.5, "route_participation": 0.91, "high_value_touches": 4.6, "red_zone_share": 0.30,
        "target_share": 0.24, "proe": 0.08, "injury_status": "ACTIVE", "espn_ownership": 97.0, "espn_proj": 15.0,
        "bye_week": 12, "opponent": "PIT", "implied_team_pts": 26.5, "spread": -3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "Burrow Red Zone / Boundary High-Point Stud"
    },
    {
        "id": "wr-pickens", "name": "George Pickens", "position": "WR", "team": "PIT",
        "adp": 48.0, "tier": 3, "projected_season": 242.0, "projected_week": 15.1,
        "xfp": 15.2, "route_participation": 0.95, "high_value_touches": 4.4, "red_zone_share": 0.33,
        "target_share": 0.28, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 14.8,
        "bye_week": 9, "opponent": "CIN", "implied_team_pts": 23.0, "spread": 3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "Contested Catch & Air Yards Dominator"
    },
    {
        "id": "wr-godwin", "name": "Chris Godwin", "position": "WR", "team": "TB",
        "adp": 50.0, "tier": 3, "projected_season": 240.0, "projected_week": 15.0,
        "xfp": 15.4, "route_participation": 0.90, "high_value_touches": 4.5, "red_zone_share": 0.28,
        "target_share": 0.26, "proe": 0.05, "injury_status": "ACTIVE", "espn_ownership": 95.0, "espn_proj": 14.7,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 23, "archetype": "Slot Target Funnel PPR Machine"
    },
    {
        "id": "wr-evans", "name": "Mike Evans", "position": "WR", "team": "TB",
        "adp": 52.0, "tier": 3, "projected_season": 238.0, "projected_week": 14.9,
        "xfp": 15.0, "route_participation": 0.88, "high_value_touches": 4.4, "red_zone_share": 0.35,
        "target_share": 0.24, "proe": 0.05, "injury_status": "ACTIVE", "espn_ownership": 95.5, "espn_proj": 14.5,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 23, "archetype": "1,000-Yard & 10-TD Machine"
    },
    {
        "id": "wr-kupp", "name": "Cooper Kupp", "position": "WR", "team": "LAR",
        "adp": 54.0, "tier": 3, "projected_season": 236.0, "projected_week": 14.7,
        "xfp": 15.2, "route_participation": 0.88, "high_value_touches": 4.3, "red_zone_share": 0.30,
        "target_share": 0.27, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 94.0, "espn_proj": 14.4,
        "bye_week": 6, "opponent": "SF", "implied_team_pts": 22.0, "spread": 4.0, "wind_mph": 4, "is_dome": False,
        "opp_rank_vs_pos": 18, "archetype": "Triple Crown PPR Slot Legend"
    },
    {
        "id": "wr-adams", "name": "Davante Adams", "position": "WR", "team": "NYJ",
        "adp": 56.0, "tier": 3, "projected_season": 235.0, "projected_week": 14.7,
        "xfp": 15.0, "route_participation": 0.92, "high_value_touches": 4.5, "red_zone_share": 0.34,
        "target_share": 0.26, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 14.3,
        "bye_week": 12, "opponent": "NE", "implied_team_pts": 23.0, "spread": -5.5, "wind_mph": 11, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Elite Separation Master"
    },
    {
        "id": "wr-mcconkey", "name": "Ladd McConkey", "position": "WR", "team": "LAC",
        "adp": 58.0, "tier": 3, "projected_season": 232.0, "projected_week": 14.5,
        "xfp": 14.8, "route_participation": 0.88, "high_value_touches": 4.2, "red_zone_share": 0.28,
        "target_share": 0.26, "proe": -0.06, "injury_status": "ACTIVE", "espn_ownership": 93.0, "espn_proj": 14.1,
        "bye_week": 5, "opponent": "KC", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 18, "archetype": "Harbaugh Target Vacuum & Elite Separator"
    },
    {
        "id": "wr-worthy", "name": "Xavier Worthy", "position": "WR", "team": "KC",
        "adp": 64.0, "tier": 3, "projected_season": 225.0, "projected_week": 14.0,
        "xfp": 14.2, "route_participation": 0.86, "high_value_touches": 4.0, "red_zone_share": 0.26,
        "target_share": 0.22, "proe": 0.08, "injury_status": "ACTIVE", "espn_ownership": 91.0, "espn_proj": 13.6,
        "bye_week": 6, "opponent": "LAC", "implied_team_pts": 26.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "4.21 Speed Gamebreaker with Mahomes"
    },
    {
        "id": "wr-shakir", "name": "Khalil Shakir", "position": "WR", "team": "BUF",
        "adp": 70.0, "tier": 4, "projected_season": 218.0, "projected_week": 13.6,
        "xfp": 13.8, "route_participation": 0.84, "high_value_touches": 3.8, "red_zone_share": 0.25,
        "target_share": 0.23, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 88.0, "espn_proj": 13.2,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Josh Allen #1 YAC Target"
    },
    {
        "id": "wr-jamo", "name": "Jameson Williams", "position": "WR", "team": "DET",
        "adp": 74.0, "tier": 4, "projected_season": 215.0, "projected_week": 13.4,
        "xfp": 13.5, "route_participation": 0.82, "high_value_touches": 3.6, "red_zone_share": 0.24,
        "target_share": 0.21, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 86.0, "espn_proj": 13.0,
        "bye_week": 5, "opponent": "GB", "implied_team_pts": 27.5, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 22, "archetype": "Deep Ball Field Tilter"
    },

    # ================= RUNNING BACKS =================
    {
        "id": "rb-achane", "name": "De'Von Achane", "position": "RB", "team": "MIA",
        "adp": 16.0, "tier": 2, "projected_season": 280.0, "projected_week": 17.5,
        "xfp": 17.4, "route_participation": 0.68, "high_value_touches": 6.2, "red_zone_share": 0.40,
        "target_share": 0.18, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 99.8, "espn_proj": 17.2,
        "bye_week": 6, "opponent": "BUF", "implied_team_pts": 21.5, "spread": 7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 25, "archetype": "Hyper-Explosive Dual-Threat PPR Weapon"
    },
    {
        "id": "rb-kyren", "name": "Kyren Williams", "position": "RB", "team": "LAR",
        "adp": 18.0, "tier": 2, "projected_season": 276.0, "projected_week": 17.2,
        "xfp": 17.0, "route_participation": 0.62, "high_value_touches": 5.8, "red_zone_share": 0.55,
        "target_share": 0.12, "proe": 0.02, "injury_status": "ACTIVE", "espn_ownership": 99.5, "espn_proj": 17.0,
        "bye_week": 6, "opponent": "SF", "implied_team_pts": 22.0, "spread": 4.0, "wind_mph": 4, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "McVay Pure Goal-Line Bellcow"
    },
    {
        "id": "rb-jacobs", "name": "Josh Jacobs", "position": "RB", "team": "GB",
        "adp": 20.0, "tier": 2, "projected_season": 270.0, "projected_week": 16.9,
        "xfp": 16.6, "route_participation": 0.58, "high_value_touches": 5.2, "red_zone_share": 0.48,
        "target_share": 0.10, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 99.2, "espn_proj": 16.7,
        "bye_week": 10, "opponent": "DET", "implied_team_pts": 25.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "Heavy Workhorse Volume Anchor"
    },
    {
        "id": "rb-kwalker", "name": "Kenneth Walker III", "position": "RB", "team": "SEA",
        "adp": 26.0, "tier": 2, "projected_season": 262.0, "projected_week": 16.4,
        "xfp": 16.2, "route_participation": 0.56, "high_value_touches": 5.0, "red_zone_share": 0.45,
        "target_share": 0.12, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 98.8, "espn_proj": 16.1,
        "bye_week": 10, "opponent": "ARI", "implied_team_pts": 24.5, "spread": -3.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 27, "archetype": "Home-Run Explosive Workhorse"
    },
    {
        "id": "rb-cook", "name": "James Cook", "position": "RB", "team": "BUF",
        "adp": 28.0, "tier": 2, "projected_season": 258.0, "projected_week": 16.1,
        "xfp": 15.9, "route_participation": 0.60, "high_value_touches": 4.8, "red_zone_share": 0.38,
        "target_share": 0.14, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 98.5, "espn_proj": 15.8,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 23, "archetype": "High-Efficiency Rushing & Pass Weapon"
    },
    {
        "id": "rb-mixon", "name": "Joe Mixon", "position": "RB", "team": "HOU",
        "adp": 30.0, "tier": 2, "projected_season": 255.0, "projected_week": 15.9,
        "xfp": 15.8, "route_participation": 0.55, "high_value_touches": 5.1, "red_zone_share": 0.50,
        "target_share": 0.11, "proe": 0.06, "injury_status": "ACTIVE", "espn_ownership": 98.2, "espn_proj": 15.6,
        "bye_week": 14, "opponent": "IND", "implied_team_pts": 26.0, "spread": -3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 24, "archetype": "Texans Touchdown Anchor"
    },
    {
        "id": "rb-kamara", "name": "Alvin Kamara", "position": "RB", "team": "NO",
        "adp": 33.0, "tier": 2, "projected_season": 252.0, "projected_week": 15.7,
        "xfp": 16.0, "route_participation": 0.70, "high_value_touches": 5.5, "red_zone_share": 0.42,
        "target_share": 0.20, "proe": 0.00, "injury_status": "ACTIVE", "espn_ownership": 98.0, "espn_proj": 15.5,
        "bye_week": 12, "opponent": "TB", "implied_team_pts": 21.5, "spread": 4.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 20, "archetype": "Full-PPR Target Legend"
    },
    {
        "id": "rb-conner", "name": "James Conner", "position": "RB", "team": "ARI",
        "adp": 36.0, "tier": 3, "projected_season": 245.0, "projected_week": 15.3,
        "xfp": 15.2, "route_participation": 0.54, "high_value_touches": 4.8, "red_zone_share": 0.52,
        "target_share": 0.10, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 97.0, "espn_proj": 15.0,
        "bye_week": 11, "opponent": "SF", "implied_team_pts": 23.5, "spread": 6.0, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 18, "archetype": "Tough YAC Rusher & Goal-Line Monster"
    },
    {
        "id": "rb-chuba", "name": "Chuba Hubbard", "position": "RB", "team": "CAR",
        "adp": 42.0, "tier": 3, "projected_season": 238.0, "projected_week": 14.9,
        "xfp": 14.8, "route_participation": 0.58, "high_value_touches": 4.6, "red_zone_share": 0.46,
        "target_share": 0.11, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 94.0, "espn_proj": 14.4,
        "bye_week": 11, "opponent": "ATL", "implied_team_pts": 21.0, "spread": 4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 25, "archetype": "Panthers Workhorse Extension"
    },
    {
        "id": "rb-bucky", "name": "Bucky Irving", "position": "RB", "team": "TB",
        "adp": 44.0, "tier": 3, "projected_season": 235.0, "projected_week": 14.7,
        "xfp": 14.6, "route_participation": 0.58, "high_value_touches": 4.5, "red_zone_share": 0.40,
        "target_share": 0.13, "proe": 0.05, "injury_status": "ACTIVE", "espn_ownership": 93.0, "espn_proj": 14.2,
        "bye_week": 11, "opponent": "NO", "implied_team_pts": 25.5, "spread": -4.0, "wind_mph": 5, "is_dome": False,
        "opp_rank_vs_pos": 23, "archetype": "Elusive Year 2 RB1 Breakout"
    },
    {
        "id": "rb-tracy", "name": "Tyrone Tracy Jr.", "position": "RB", "team": "NYG",
        "adp": 52.0, "tier": 3, "projected_season": 226.0, "projected_week": 14.1,
        "xfp": 14.0, "route_participation": 0.62, "high_value_touches": 4.2, "red_zone_share": 0.42,
        "target_share": 0.14, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 90.0, "espn_proj": 13.8,
        "bye_week": 11, "opponent": "DAL", "implied_team_pts": 21.0, "spread": 6.5, "wind_mph": 5, "is_dome": True,
        "opp_rank_vs_pos": 26, "archetype": "Converted WR / High-Volume Pass Catcher"
    },
    {
        "id": "rb-swift", "name": "D'Andre Swift", "position": "RB", "team": "CHI",
        "adp": 55.0, "tier": 3, "projected_season": 222.0, "projected_week": 13.9,
        "xfp": 13.8, "route_participation": 0.56, "high_value_touches": 4.1, "red_zone_share": 0.38,
        "target_share": 0.12, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 89.0, "espn_proj": 13.5,
        "bye_week": 7, "opponent": "MIN", "implied_team_pts": 23.5, "spread": 2.5, "wind_mph": 8, "is_dome": False,
        "opp_rank_vs_pos": 19, "archetype": "Bears Lead Dual-Threat Back"
    },

    # ================= TIGHT ENDS =================
    {
        "id": "te-kincaid", "name": "Dalton Kincaid", "position": "TE", "team": "BUF",
        "adp": 66.0, "tier": 2, "projected_season": 210.0, "projected_week": 13.1,
        "xfp": 13.0, "route_participation": 0.82, "high_value_touches": 4.1, "red_zone_share": 0.27,
        "target_share": 0.21, "proe": 0.03, "injury_status": "ACTIVE", "espn_ownership": 96.0, "espn_proj": 12.8,
        "bye_week": 12, "opponent": "MIA", "implied_team_pts": 28.0, "spread": -7.0, "wind_mph": 12, "is_dome": False,
        "opp_rank_vs_pos": 21, "archetype": "Josh Allen Slot/Seam Weapon"
    },
    {
        "id": "te-mandrews", "name": "Mark Andrews", "position": "TE", "team": "BAL",
        "adp": 68.0, "tier": 2, "projected_season": 208.0, "projected_week": 13.0,
        "xfp": 12.8, "route_participation": 0.72, "high_value_touches": 4.0, "red_zone_share": 0.32,
        "target_share": 0.19, "proe": -0.05, "injury_status": "ACTIVE", "espn_ownership": 95.0, "espn_proj": 12.6,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "Lamar Jackson Goal-Line Red Zone Monster"
    },
    {
        "id": "te-pitts", "name": "Kyle Pitts", "position": "TE", "team": "ATL",
        "adp": 74.0, "tier": 3, "projected_season": 195.0, "projected_week": 12.2,
        "xfp": 12.0, "route_participation": 0.78, "high_value_touches": 3.8, "red_zone_share": 0.25,
        "target_share": 0.18, "proe": 0.01, "injury_status": "ACTIVE", "espn_ownership": 92.0, "espn_proj": 11.8,
        "bye_week": 12, "opponent": "CAR", "implied_team_pts": 25.5, "spread": -4.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 28, "archetype": "Unicorn Athletic Seam Threat"
    },
    {
        "id": "te-goedert", "name": "Dallas Goedert", "position": "TE", "team": "PHI",
        "adp": 80.0, "tier": 3, "projected_season": 188.0, "projected_week": 11.8,
        "xfp": 11.6, "route_participation": 0.76, "high_value_touches": 3.7, "red_zone_share": 0.24,
        "target_share": 0.17, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 88.0, "espn_proj": 11.4,
        "bye_week": 5, "opponent": "WAS", "implied_team_pts": 28.5, "spread": -8.0, "wind_mph": 7, "is_dome": False,
        "opp_rank_vs_pos": 24, "archetype": "Eagles Middle of the Field Anchor"
    },
    {
        "id": "te-kraft", "name": "Tucker Kraft", "position": "TE", "team": "GB",
        "adp": 84.0, "tier": 3, "projected_season": 184.0, "projected_week": 11.5,
        "xfp": 11.3, "route_participation": 0.78, "high_value_touches": 3.6, "red_zone_share": 0.26,
        "target_share": 0.17, "proe": 0.04, "injury_status": "ACTIVE", "espn_ownership": 86.0, "espn_proj": 11.0,
        "bye_week": 10, "opponent": "DET", "implied_team_pts": 25.0, "spread": 3.5, "wind_mph": 0, "is_dome": True,
        "opp_rank_vs_pos": 21, "archetype": "Jordan Love YAC Monster Breakout"
    },
    {
        "id": "te-likely", "name": "Isaiah Likely", "position": "TE", "team": "BAL",
        "adp": 90.0, "tier": 3, "projected_season": 180.0, "projected_week": 11.2,
        "xfp": 11.0, "route_participation": 0.65, "high_value_touches": 3.5, "red_zone_share": 0.25,
        "target_share": 0.16, "proe": -0.05, "injury_status": "ACTIVE", "espn_ownership": 82.0, "espn_proj": 10.8,
        "bye_week": 14, "opponent": "CLE", "implied_team_pts": 27.5, "spread": -6.5, "wind_mph": 9, "is_dome": False,
        "opp_rank_vs_pos": 20, "archetype": "Explosive Athletic Playmaker"
    },
    {
        "id": "te-freiermuth", "name": "Pat Freiermuth", "position": "TE", "team": "PIT",
        "adp": 96.0, "tier": 4, "projected_season": 172.0, "projected_week": 10.8,
        "xfp": 10.5, "route_participation": 0.74, "high_value_touches": 3.2, "red_zone_share": 0.24,
        "target_share": 0.16, "proe": -0.04, "injury_status": "ACTIVE", "espn_ownership": 75.0, "espn_proj": 10.2,
        "bye_week": 9, "opponent": "CIN", "implied_team_pts": 23.0, "spread": 3.5, "wind_mph": 6, "is_dome": False,
        "opp_rank_vs_pos": 22, "archetype": "Red Zone Possession Target"
    }
]

if __name__ == "__main__":
    from backend.app.services.generate_players import EXPANDED_PLAYERS
    print(f"Skill players to add: {len(SKILL_PLAYERS)}")
