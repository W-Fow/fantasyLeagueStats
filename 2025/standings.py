import pandas as pd
import plotly.express as px
from espn_api.football import League
from keys import LEAGUE_ID, SEASON_ID, SWID, ESPN_S2, get_team_colors

# Initialize league
league = League(league_id=LEAGUE_ID, year=SEASON_ID, espn_s2=ESPN_S2, swid=SWID)
current_week = league.current_week - 1  # use completed weeks only

team_colors = get_team_colors()
team_order = list(team_colors.keys())

# Track cumulative wins, losses, and points
records = {team.team_name: {"wins": 0, "losses": 0, "points_for": 0} for team in league.teams}

rows = []
for week in range(1, current_week + 1):
    matchups = league.scoreboard(week)
    for matchup in matchups:
        home, away = matchup.home_team, matchup.away_team
        home_score, away_score = home.scores[week - 1], away.scores[week - 1]

        # Update points for tiebreakers
        records[home.team_name]["points_for"] += home_score
        records[away.team_name]["points_for"] += away_score

        # Update wins/losses
        if home_score > away_score:
            records[home.team_name]["wins"] += 1
            records[away.team_name]["losses"] += 1
        elif away_score > home_score:
            records[away.team_name]["wins"] += 1
            records[home.team_name]["losses"] += 1
        # (ties ignored here, add handling if needed)

    # Build weekly standings sorted by record first, then points_for
    standings = sorted(
        records.items(),
        key=lambda x: (x[1]["wins"], x[1]["points_for"]),
        reverse=True
    )

    for rank, (team, rec) in enumerate(standings, start=1):
        rows.append({
            "Week": week,
            "Team": team,
            "Rank": rank,
            "Wins": rec["wins"],
            "Losses": rec["losses"],
            "Points For": rec["points_for"],
            "Record": f"{rec['wins']}-{rec['losses']}"
        })

# Build DataFrame
df = pd.DataFrame(rows)

# Ensure consistent legend order
df["Team"] = pd.Categorical(df["Team"], categories=team_order, ordered=True)

# Plot standings over time with record in hover
fig = px.line(
    df,
    x="Week",
    y="Rank",
    color="Team",
    markers=True,
    title="Standings Over Time",
    color_discrete_map=team_colors,
    category_orders={"Team": team_order},
    hover_data={"Record": True}
)

# Flip y-axis so Rank 1 is at the top
fig.update_layout(
    template="plotly_white",
    yaxis=dict(autorange="reversed"),
    legend=dict(
        title="Teams",
        orientation="h",
        yanchor="top",
        y=-0.25,
        xanchor="center",
        x=0.5,
        font=dict(size=9),
        bgcolor="rgba(255,255,255,0.7)"
    ),
    margin=dict(b=120)
)

fig.write_html("Graphs/standings_over_time.html", include_plotlyjs="cdn")
print("File saved as Graphs/standings_over_time.html")
