import re
import ast

with open("backend/app/services/nfl_stats_service.py", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'INITIAL_PLAYERS:\s*List\[Dict\[str,\s*Any\]\]\s*=\s*(\[[\s\S]*?\])\s*class\s+NFLStatsService', content)
if not match:
    print("Match failed")
    exit(1)

players = ast.literal_eval(match.group(1))

# Systematically assign Tier based on position & projected season points
for p in players:
    pos = p["position"]
    proj = p.get("projected_season", 0.0)
    
    if pos in ["WR", "RB"]:
        if proj >= 290.0:
            p["tier"] = 1
        elif proj >= 250.0:
            p["tier"] = 2
        elif proj >= 210.0:
            p["tier"] = 3
        elif proj >= 170.0:
            p["tier"] = 4
        else:
            p["tier"] = 5
    elif pos == "QB":
        if proj >= 350.0:
            p["tier"] = 1
        elif proj >= 320.0:
            p["tier"] = 2
        elif proj >= 290.0:
            p["tier"] = 3
        elif proj >= 255.0:
            p["tier"] = 4
        else:
            p["tier"] = 5
    elif pos == "TE":
        if proj >= 220.0:
            p["tier"] = 1
        elif proj >= 200.0:
            p["tier"] = 2
        elif proj >= 175.0:
            p["tier"] = 3
        elif proj >= 150.0:
            p["tier"] = 4
        else:
            p["tier"] = 5
    elif pos in ["K", "DEF"]:
        if proj >= 135.0:
            p["tier"] = 1
        elif proj >= 125.0:
            p["tier"] = 2
        elif proj >= 115.0:
            p["tier"] = 3
        else:
            p["tier"] = 4

# Format Python code for INITIAL_PLAYERS
formatted_players_str = "INITIAL_PLAYERS: List[Dict[str, Any]] = [\n"
for p in players:
    formatted_players_str += "    " + repr(p) + ",\n"
formatted_players_str += "]\n\n"

# Reconstruct file
prefix = content[:match.start()]
suffix = content[match.end() - len("class NFLStatsService"):]

new_content = prefix + formatted_players_str + suffix

with open("backend/app/services/nfl_stats_service.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Tiers systematically calibrated!")
