import re
from backend.app.services.generate_players import EXPANDED_PLAYERS
from backend.app.services.skill_players import SKILL_PLAYERS

# Read current nfl_stats_service.py
with open("backend/app/services/nfl_stats_service.py", "r", encoding="utf-8") as f:
    content = f.read()

# Extract existing INITIAL_PLAYERS
match = re.search(r'INITIAL_PLAYERS:\s*List\[Dict\[str,\s*Any\]\]\s*=\s*(\[[\s\S]*?\])\s*class\s+NFLStatsService', content)
if not match:
    print("Could not find INITIAL_PLAYERS regex match")
    exit(1)

import ast
existing_players = ast.literal_eval(match.group(1))

# Merge players by ID (avoiding duplicate IDs)
seen_ids = set()
merged_players = []

for p in existing_players:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        merged_players.append(p)

for p in EXPANDED_PLAYERS:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        merged_players.append(p)

for p in SKILL_PLAYERS:
    if p["id"] not in seen_ids:
        seen_ids.add(p["id"])
        merged_players.append(p)


print(f"Total merged players: {len(merged_players)}")

# Format Python code for INITIAL_PLAYERS
formatted_players_str = "INITIAL_PLAYERS: List[Dict[str, Any]] = [\n"
for p in merged_players:
    formatted_players_str += "    " + repr(p) + ",\n"
formatted_players_str += "]\n\n"

# Reconstruct file
prefix = content[:match.start()]
suffix = content[match.end() - len("class NFLStatsService"):]

new_content = prefix + formatted_players_str + suffix

with open("backend/app/services/nfl_stats_service.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("nfl_stats_service.py successfully updated!")
