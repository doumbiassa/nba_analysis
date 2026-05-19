import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NBA 10-Year Analysis",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme constants ───────────────────────────────────────────────────────────
BG        = "#0f1117"
CARD_BG   = "#1a1d27"
BORDER    = "#2d3148"
NBA_BLUE  = "#1d428a"
NBA_RED   = "#c8102e"
NBA_GOLD  = "#ffc72c"
TEXT_MAIN = "#e8eaf6"
TEXT_DIM  = "#8a8db0"
PLASMA    = px.colors.sequential.Plasma

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* App background */
  .stApp {{ background: {BG}; color: {TEXT_MAIN}; }}
  [data-testid="stSidebar"] {{ background: #12141f; border-right: 1px solid {BORDER}; }}

  /* Hide Streamlit branding */
  #MainMenu, footer, header {{ visibility: hidden; }}

  /* Metric cards */
  .kpi-row {{ display: flex; gap: 14px; margin-bottom: 28px; flex-wrap: wrap; }}
  .kpi-card {{
    flex: 1; min-width: 140px;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
  }}
  .kpi-value {{ font-size: 32px; font-weight: 800; line-height: 1.1; }}
  .kpi-label {{ font-size: 11px; font-weight: 600; letter-spacing: 1px;
                text-transform: uppercase; color: {TEXT_DIM}; margin-top: 5px; }}
  .kpi-delta {{ font-size: 12px; margin-top: 4px; }}
  .up   {{ color: #4ade80; }}
  .down {{ color: #f87171; }}

  /* Section headers */
  .section-title {{
    font-size: 20px; font-weight: 700; color: {TEXT_MAIN};
    border-left: 4px solid {NBA_GOLD};
    padding-left: 12px; margin: 28px 0 14px;
  }}

  /* Insight boxes */
  .insight {{
    background: #1e2235;
    border: 1px solid {BORDER};
    border-left: 4px solid {NBA_GOLD};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: {TEXT_DIM};
    margin-top: 8px;
  }}
  .insight b {{ color: {TEXT_MAIN}; }}
</style>
""", unsafe_allow_html=True)

# ── Plotly base layout ────────────────────────────────────────────────────────
def base_layout(**kwargs):
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_MAIN, family="Inter, system-ui, sans-serif"),
        margin=dict(l=50, r=30, t=50, b=50),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, showgrid=True),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, showgrid=True),
        **kwargs,
    )

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    league  = pd.read_csv("data/league_stats.csv")
    leaders = pd.read_csv("data/scoring_leaders.csv")
    teams   = pd.read_csv("data/top_teams.csv")
    careers = pd.read_csv("data/player_careers.csv")
    return league, leaders, teams, careers

league, leaders, teams, careers = load_data()

PLAYERS   = sorted(careers["player"].unique())
SEASONS   = sorted(league["season"].unique())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 10px 0 18px;'>
      <div style='font-size:40px'>🏀</div>
      <div style='font-size:18px; font-weight:800; color:{TEXT_MAIN}'>NBA Analysis</div>
      <div style='font-size:12px; color:{TEXT_DIM}'>2014–15 to 2023–24</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;font-weight:700;letter-spacing:1px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:8px'>Season Range</div>", unsafe_allow_html=True)
    season_range = st.slider(
        "Season range", min_value=int(SEASONS[0]), max_value=int(SEASONS[-1]),
        value=(int(SEASONS[0]), int(SEASONS[-1])), label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;font-weight:700;letter-spacing:1px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:8px'>Players to Compare</div>", unsafe_allow_html=True)
    selected_players = st.multiselect(
        "Players", PLAYERS,
        default=["Stephen Curry", "LeBron James", "James Harden", "Giannis Antetokounmpo"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px;font-weight:700;letter-spacing:1px;color:{TEXT_DIM};text-transform:uppercase;margin-bottom:8px'>Metric — Career Arc</div>", unsafe_allow_html=True)
    arc_metric = st.selectbox(
        "Metric", ["ppg", "ts_pct", "3pm", "rpg", "apg"],
        format_func=lambda x: {
            "ppg": "Points Per Game",
            "ts_pct": "True Shooting %",
            "3pm": "3-Pointers Made",
            "rpg": "Rebounds Per Game",
            "apg": "Assists Per Game",
        }[x],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(f"<small style='color:{TEXT_DIM}'>By <b style='color:{TEXT_MAIN}'>Dr. Moussa Doumbia</b><br>Howard University · Dept. of Mathematics</small>", unsafe_allow_html=True)

# ── Filter data by sidebar range ──────────────────────────────────────────────
lg = league[(league["season"] >= season_range[0]) & (league["season"] <= season_range[1])].copy()
ld = leaders[(leaders["season"] >= season_range[0]) & (leaders["season"] <= season_range[1])].copy()
ca = careers[(careers["season"] >= season_range[0]) & (careers["season"] <= season_range[1])].copy()
if selected_players:
    ca = ca[ca["player"].isin(selected_players)]

# ── Page title ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='padding: 10px 0 4px;'>
  <div style='font-size:28px; font-weight:900; color:{TEXT_MAIN}; line-height:1.1'>
    🏀 10 Years of NBA Data
    <span style='color:{NBA_GOLD}'>— What the Numbers Say</span>
  </div>
  <div style='font-size:14px; color:{TEXT_DIM}; margin-top:6px'>
    Seasons {season_range[0]-1}–{str(season_range[0])[-2:]} through {season_range[1]-1}–{str(season_range[1])[-2:]}
    &nbsp;·&nbsp; {season_range[1]-season_range[0]+1} seasons selected
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════
ppg_start  = lg["pts_per_game"].iloc[0]
ppg_end    = lg["pts_per_game"].iloc[-1]
tpa_start  = lg["3pa_per_game"].iloc[0]
tpa_end    = lg["3pa_per_game"].iloc[-1]
top_scorer = ld.loc[ld["ppg"].idxmax()]
peak_ppg   = ld["ppg"].max()
gsw_rings  = (lg["champion"] == "Golden State Warriors").sum()

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-value" style="color:{NBA_GOLD}">{ppg_end}</div>
    <div class="kpi-label">Avg PPG (latest)</div>
    <div class="kpi-delta {'up' if ppg_end>ppg_start else 'down'}">
      {'▲' if ppg_end>ppg_start else '▼'} {abs(ppg_end-ppg_start):.1f} vs start
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#a78bfa">{tpa_end}</div>
    <div class="kpi-label">3PA / Game (latest)</div>
    <div class="kpi-delta up">▲ {tpa_end-tpa_start:.1f} ({(tpa_end-tpa_start)/tpa_start*100:.0f}%)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:{NBA_RED}">{peak_ppg}</div>
    <div class="kpi-label">Peak Single-Season PPG</div>
    <div class="kpi-delta" style="color:{TEXT_DIM}">{top_scorer['player'].split()[-1]} · {top_scorer['season_label']}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#4ade80">{gsw_rings}</div>
    <div class="kpi-label">GS Warriors Titles</div>
    <div class="kpi-delta" style="color:{TEXT_DIM}">of {len(lg)} championships</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color:#38bdf8">{lg['ts_pct'].iloc[-1]}%</div>
    <div class="kpi-label">True Shooting % (latest)</div>
    <div class="kpi-delta up">▲ {lg['ts_pct'].iloc[-1]-lg['ts_pct'].iloc[0]:.1f}pp all-time high</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 1. THREE-POINT REVOLUTION
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">1 · The Three-Point Revolution</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=lg["season_label"], y=lg["3pa_per_game"],
        mode="lines+markers",
        line=dict(color=NBA_GOLD, width=3),
        marker=dict(size=9, color=NBA_GOLD, line=dict(color=BG, width=2)),
        fill="tozeroy", fillcolor="rgba(255,199,44,0.10)",
        name="3PA/Game",
        hovertemplate="<b>%{x}</b><br>3PA per game: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=lg["season_label"], y=lg["3pm_per_game"],
        mode="lines+markers",
        line=dict(color="#a78bfa", width=2, dash="dot"),
        marker=dict(size=7, color="#a78bfa"),
        name="3PM/Game",
        hovertemplate="<b>%{x}</b><br>3PM per game: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **base_layout(title="3-Point Attempts & Makes Per Game"),
        legend=dict(bgcolor=CARD_BG, bordercolor=BORDER, x=0.02, y=0.97),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=lg["pace"], y=lg["pts_per_game"],
        mode="markers+text",
        marker=dict(
            size=14, color=lg["season"],
            colorscale="Plasma", showscale=True,
            colorbar=dict(title="Season", tickfont=dict(color=TEXT_MAIN)),
            line=dict(color=BG, width=1.5),
        ),
        text=[f"'{str(s)[-2:]}" for s in lg["season"]],
        textposition="top center",
        textfont=dict(size=10, color=TEXT_DIM),
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "Pace: %{x:.1f}<br>PPG: %{y:.1f}<extra></extra>"
        ),
        customdata=lg["season_label"],
        name="",
    ))
    # Trend line
    z = np.polyfit(lg["pace"], lg["pts_per_game"], 1)
    x_trend = np.linspace(lg["pace"].min(), lg["pace"].max(), 80)
    fig2.add_trace(go.Scatter(
        x=x_trend, y=np.polyval(z, x_trend),
        mode="lines", line=dict(color=NBA_RED, width=2, dash="dash"),
        name="Trend", showlegend=True,
    ))
    corr = lg["pace"].corr(lg["pts_per_game"])
    fig2.update_layout(
        **base_layout(title=f"Pace vs Scoring (r = {corr:.2f})"),
        xaxis_title="Pace (possessions/48 min)",
        yaxis_title="Points Per Game",
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown(f"""<div class="insight">
💡 <b>3-point attempts surged +{(tpa_end-tpa_start)/tpa_start*100:.0f}%</b> over the decade ({tpa_start} → {tpa_end} per game).
Pace and scoring are strongly correlated (r = {corr:.2f}) — faster games mean more points, but smarter shot selection drove efficiency gains too.
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 2. SCORING EXPLOSION
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">2 · Scoring Explosion — Is the NBA Too Easy?</div>', unsafe_allow_html=True)

col3, col4 = st.columns([3, 2])

with col3:
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=lg["season_label"],
        y=lg["pts_per_game"],
        marker=dict(
            color=lg["pts_per_game"],
            colorscale="Plasma",
            line=dict(color=BG, width=0.6),
        ),
        text=lg["pts_per_game"].round(1),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_MAIN),
        hovertemplate=(
            "<b>%{x}</b><br>PPG: %{y:.1f}<br>Champion: %{customdata}<extra></extra>"
        ),
        customdata=lg["champion"],
        name="PPG",
    ))
    fig3.add_trace(go.Scatter(
        x=lg["season_label"], y=lg["pts_per_game"],
        mode="lines", line=dict(color=NBA_GOLD, width=2),
        name="Trend", showlegend=False,
    ))
    fig3.update_layout(
        **base_layout(title="League Average Points Per Game by Season"),
        yaxis=dict(range=[94, 120], gridcolor=BORDER),
        xaxis=dict(tickangle=-35),
        bargap=0.25, showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    metrics = ["pts_per_game", "fg_pct", "3p_pct", "ts_pct"]
    labels  = ["PPG", "FG%", "3P%", "TS%"]
    fig4 = make_subplots(rows=4, cols=1, shared_xaxes=True,
                         vertical_spacing=0.06,
                         subplot_titles=labels)
    colors = [NBA_GOLD, "#4ade80", "#a78bfa", "#38bdf8"]
    for i, (m, c) in enumerate(zip(metrics, colors), start=1):
        fig4.add_trace(go.Scatter(
            x=lg["season_label"], y=lg[m],
            mode="lines+markers", line=dict(color=c, width=2),
            marker=dict(size=5, color=c), name=labels[i-1],
            hovertemplate=f"<b>%{{x}}</b><br>{labels[i-1]}: %{{y}}<extra></extra>",
        ), row=i, col=1)
        fig4.update_yaxes(
            gridcolor=BORDER, linecolor=BORDER,
            tickfont=dict(size=9), row=i, col=1
        )
    fig4.update_xaxes(tickangle=-45, tickfont=dict(size=8))
    fig4.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_MAIN),
        height=380, margin=dict(l=40, r=10, t=30, b=40),
        showlegend=False,
        title="Key Efficiency Metrics Over Time",
    )
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 3. SCORING LEADERS
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">3 · Who Dominated Scoring?</div>', unsafe_allow_html=True)

col5, col6 = st.columns([3, 2])

PLAYER_COLORS = {
    "Russell Westbrook": "#007AC1",
    "Stephen Curry":     "#FFC72C",
    "James Harden":      "#CE1141",
    "Joel Embiid":       "#006BB6",
    "Luka Doncic":       "#00538C",
}

with col5:
    ld_sorted = ld.sort_values("season")
    bar_colors = [PLAYER_COLORS.get(p, "#8a8db0") for p in ld_sorted["player"]]
    fig5 = go.Figure(go.Bar(
        x=ld_sorted["ppg"],
        y=ld_sorted["season_label"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color=BG, width=0.6)),
        text=[f"{row['player']}  {row['ppg']} PPG" for _, row in ld_sorted.iterrows()],
        textposition="inside",
        textfont=dict(size=11, color="white"),
        hovertemplate=(
            "<b>%{y}</b><br>%{text}<br>"
            "RPG: %{customdata[0]} · APG: %{customdata[1]}<extra></extra>"
        ),
        customdata=ld_sorted[["rpg", "apg"]].values,
    ))
    fig5.update_layout(
        **base_layout(title="Scoring Champion Each Season"),
        xaxis=dict(range=[0, 43], title="Points Per Game"),
        yaxis=dict(title=""),
        height=380,
    )
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    counts = ld["player"].value_counts().reset_index()
    counts.columns = ["player", "titles"]
    pie_colors = [PLAYER_COLORS.get(p, "#8a8db0") for p in counts["player"]]
    fig6 = go.Figure(go.Pie(
        labels=counts["player"],
        values=counts["titles"],
        marker=dict(colors=pie_colors, line=dict(color=BG, width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="white"),
        hole=0.42,
        hovertemplate="<b>%{label}</b><br>%{value} scoring title(s)<extra></extra>",
    ))
    fig6.add_annotation(
        text=f"<b>{len(ld)}</b><br><span style='font-size:10px'>seasons</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=TEXT_MAIN),
    )
    fig6.update_layout(
        paper_bgcolor=BG,
        font=dict(color=TEXT_MAIN),
        title="Share of Scoring Titles",
        showlegend=False,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig6, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 4. DYNASTY WATCH
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">4 · Dynasty Watch — Championships</div>', unsafe_allow_html=True)

champs = lg["champion"].value_counts().reset_index()
champs.columns = ["team", "titles"]
TEAM_COLORS = {
    "Golden State Warriors": "#FFC72C",
    "Cleveland Cavaliers":   "#860038",
    "Toronto Raptors":       "#CE1141",
    "Los Angeles Lakers":    "#552583",
    "Milwaukee Bucks":       "#00471B",
    "Denver Nuggets":        "#4fa8d5",
    "Boston Celtics":        "#007A33",
}
col7, col8 = st.columns([2, 3])

with col7:
    fig7 = go.Figure(go.Bar(
        x=champs["titles"],
        y=champs["team"],
        orientation="h",
        marker=dict(
            color=[TEAM_COLORS.get(t, NBA_BLUE) for t in champs["team"]],
            line=dict(color=BG, width=0.8),
        ),
        text=["💍" * t + f"  ({t})" for t in champs["titles"]],
        textposition="outside",
        textfont=dict(size=13),
        hovertemplate="<b>%{y}</b><br>%{x} championship(s)<extra></extra>",
    ))
    fig7.update_layout(
        **base_layout(title="Championships Won"),
        xaxis=dict(range=[0, champs["titles"].max() + 1.5], title="Titles"),
        yaxis=dict(title=""),
        height=320,
    )
    st.plotly_chart(fig7, use_container_width=True)

with col8:
    # Timeline: who won each year
    fig8 = go.Figure()
    for i, (_, row) in enumerate(lg.iterrows()):
        team = row["champion"]
        color = TEAM_COLORS.get(team, NBA_BLUE)
        fig8.add_trace(go.Bar(
            x=[row["season_label"]],
            y=[1],
            name=team,
            marker_color=color,
            showlegend=(team not in [t for _, r in lg.iterrows()
                                     for t in [r["champion"]]
                                     if list(lg["champion"]).index(team) < i]),
            text=team.replace("Golden State ", "GS ").replace(
                "Los Angeles ", "LA ").replace("Cleveland ", "CLE ").replace(
                "Toronto ", "TOR ").replace("Milwaukee ", "MIL ").replace(
                "Denver ", "DEN ").replace("Boston ", "BOS "),
            textposition="inside",
            textfont=dict(size=10, color="white"),
            hovertemplate=f"<b>{team}</b><br>{row['season_label']} Champion<extra></extra>",
        ))
    seen = set()
    for trace in fig8.data:
        if trace.name in seen:
            trace.showlegend = False
        seen.add(trace.name)
    fig8.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_MAIN),
        title="Championship Timeline",
        barmode="stack",
        xaxis=dict(tickangle=-35, gridcolor=BORDER),
        yaxis=dict(showticklabels=False, gridcolor=BORDER),
        legend=dict(bgcolor=CARD_BG, bordercolor=BORDER,
                    font=dict(size=10), orientation="h",
                    yanchor="bottom", y=1.02),
        height=320,
        margin=dict(l=20, r=20, t=60, b=60),
    )
    st.plotly_chart(fig8, use_container_width=True)

st.markdown(f"""<div class="insight">
💡 <b>Golden State Warriors dominated the decade</b> — {gsw_rings} titles in 10 years ({gsw_rings/len(lg)*100:.0f}% of all championships).
Their historic 73-9 season (2015-16) remains the best record in NBA history.
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# 5. PLAYER CAREER ARCS
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">5 · Superstar Career Arcs</div>', unsafe_allow_html=True)

CAREER_COLORS = ["#FFC72C", "#CE1141", "#a78bfa", "#4ade80", "#38bdf8"]
METRIC_LABELS = {
    "ppg": "Points Per Game",
    "ts_pct": "True Shooting %",
    "3pm": "3-Pointers Made",
    "rpg": "Rebounds Per Game",
    "apg": "Assists Per Game",
}

if not selected_players:
    st.info("Select at least one player in the sidebar.")
else:
    fig9 = go.Figure()
    for player, color in zip(selected_players, CAREER_COLORS):
        df_p = ca[ca["player"] == player].sort_values("season")
        if df_p.empty:
            continue
        fig9.add_trace(go.Scatter(
            x=df_p["season_label"],
            y=df_p[arc_metric],
            mode="lines+markers",
            name=player,
            line=dict(color=color, width=2.5),
            marker=dict(size=9, color=color, line=dict(color=BG, width=1.5)),
            fill="tozeroy",
            fillcolor=color.replace("#", "rgba(") + ",0.07)" if color.startswith("#") else color,
            hovertemplate=(
                f"<b>{player}</b><br>"
                f"{METRIC_LABELS[arc_metric]}: %{{y}}<br>Age: %{{customdata}}<extra></extra>"
            ),
            customdata=df_p["age"],
        ))
        # Peak annotation
        peak_idx = df_p[arc_metric].idxmax()
        peak_val = df_p.loc[peak_idx, arc_metric]
        peak_sea = df_p.loc[peak_idx, "season_label"]
        fig9.add_annotation(
            x=peak_sea, y=peak_val,
            text=f"▲ {peak_val}",
            showarrow=True, arrowhead=2, arrowcolor=color,
            font=dict(size=10, color=color),
            ax=0, ay=-28,
        )

    fig9.update_layout(
        **base_layout(title=f"{METRIC_LABELS[arc_metric]} — Career Arc Comparison"),
        hovermode="x unified",
        legend=dict(bgcolor=CARD_BG, bordercolor=BORDER,
                    orientation="h", yanchor="bottom", y=1.02,
                    font=dict(size=11)),
        xaxis=dict(tickangle=-35),
        height=430,
    )
    st.plotly_chart(fig9, use_container_width=True)

    # Age vs metric scatter
    if arc_metric == "ppg":
        st.markdown(f"<div style='font-size:14px;font-weight:600;color:{TEXT_DIM};margin-bottom:6px'>Age vs {METRIC_LABELS[arc_metric]} — Does performance decline with age?</div>", unsafe_allow_html=True)
        fig10 = go.Figure()
        for player, color in zip(selected_players, CAREER_COLORS):
            df_p = ca[ca["player"] == player].sort_values("age")
            if df_p.empty:
                continue
            fig10.add_trace(go.Scatter(
                x=df_p["age"], y=df_p[arc_metric],
                mode="markers+lines",
                name=player,
                marker=dict(size=10, color=color, line=dict(color=BG, width=1)),
                line=dict(color=color, width=1.5, dash="dot"),
                hovertemplate=f"<b>{player}</b> — Age %{{x}}<br>{METRIC_LABELS[arc_metric]}: %{{y}}<extra></extra>",
            ))
        fig10.update_layout(
            **base_layout(title=f"Age vs {METRIC_LABELS[arc_metric]}"),
            xaxis_title="Age", yaxis_title=METRIC_LABELS[arc_metric],
            hovermode="x unified",
            legend=dict(bgcolor=CARD_BG, bordercolor=BORDER, font=dict(size=11)),
            height=340,
        )
        st.plotly_chart(fig10, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 6. EFFICIENCY SCATTER (BUBBLE CHART)
# ═══════════════════════════════════════════════════════
st.markdown('<div class="section-title">6 · Scoring vs Efficiency — Bubble = 3PM</div>', unsafe_allow_html=True)

avg_stats = (
    careers.groupby("player")[["ppg", "rpg", "apg", "ts_pct", "3pm"]]
    .mean().reset_index().sort_values("ppg", ascending=False)
)

fig11 = go.Figure()
colors_bubble = [PLAYER_COLORS.get(p, "#8a8db0") for p in avg_stats["player"]]

fig11.add_trace(go.Scatter(
    x=avg_stats["ts_pct"],
    y=avg_stats["ppg"],
    mode="markers+text",
    marker=dict(
        size=avg_stats["3pm"] / 3,
        color=colors_bubble,
        opacity=0.88,
        line=dict(color="white", width=1.5),
        sizemode="diameter",
    ),
    text=avg_stats["player"].apply(lambda n: n.split()[-1]),
    textposition="top center",
    textfont=dict(size=11, color="white"),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "PPG: %{y:.1f}  ·  TS%: %{x:.1f}<br>"
        "3PM/season: %{customdata[1]:.0f}<br>"
        "RPG: %{customdata[2]:.1f}  ·  APG: %{customdata[3]:.1f}<extra></extra>"
    ),
    customdata=avg_stats[["player", "3pm", "rpg", "apg"]].values,
))

# Average lines
avg_ts = avg_stats["ts_pct"].mean()
avg_ppg = avg_stats["ppg"].mean()
fig11.add_vline(x=avg_ts, line=dict(color=NBA_GOLD, dash="dash", width=1.5),
                annotation_text="Avg TS%", annotation_font_color=NBA_GOLD)
fig11.add_hline(y=avg_ppg, line=dict(color=NBA_RED, dash="dash", width=1.5),
                annotation_text="Avg PPG", annotation_font_color=NBA_RED)

fig11.update_layout(
    **base_layout(title="10-Year Avg: True Shooting % vs PPG  (bubble = 3PM per season)"),
    xaxis_title="True Shooting % (10-yr avg)",
    yaxis_title="Points Per Game (10-yr avg)",
    height=450,
    showlegend=False,
)
st.plotly_chart(fig11, use_container_width=True)

# ═══════════════════════════════════════════════════════
# 7. RAW DATA TABLE
# ═══════════════════════════════════════════════════════
with st.expander("📋 View Raw League Stats Table"):
    st.dataframe(
        lg[["season_label", "pts_per_game", "3pa_per_game", "3pm_per_game",
            "3p_pct", "ts_pct", "pace", "fg_pct", "champion"]]
        .rename(columns={
            "season_label": "Season",
            "pts_per_game": "PPG",
            "3pa_per_game": "3PA",
            "3pm_per_game": "3PM",
            "3p_pct": "3P%",
            "ts_pct": "TS%",
            "pace": "Pace",
            "fg_pct": "FG%",
            "champion": "Champion",
        }),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("📋 View Scoring Leaders Table"):
    st.dataframe(
        ld[["season_label", "player", "team", "ppg", "rpg", "apg", "fg_pct", "games"]]
        .rename(columns={
            "season_label": "Season", "player": "Player", "team": "Team",
            "ppg": "PPG", "rpg": "RPG", "apg": "APG",
            "fg_pct": "FG%", "games": "GP",
        }),
        use_container_width=True,
        hide_index=True,
    )

# ═══════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════
st.markdown(f"""
<div style='margin-top:48px; padding-top:20px; border-top:1px solid {BORDER};
     text-align:center; font-size:12px; color:{TEXT_DIM}'>
  🏀 NBA 10-Year Analysis Dashboard &nbsp;·&nbsp;
  <b style='color:{TEXT_MAIN}'>Dr. Moussa Doumbia</b> &nbsp;·&nbsp;
  Howard University, Department of Mathematics &nbsp;·&nbsp;
  <a href='https://github.com/doumbiassa/nba_analysis'
     style='color:{NBA_GOLD};text-decoration:none'>
    github.com/doumbiassa/nba_analysis
  </a>
</div>
""", unsafe_allow_html=True)
