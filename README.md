# 🏀 10 Years of NBA Data Analysis (2014–2024)

A data science deep-dive into a decade of NBA statistics using Python, Pandas, Matplotlib, and Seaborn.

## What's Inside

| File | Description |
|---|---|
| `nba_analysis.ipynb` | Main Jupyter notebook — all analysis & plots |
| `fetch_live_data.py` | Script to pull real-time data from the NBA API |
| `data/league_stats.csv` | League-wide averages per season (pace, 3PA, PPG, TS%) |
| `data/scoring_leaders.csv` | Scoring champion each season |
| `data/top_teams.csv` | Best teams per season + playoff results |
| `data/player_careers.csv` | Season-by-season stats for Curry, LeBron, Harden, Giannis, KD |
| `plots/` | Saved high-res chart images |

## Key Findings

1. **Three-Point Revolution** — 3PA/game went from 22.4 → 35.1 (+57%) in 10 years
2. **Scoring Explosion** — League PPG rose from 100.0 → 114.8 (+14.8 pts/game)
3. **Harden's 2018-19** — 36.1 PPG, the highest in 30+ years
4. **GSW Dynasty** — 4 Championships in 10 years, including the all-time record 73-9 season
5. **LeBron James** — Still averaging 25+ PPG at age 39 — unprecedented longevity

## Setup

```bash
# Clone the repo
git clone https://github.com/doumbiassa/nba_analysis.git
cd nba_analysis

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook nba_analysis.ipynb
```

## Fetch Live Data (Optional)

The notebook ships with curated CSV data so it runs immediately. To update with real-time NBA API data:

```bash
python fetch_live_data.py
```

## Tools Used

- **Python 3.11+**
- **Pandas** — data manipulation
- **NumPy** — numerical computing
- **Matplotlib / Seaborn** — visualization
- **nba_api** — live data from stats.nba.com

---

*Analysis by Dr. Moussa Doumbia — Howard University, Department of Mathematics*
