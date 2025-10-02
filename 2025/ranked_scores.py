import os
import pandas as pd
from espn_api.football import League
from keys import LEAGUE_ID, SEASON_ID, SWID, ESPN_S2  # store credentials in keys.py

# Initialize league
league = League(league_id=LEAGUE_ID, year=SEASON_ID, espn_s2=ESPN_S2, swid=SWID)

# Get the current week
current_week = league.current_week - 1

# Ensure "tables" subdirectory exists
os.makedirs("tables", exist_ok=True)

# ---------------------------
# Table 1: Ranked Scores Table
# ---------------------------
rows_scores = []

for week in range(1, current_week + 1):
    scoreboard = league.scoreboard(week=week)
    for match in scoreboard:
        for team in [match.home_team, match.away_team]:
            if team:
                rows_scores.append({
                    "Week": week,
                    "Team": team.team_name,
                    "Points": team.scores[week - 1]
                })

df_scores = pd.DataFrame(rows_scores)
df_scores = df_scores.sort_values(by="Points", ascending=False)
html_table_scores = df_scores.to_html(index=False, classes="points-table", border=0)

with open("tables/team_points.html", "w") as f:
    f.write(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Fantasy Ranked Scores</title>
        <link rel="stylesheet" href="../styles.css">
        <style>
            .points-table {{
                border-collapse: collapse;
                margin: 20px auto;
                width: 80%;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
            }}
            .points-table th, .points-table td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}
            .points-table th {{
                background: #004aad;
                color: white;
                font-weight: 600;
            }}
            .points-table tr:nth-child(even) {{
                background-color: #f2f6ff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="../index.html" class="back-button">Home</a>
            <h1>Fantasy Ranked Scores</h1>
            <p class="byline">Sorted from highest to lowest total points</p>
            {html_table_scores}
        </div>
    </body>
    </html>
    """)

print("✅ tables/team_points.html created")


# ---------------------------
# Table 2: Closest Games Table
# ---------------------------
rows_closest = []

for week in range(1, current_week + 1):
    scoreboard = league.scoreboard(week=week)
    for match in scoreboard:
        if match.home_team and match.away_team:
            home_points = match.home_score
            away_points = match.away_score

            if home_points > away_points:
                winner, loser = match.home_team, match.away_team
                win_score, lose_score = home_points, away_points
            else:
                winner, loser = match.away_team, match.home_team
                win_score, lose_score = away_points, home_points

            diff = abs(win_score - lose_score)

            rows_closest.append({
                "Week": week,
                "Winning Team": winner.team_name,
                "Losing Team": loser.team_name,
                "Winning Score": win_score,
                "Losing Score": lose_score,
                "Score Difference": diff
            })

df_closest = pd.DataFrame(rows_closest)
df_closest = df_closest.sort_values(by="Score Difference", ascending=True)
html_table_closest = df_closest.to_html(index=False, classes="points-table", border=0)

with open("tables/close_games.html", "w") as f:
    f.write(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Fantasy Closest Games</title>
        <link rel="stylesheet" href="../styles.css">
        <style>
            .points-table {{
                border-collapse: collapse;
                margin: 20px auto;
                width: 80%;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
            }}
            .points-table th, .points-table td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}
            .points-table th {{
                background: #004aad;
                color: white;
                font-weight: 600;
            }}
            .points-table tr:nth-child(even) {{
                background-color: #f2f6ff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="../index.html" class="back-button">Home</a>
            <h1>Fantasy Closest Games</h1>
            <p class="byline">Games with the smallest score differences</p>
            {html_table_closest}
        </div>
    </body>
    </html>
    """)

print("✅ tables/close_games.html created")
