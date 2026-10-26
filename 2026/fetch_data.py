"""
Pull 2026 league data from ESPN and write 2026/data.js for the dashboard.

Run from the project root:
    python 2026/fetch_data.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from espn_api.football import League

HERE = Path(__file__).resolve().parent          # .../2026
PROJECT_ROOT = HERE.parent                      # keys.py lives here
sys.path.insert(0, str(PROJECT_ROOT))

from keys import LEAGUE_ID, SWID, ESPN_S2, get_team_colors

SEASON = 2026
OUTPUT_FILE = HERE / "data.js"

league = League(league_id=LEAGUE_ID, year=SEASON, espn_s2=ESPN_S2, swid=SWID)

# Only use completed weeks, same as the 2025 scripts
completed_weeks = league.current_week - 1

# ---- Team weekly scores (used by the charts) ----
teams = []
for team in league.teams:
    teams.append({
        "id": team.team_id,
        "name": team.team_name,
        "weekly": [round(float(s), 1) for s in team.scores[:completed_weeks]],
    })

# ---- Standings (season totals and record) ----
standings = []
for team in league.teams:
    standings.append({
        "name": team.team_name,
        "wins": team.wins,
        "losses": team.losses,
        "points_for": round(team.points_for, 1),
        "points_against": round(team.points_against, 1),
    })
standings.sort(key=lambda s: (s["wins"], s["points_for"]), reverse=True)

# ---- Every matchup, week by week ----
matchups = []
for week in range(1, completed_weeks + 1):
    for m in league.scoreboard(week):
        # Skip bye weeks, where one side isn't a real team
        if not hasattr(m.home_team, "team_name") or not hasattr(m.away_team, "team_name"):
            continue

        home_score = round(m.home_score, 1)
        away_score = round(m.away_score, 1)
        if home_score > away_score:
            winner = "HOME"
        elif away_score > home_score:
            winner = "AWAY"
        else:
            winner = "TIE"

        matchups.append({
            "week": week,
            "home": m.home_team.team_name,
            "home_score": home_score,
            "away": m.away_team.team_name,
            "away_score": away_score,
            "winner": winner,
        })
        
# ---- Weekly points against (each team's opponent score) ----
opponent_score = {}
for mu in matchups:
    opponent_score[(mu["week"], mu["home"])] = mu["away_score"]
    opponent_score[(mu["week"], mu["away"])] = mu["home_score"]

for team in teams:
    # Bye weeks have no opponent, so they count as 0 against
    team["weekly_against"] = [
        opponent_score.get((week, team["name"]), 0)
        for week in range(1, completed_weeks + 1)
    ]

# ---- Team colors from keys.py ----
try:
    colors = get_team_colors()
except Exception as e:
    print(f"Could not load team colors: {e}")
    colors = {}

payload = {
    "season": SEASON,
    "completed_weeks": completed_weeks,
    "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "teams": teams,
    "standings": standings,
    "matchups": matchups,
    "colors": colors,
}

OUTPUT_FILE.write_text(
    "window.LEAGUE_DATA = " + json.dumps(payload, indent=2) + ";\n",
    encoding="utf-8",
)
print(f"Wrote {OUTPUT_FILE} ({completed_weeks} completed weeks, {len(teams)} teams)")