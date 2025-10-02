import pandas as pd
import plotly.express as px
from espn_api.football import League

# Import league details and credentials from keys.py
from keys import LEAGUE_ID, SEASON_ID, SWID, ESPN_S2, get_team_colors

# Initialize the league
league = League(league_id=LEAGUE_ID, year=SEASON_ID, espn_s2=ESPN_S2, swid=SWID)
WEEK_NUMBER = league.current_week - 1
team_colors = get_team_colors()

# Create a dictionary to hold cumulative scores for each team
teams_cumulative_scores = {team.team_name: [0] * WEEK_NUMBER for team in league.teams}

# Gather scores for each week
for week in range(1, WEEK_NUMBER + 1):
    try:
        week_matchups = league.scoreboard(week)
    except Exception as e:
        print(f"Error fetching scoreboard for week {week}: {e}")
        continue

    for matchup in week_matchups:
        home_team = matchup.home_team
        away_team = matchup.away_team

        # Update scores for each team
        teams_cumulative_scores[home_team.team_name][week - 1] = home_team.scores[week - 1]
        teams_cumulative_scores[away_team.team_name][week - 1] = away_team.scores[week - 1]

# Convert to cumulative sums
for team in teams_cumulative_scores:
    teams_cumulative_scores[team] = pd.Series(teams_cumulative_scores[team]).cumsum()

# Reshape data into a DataFrame for Plotly
df = pd.DataFrame(teams_cumulative_scores)
df["Week"] = range(1, WEEK_NUMBER + 1)
df = df.melt(id_vars=["Week"], var_name="Team", value_name="Cumulative Points")

# team_colors is your dict from keys.py
team_order = list(team_colors.keys())

# Ensure Team is a categorical column with that order
df["Team"] = pd.Categorical(df["Team"], categories=team_order, ordered=True)

# Create interactive line chart
fig = px.line(
    df,
    x="Week",
    y="Cumulative Points",
    color="Team",
    markers=True,
    title="Cumulative Points",
    color_discrete_map=team_colors
)

# Improve layout
fig.update_layout(
    xaxis=dict(tickmode="linear", tick0=1, dtick=1),
    yaxis_title="Cumulative Points",
    legend_title="Teams",
    template="plotly_white"
)

fig.update_layout(
    legend=dict(
        title="Teams",
        orientation="h",      # horizontal legend
        yanchor="top",        # anchor legend to top of its box
        y=-0.25,              # push below chart (negative = outside plot area)
        xanchor="center",
        x=0.5,
        font=dict(size=9),    # smaller font size
        bgcolor="rgba(255,255,255,0.7)",  # semi-transparent background
    ),
    margin=dict(b=120)  # add extra space at bottom for legend
)


# Save interactive chart as standalone HTML
fig.write_html("Graphs/cumulative_points_graph.html", include_plotlyjs="cdn")
print("File saved as Graphs/cumulative_points_graph.html")
