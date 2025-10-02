import pandas as pd
import plotly.express as px
from espn_api.football import League

# Import league details and credentials from keys.py
from keys import LEAGUE_ID, SEASON_ID, SWID, ESPN_S2, get_team_colors

# Initialize the league
league = League(league_id=LEAGUE_ID, year=SEASON_ID, espn_s2=ESPN_S2, swid=SWID)
WEEK_NUMBER = league.current_week - 1
team_colors = get_team_colors()

# Create a dictionary to hold cumulative "points against" for each team
teams_cumulative_against = {team.team_name: [0] * WEEK_NUMBER for team in league.teams}

# Gather "points against" for each week
for week in range(1, WEEK_NUMBER + 1):
    try:
        week_matchups = league.scoreboard(week)
    except Exception as e:
        print(f"Error fetching scoreboard for week {week}: {e}")
        continue

    for matchup in week_matchups:
        home_team = matchup.home_team
        away_team = matchup.away_team

        # Points against is the *opponent’s* score
        teams_cumulative_against[home_team.team_name][week - 1] = away_team.scores[week - 1]
        teams_cumulative_against[away_team.team_name][week - 1] = home_team.scores[week - 1]

# Convert to cumulative sums
for team in teams_cumulative_against:
    teams_cumulative_against[team] = pd.Series(teams_cumulative_against[team]).cumsum()

# Reshape into DataFrame for Plotly
df_against = pd.DataFrame(teams_cumulative_against)
df_against["Week"] = range(1, WEEK_NUMBER + 1)
df_against = df_against.melt(id_vars=["Week"], var_name="Team", value_name="Cumulative Points Against")

# team_colors is your dict from keys.py
team_order = list(team_colors.keys())

# Ensure Team is a categorical column with that order
df_against["Team"] = pd.Categorical(df_against["Team"], categories=team_order, ordered=True)

# Create interactive line chart
fig_against = px.line(
    df_against,
    x="Week",
    y="Cumulative Points Against",
    color="Team",
    markers=True,
    title="Cumulative Points Against",
    color_discrete_map=team_colors
)

# Improve layout
fig_against.update_layout(
    xaxis=dict(tickmode="linear", tick0=1, dtick=1),
    yaxis_title="Cumulative Points Against",
    legend_title="Teams",
    template="plotly_white"
)

fig_against.update_layout(
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
fig_against.write_html("Graphs/cumulative_points_against.html", include_plotlyjs="cdn")
print("File saved as Graphs/cumulative_points_against.html")
