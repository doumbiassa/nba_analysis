"""
Fetch real-time NBA stats using the nba_api package.
Run this script to overwrite the CSV files in data/ with live data.

Usage:
    pip install nba_api
    python fetch_live_data.py
"""

import time
import pandas as pd
from nba_api.stats.endpoints import (
    leaguedashteamstats,
    leaguedashplayerstats,
    leagueaverages,
)
from nba_api.stats.static import teams as nba_teams

SEASONS = [
    "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
    "2019-20", "2020-21", "2021-22", "2022-23", "2023-24",
]

CHAMPIONS = {
    "2014-15": "Golden State Warriors",
    "2015-16": "Cleveland Cavaliers",
    "2016-17": "Golden State Warriors",
    "2017-18": "Golden State Warriors",
    "2018-19": "Toronto Raptors",
    "2019-20": "Los Angeles Lakers",
    "2020-21": "Milwaukee Bucks",
    "2021-22": "Golden State Warriors",
    "2022-23": "Denver Nuggets",
    "2023-24": "Boston Celtics",
}


def fetch_league_averages():
    rows = []
    for season in SEASONS:
        print(f"  Fetching league averages: {season} ...", end=" ", flush=True)
        try:
            lg = leagueaverages.LeagueAverages(season=season, season_type_all_star="Regular Season")
            df = lg.get_data_frames()[0]
            row = df.iloc[0]
            rows.append({
                "season":        int(season[:4]) + 1,
                "season_label":  season,
                "pts_per_game":  round(row["PTS"], 1),
                "fg_pct":        round(row["FG_PCT"] * 100, 1),
                "3pa_per_game":  round(row["FG3A"], 1),
                "3pm_per_game":  round(row["FG3M"], 1),
                "3p_pct":        round(row["FG3_PCT"] * 100, 1),
                "champion":      CHAMPIONS[season],
            })
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
        time.sleep(1)
    return pd.DataFrame(rows)


def fetch_scoring_leaders():
    rows = []
    for season in SEASONS:
        print(f"  Fetching scoring leaders: {season} ...", end=" ", flush=True)
        try:
            ps = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season, season_type_all_star="Regular Season",
                per_mode_simple="PerGame",
            )
            df = ps.get_data_frames()[0]
            df = df[df["GP"] >= 30].copy()
            df["PPG"] = df["PTS"].astype(float)
            leader = df.sort_values("PPG", ascending=False).iloc[0]
            rows.append({
                "season":       int(season[:4]) + 1,
                "season_label": season,
                "player":       leader["PLAYER_NAME"],
                "team":         leader["TEAM_ABBREVIATION"],
                "ppg":          round(leader["PTS"], 1),
                "rpg":          round(leader["REB"], 1),
                "apg":          round(leader["AST"], 1),
                "fg_pct":       round(leader["FG_PCT"] * 100, 1),
                "games":        int(leader["GP"]),
            })
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
        time.sleep(1)
    return pd.DataFrame(rows)


def fetch_top_teams():
    rows = []
    for season in SEASONS:
        print(f"  Fetching team stats: {season} ...", end=" ", flush=True)
        try:
            ts = leaguedashteamstats.LeagueDashTeamStats(
                season=season, season_type_all_star="Regular Season",
                per_mode_simple="PerGame",
            )
            df = ts.get_data_frames()[0]
            df = df.sort_values("W", ascending=False).head(3)
            for _, row in df.iterrows():
                rows.append({
                    "season":       int(season[:4]) + 1,
                    "season_label": season,
                    "team":         row["TEAM_NAME"],
                    "wins":         int(row["W"]),
                    "losses":       int(row["L"]),
                    "win_pct":      round(row["W_PCT"], 3),
                    "pts_for":      round(row["PTS"], 1),
                })
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
        time.sleep(1)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("\n🏀 Fetching live NBA data ...\n")

    print("League Averages:")
    league_df = fetch_league_averages()
    league_df.to_csv("data/league_stats.csv", index=False)
    print(f"  → Saved {len(league_df)} rows to data/league_stats.csv\n")

    print("Scoring Leaders:")
    leaders_df = fetch_scoring_leaders()
    leaders_df.to_csv("data/scoring_leaders.csv", index=False)
    print(f"  → Saved {len(leaders_df)} rows to data/scoring_leaders.csv\n")

    print("Top Teams:")
    teams_df = fetch_top_teams()
    teams_df.to_csv("data/top_teams.csv", index=False)
    print(f"  → Saved {len(teams_df)} rows to data/top_teams.csv\n")

    print("✅ All data refreshed. Run nba_analysis.ipynb to see the updated plots.")
