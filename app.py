# ============================================================
# PRISM CRICKET TEAM BALANCER — STREAMLIT FRONTEND
# ============================================================
# Keep balancing and session business logic in the backend.
# This file is presentation and interaction only.
# ============================================================

import html
import streamlit as st
from st_keyup import st_keyup

from backend.player_service import PlayerService
from backend.session_manager import CricketSession
from backend.team_balancer import team_stats, player_strength


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Prism Cricket Team Balancer",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# VISUAL THEME
# ============================================================
# Palette: navy #0B1220 | panel #152238 | lime #B7F34A
# Lime buttons use dark text for accessible contrast.
# ============================================================

st.markdown(
    """
    <style>
      :root {
        --prism-bg: #0B1220;
        --prism-panel: #152238;
        --prism-panel-2: #1B2B43;
        --prism-lime: #B7F34A;
        --prism-text: #F5F7FA;
        --prism-muted: #AAB6C8;
        --prism-border: rgba(210,224,245,.13);
      }
      .stApp { background:var(--prism-bg); color:var(--prism-text); }
      [data-testid="stHeader"] { display:none; }
      [data-testid="stSidebar"] { display:none; }
      .block-container { max-width:1160px; padding-top:1.5rem; padding-bottom:3.5rem; }
      [data-testid="stMainMenu"] { display:none !important; }
      [data-testid="stToolbar"] { display:none !important; }
      h1,h2,h3,h4,p,label,[data-testid="stMarkdownContainer"] { color:var(--prism-text); }
      h1 { letter-spacing:-.045em; font-weight:800; }
      h2,h3 { letter-spacing:-.025em; }
      [data-testid="stCaptionContainer"] { color:var(--prism-muted); }
      hr { border-color:var(--prism-border); }
      .prism-eyebrow { color:var(--prism-lime); text-transform:uppercase; letter-spacing:.17em; font-size:.7rem; font-weight:850; margin-bottom:.25rem; }
      .prism-subtitle { color:var(--prism-muted); font-size:.94rem; margin-top:-.55rem; margin-bottom:1.2rem; }
      .prism-muted { color:var(--prism-muted); }

      div[data-testid="stTextInput"] input {
        background:var(--prism-panel); color:var(--prism-text); border:1px solid var(--prism-border);
        border-radius:12px; min-height:2.7rem;
      }
      div[data-testid="stTextInput"] input:focus { border-color:var(--prism-lime); box-shadow:0 0 0 1px var(--prism-lime); }

      /* Selection summary + action live in one shared card. */
      .st-key-selection-action-card {
        background:linear-gradient(145deg,#192A40 0%,#111D30 100%);
        border:1px solid var(--prism-border); border-radius:17px; padding:.7rem .9rem;
        margin:.15rem 0 1rem;
      }
      .prism-selection-card { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.15rem 0; }
      .prism-selection-label { color:var(--prism-muted); font-size:.75rem; font-weight:750; letter-spacing:.06em; text-transform:uppercase; }
      .prism-selection-count { font-size:1.55rem; line-height:1.2; font-weight:850; color:var(--prism-text); }
      .prism-selection-hint { color:var(--prism-muted); font-size:.76rem; margin-top:.18rem; }

      /* The checkbox is overlaid at the lower-right inside the visual player card. */
      [class*="st-key-player-selection-row-"], [class*="st-key-team-a-player-"],
      [class*="st-key-team-b-player-"], [class*="st-key-mobile-team-player-"] {
        margin:0 0 .82rem 0 !important; padding:0 !important;
      }
      [class*="st-key-player-selection-row-"] [data-testid="stHorizontalBlock"],
      [class*="st-key-team-a-player-"] [data-testid="stHorizontalBlock"],
      [class*="st-key-team-b-player-"] [data-testid="stHorizontalBlock"],
      [class*="st-key-mobile-team-player-"] [data-testid="stHorizontalBlock"] {
        position:relative !important; align-items:stretch !important; gap:0 !important; padding:0 !important;
        border:0 !important; background:transparent !important; box-shadow:none !important; margin:0 !important;
      }
      [class*="st-key-player-selection-row-"] [data-testid="column"],
      [class*="st-key-team-a-player-"] [data-testid="column"],
      [class*="st-key-team-b-player-"] [data-testid="column"],
      [class*="st-key-mobile-team-player-"] [data-testid="column"] { min-width:0 !important; }
      [class*="st-key-player-selection-row-"] [data-testid="column"]:first-child,
      [class*="st-key-team-a-player-"] [data-testid="column"]:first-child,
      [class*="st-key-team-b-player-"] [data-testid="column"]:first-child,
      [class*="st-key-mobile-team-player-"] [data-testid="column"]:first-child {
        width:100% !important; max-width:100% !important; flex:1 1 100% !important;
      }
      [class*="st-key-player-selection-row-"] [data-testid="column"]:last-child,
      [class*="st-key-team-a-player-"] [data-testid="column"]:last-child,
      [class*="st-key-team-b-player-"] [data-testid="column"]:last-child,
      [class*="st-key-mobile-team-player-"] [data-testid="column"]:last-child {
        position:absolute !important; right:.62rem !important; bottom:.35rem !important; z-index:3 !important;
        width:2rem !important; max-width:2rem !important; flex:0 0 2rem !important;
      }
      [class*="st-key-player-selection-row-"] .prism-player-card,
      [class*="st-key-team-a-player-"] .prism-player-card,
      [class*="st-key-team-b-player-"] .prism-player-card,
      [class*="st-key-mobile-team-player-"] .prism-player-card { margin:0 !important; height:100%; }
      [data-testid="stCheckbox"] { display:flex; align-items:center; justify-content:center; min-width:1.7rem; }
      [data-testid="stCheckbox"] label { gap:0 !important; }
      [data-testid="stCheckbox"] label > div:last-child { display:none !important; }
      [data-testid="stCheckbox"] input { accent-color:var(--prism-lime); }
      .prism-player-card.is-selected { border:1.5px solid var(--prism-lime); box-shadow:inset 4px 0 0 var(--prism-lime),0 4px 14px rgba(0,0,0,.18); background:linear-gradient(145deg,#20364F 0%,#14243A 100%); }
      .prism-role { color:#D8E1EF; font-weight:800; }
      .prism-total { color:var(--prism-lime); font-weight:850; }
      /* Primary action */
      button[kind="primary"], button[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primary"] {
        background:var(--prism-lime) !important; color:#101827 !important; border:1px solid var(--prism-lime) !important;
        border-radius:12px; font-weight:850; min-height:2.85rem; box-shadow:none;
      }
      button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primary"]:hover { background:#C9FF70 !important; color:#101827 !important; border-color:#C9FF70 !important; transform:translateY(-1px); }
      button[kind="primary"] *, button[data-testid="stBaseButton-primary"] *, [data-testid="stBaseButton-primary"] * { color:#101827 !important; fill:#101827 !important; }
      div.stButton > button:not([kind="primary"]) { border-radius:12px; border-color:var(--prism-border); min-height:2.85rem; height:2.85rem; }
      .st-key-selection-action-card [data-testid="stButton"] > button { width:100% !important; min-height:2.85rem !important; height:2.85rem !important; white-space:nowrap !important; padding:.5rem .55rem !important; font-size:.82rem !important; font-weight:850 !important; }
      .st-key-selection-action-card [data-testid="stButton"] { width:100% !important; }

      /* Team summary cards */
      .prism-team-card {
        background:linear-gradient(145deg,#192A40 0%,#111D30 100%);
        border:1px solid var(--prism-border); border-radius:18px; padding:1rem 1.05rem .9rem; min-height:260px;
        transition:border-color .16s ease, box-shadow .16s ease;
      }
      .prism-team-card.is-selected { border:1.5px solid var(--prism-lime); box-shadow:0 0 0 1px rgba(183,243,74,.16),0 8px 24px rgba(0,0,0,.16); }
      .prism-team-summary-head { display:flex; align-items:flex-start; justify-content:space-between; gap:.5rem; }
      .prism-selected-tag { color:#101827; background:var(--prism-lime); border-radius:999px; padding:.18rem .48rem; font-size:.62rem; font-weight:900; letter-spacing:.04em; }
      .prism-shared-tag { color:#101827; background:var(--prism-lime); border-radius:999px; padding:.12rem .42rem; font-size:.62rem; font-weight:900; margin-left:.4rem; white-space:nowrap; }
      .prism-team-title { font-size:1rem; font-weight:850; margin-bottom:.15rem; }
      .prism-team-score { color:var(--prism-lime); font-size:1.8rem; font-weight:900; letter-spacing:-.045em; }
      .prism-team-small { color:var(--prism-muted); font-size:.76rem; }
      .prism-stat-pill { display:inline-block; margin:.18rem .2rem .02rem 0; padding:.25rem .45rem; border:1px solid var(--prism-border); border-radius:8px; font-size:.7rem; color:var(--prism-text); background:rgba(255,255,255,.025); }
      .prism-stat-pill b { color:var(--prism-lime); }
      .prism-bar-row { display:grid; grid-template-columns:58px 1fr 38px; gap:8px; align-items:center; margin-top:.52rem; }
      .prism-bar-label { color:var(--prism-muted); font-size:.73rem; }
      .prism-bar-track { height:6px; background:#2A3B52; border-radius:99px; overflow:hidden; }
      .prism-bar-fill { height:100%; background:var(--prism-lime); border-radius:99px; }
      .prism-bar-value { font-size:.72rem; font-weight:750; text-align:right; }
      .prism-mobile-summary-lines { display:none; }
      .prism-mobile-summary-line { color:var(--prism-text); font-size:.66rem; line-height:1.45; white-space:nowrap; letter-spacing:-.015em; }
      .prism-mobile-summary-line strong { color:var(--prism-lime); font-weight:850; }

      .st-key-team-a-card-select, .st-key-team-b-card-select { display:none !important; }
      .st-key-team-a-desktop, .st-key-team-b-desktop, .st-key-desktop-team-summaries { display:block; }
      .st-key-mobile-team-list, .st-key-mobile-summary-buttons { display:none; }

      /* Player details below the team cards */
      .prism-player-card { border:1px solid rgba(210,224,245,.16); border-radius:14px; padding:.85rem .9rem; margin:0 0 .9rem 0; background:linear-gradient(145deg,rgba(25,42,64,.96),rgba(17,29,48,.96)); }
      .prism-player-card.has-select-control { padding-bottom:.72rem; }
      .prism-player-card.has-select-control .prism-player-card-skills { padding-right:2.05rem; }
      .prism-player-card.shared { border-color:rgba(183,243,74,.42); }
      .prism-player-card-top { display:flex; justify-content:space-between; gap:.5rem; align-items:center; }
      .prism-player-card-name { display:flex; align-items:center; flex-wrap:wrap; min-width:0; font-size:1.02rem; font-weight:850; }
      .prism-player-card-rank { color:var(--prism-lime); font-size:.86rem; font-weight:900; white-space:nowrap; }
      .prism-player-card-score { color:var(--prism-lime); font-size:1.2rem; line-height:1.1; font-weight:900; white-space:nowrap; }
      .prism-player-card-skills { display:flex; flex-wrap:wrap; gap:.32rem .8rem; color:#C5D0E0; font-size:.84rem; margin-top:.5rem; }
      .prism-player-card-skills b { color:var(--prism-text); font-weight:850; font-size:.9rem; }
      .prism-player-card-footer { margin-top:.34rem; }
      .prism-role { color:#AAB6C8 !important; font-size:.65rem !important; letter-spacing:.09em; font-weight:750; }

      /* The Streamlit dialog is centered by Streamlit; keep it on-brand. */
      [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p { color:var(--prism-text); }
      [data-testid="stDialog"] { border:1px solid var(--prism-border); }

      @media (max-width:760px) {
        .block-container { padding-left:.85rem; padding-right:.85rem; padding-top:.8rem; }
        .prism-team-card { transition:none !important; }
        h1 { font-size:1.85rem !important; }
        h2 { font-size:1.3rem !important; }
        .prism-team-card { min-height:0; padding:.8rem; }
        .prism-bar-row { display:none; }
        .prism-team-small { font-size:.67rem; }
        .prism-team-title { font-size:.88rem; }
        .prism-team-score { font-size:1.35rem; }
        .prism-selected-tag { font-size:.55rem; padding:.15rem .35rem; }
        .prism-player-card-top { align-items:flex-start; }
        .prism-player-card-name { overflow-wrap:anywhere; }
        .prism-player-card-rank { flex-shrink:0; }
        .prism-stat-pill { font-size:.64rem; padding:.22rem .34rem; }
        .prism-player-meta { font-size:.69rem; }
        [class*="st-key-player-selection-row-"] { margin-bottom:.82rem !important; }
        [class*="st-key-team-a-desktop"] [data-testid="stElementContainer"],
        [class*="st-key-team-b-desktop"] [data-testid="stElementContainer"],
        [class*="st-key-mobile-team-list"] [data-testid="stElementContainer"] { margin-bottom:.8rem !important; }
        .st-key-team-a-desktop, .st-key-team-b-desktop, .st-key-desktop-team-summaries { display:none; }
        .st-key-mobile-team-list, .st-key-mobile-summary-buttons { display:block; }
        /* Mobile summary cards use the same HTML card as desktop, sized to half-width columns. */
        .st-key-mobile-summary-buttons [data-testid="stHorizontalBlock"] {
          display:grid !important; grid-template-columns:minmax(0,1fr) minmax(0,1fr) !important;
          grid-auto-flow:column !important; align-items:stretch !important; gap:.45rem !important;
          width:100% !important; min-width:0 !important; margin:0 !important;
        }
        .st-key-mobile-summary-buttons [data-testid="column"] {
          width:100% !important; min-width:0 !important; max-width:none !important;
          flex:none !important; padding:0 !important; margin:0 !important;
        }
        .st-key-mobile-summary-buttons .prism-team-card { min-width:0; min-height:0; height:100%; padding:.68rem .48rem; border-radius:14px; overflow:hidden; }
        .st-key-mobile-summary-buttons .prism-team-summary-head { gap:.15rem; }
        .st-key-mobile-summary-buttons .prism-selected-tag { display:none !important; }
        .st-key-mobile-summary-buttons .prism-team-title { font-size:.8rem; }
        .st-key-mobile-summary-buttons .prism-team-score { font-size:1.22rem; }
        .st-key-mobile-summary-buttons .prism-team-small { font-size:.61rem; line-height:1.3; }
        .st-key-mobile-summary-buttons .prism-stat-grid,
        .st-key-mobile-summary-buttons .prism-role-count-pills { display:none !important; }
        .st-key-mobile-summary-buttons .prism-mobile-summary-lines { display:block !important; margin-top:.42rem; }
        .st-key-mobile-summary-buttons .prism-mobile-summary-line { font-size:clamp(.54rem, 2.3vw, .66rem); line-height:1.55; letter-spacing:-.025em; }
        .st-key-mobile-summary-buttons [data-testid="stButton"] { width:100% !important; margin-top:.4rem !important; }
        .st-key-mobile-summary-buttons [data-testid="stButton"] > button {
          width:100% !important; min-height:2.1rem !important; height:2.1rem !important; padding:.35rem .3rem !important;
          font-size:.68rem !important; line-height:1.15 !important; white-space:normal !important;
          border:1px solid rgba(210,224,245,.2) !important; border-radius:9px !important; transition:none !important;
        }
        .st-key-mobile-summary-buttons .prism-stat-grid { display:block; }
        [class*="st-key-player-selection-row-"] [data-testid="stHorizontalBlock"] { gap:.4rem !important; }
        .prism-player-card-name { font-size:1rem; }
        .prism-player-card-score { font-size:1.12rem; }
        .prism-player-card-skills { font-size:.78rem; gap:.22rem .48rem; }
        .prism-role { font-size:.62rem !important; }
        .st-key-team-a-card-select, .st-key-team-b-card-select { display:none !important; }
        .st-key-team-card-a, .st-key-team-card-b { position:relative; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SERVICES AND SESSION STATE
# ============================================================

@st.cache_resource
def get_player_service():
    return PlayerService("players.csv")


@st.cache_data
def get_master_players():
    return get_player_service().load_master_players()


master_players = get_master_players()

if "cricket_session" not in st.session_state:
    st.session_state.cricket_session = CricketSession()

session = st.session_state.cricket_session


# ============================================================
# HELPERS
# ============================================================

def player_role(player):
    batsman = bool(player.get("is_batsman", False))
    bowler = bool(player.get("is_bowler", False))
    if batsman and bowler:
        return "ALL-ROUNDER"
    if batsman:
        return "BATTER"
    if bowler:
        return "BOWLER"
    return "FIELD"


def player_score(player):
    """Use the existing backend's weighted individual-strength score."""
    return float(player_strength(player))


def ranked_players(players):
    return sorted(players, key=lambda p: (-player_score(p), p["name"].casefold()))


def role_counts(team):
    counts = {"batters": 0, "bowlers": 0, "all_rounders": 0, "field_players": 0}
    for player in team:
        batsman = bool(player.get("is_batsman", False))
        bowler = bool(player.get("is_bowler", False))
        if batsman and bowler:
            counts["all_rounders"] += 1
        elif batsman:
            counts["batters"] += 1
        elif bowler:
            counts["bowlers"] += 1
        else:
            counts["field_players"] += 1
    return counts


def render_skill_bar(label, value):
    value = max(0.0, min(10.0, float(value)))
    st.markdown(
        f'''<div class="prism-bar-row">
          <div class="prism-bar-label">{html.escape(label)}</div>
          <div class="prism-bar-track"><div class="prism-bar-fill" style="width:{value * 10:.1f}%"></div></div>
          <div class="prism-bar-value">{value:.2f}</div>
        </div>''',
        unsafe_allow_html=True,
    )


def render_team_summary(team_name, team, selected=False):
    'Render total skills and impact counts provided by the backend.'
    stats = team_stats(team)
    roles = role_counts(team)
    selected_tag = '<span class="prism-selected-tag">PLAYERS SHOWN</span>' if selected else ''
    selected_class = " is-selected" if selected else ""

    batting_total = float(stats.get("batting", 0.0) or 0.0)
    bowling_total = float(stats.get("bowling", 0.0) or 0.0)
    fielding_total = float(stats.get("fielding", 0.0) or 0.0)
    strength_total = float(stats.get("strength", 0.0) or 0.0)
    player_count = len(team)
    max_skill_total = max(1.0, player_count * 10.0)

    elite_batters = int(stats.get("elite_batters", 0) or 0)
    elite_bowlers = int(stats.get("elite_bowlers", 0) or 0)
    strong_batters = int(stats.get("strong_batters", 0) or 0)
    strong_bowlers = int(stats.get("strong_bowlers", 0) or 0)
    fielders = int(stats.get("fielders", 0) or 0)

    st.markdown(
        f'''<div class="prism-team-card{selected_class}">
          <div class="prism-team-summary-head"><div>
            <div class="prism-team-title">{html.escape(team_name)}</div>
            <div class="prism-team-score">{strength_total:.2f}</div>
            <div class="prism-team-small">TEAM STRENGTH · {player_count} PLAYERS</div>
          </div>{selected_tag}</div>
          <div class="prism-stat-grid" style="margin-top:.55rem">
            <span class="prism-stat-pill"><b>{elite_batters}</b> Elite Batters</span>
            <span class="prism-stat-pill"><b>{elite_bowlers}</b> Elite Bowlers</span>
            <span class="prism-stat-pill"><b>{strong_batters}</b> Strong Batters</span>
            <span class="prism-stat-pill"><b>{strong_bowlers}</b> Strong Bowlers</span>
          </div>
          <div class="prism-role-count-pills" style="margin-top:.25rem">
            <span class="prism-stat-pill"><b>{roles['batters']}</b> Batters</span>
            <span class="prism-stat-pill"><b>{roles['bowlers']}</b> Bowlers</span>
            <span class="prism-stat-pill"><b>{roles['all_rounders']}</b> All-rounders</span>
            <span class="prism-stat-pill"><b>{roles['field_players']}</b> Fielders</span>
          </div>
          <div class="prism-mobile-summary-lines">
            <div class="prism-mobile-summary-line">Bat <strong>{batting_total:.2f}</strong> · Elite {elite_batters} · Strong {strong_batters}</div>
            <div class="prism-mobile-summary-line">Bowl <strong>{bowling_total:.2f}</strong> · Elite {elite_bowlers} · Strong {strong_bowlers}</div>
            <div class="prism-mobile-summary-line">Field <strong>{fielding_total:.2f}</strong> · Fielder {fielders}</div>
          </div>
          <div class="prism-bar-row"><div class="prism-bar-label">Batting</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(100.0,batting_total / max_skill_total * 100)):.1f}%"></div></div><div class="prism-bar-value">{batting_total:.2f}</div></div>
          <div class="prism-bar-row"><div class="prism-bar-label">Bowling</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(100.0,bowling_total / max_skill_total * 100)):.1f}%"></div></div><div class="prism-bar-value">{bowling_total:.2f}</div></div>
          <div class="prism-bar-row"><div class="prism-bar-label">Fielding</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(100.0,fielding_total / max_skill_total * 100)):.1f}%"></div></div><div class="prism-bar-value">{fielding_total:.2f}</div></div>
        </div>''',
        unsafe_allow_html=True,
    )

def player_card_html(player, rank_lookup, shared_names=None, selected=False, selectable=False):
    """Return the shared player-card markup used on selection and team pages."""
    name = html.escape(str(player["name"]))
    role = html.escape(player_role(player))
    rank = rank_lookup.get(player["name"], "—")
    score = player_score(player)
    shared_names = shared_names or set()
    is_shared = player["name"] in shared_names
    classes = ["prism-player-card"]
    if is_shared:
        classes.append("shared")
    if selected:
        classes.append("is-selected")
    if selectable:
        classes.append("has-select-control")
    shared_tag = '<span class="prism-shared-tag">SHARED</span>' if is_shared else ""
    return f"""<div class="{' '.join(classes)}">
      <div class="prism-player-card-top">
        <div class="prism-player-card-name"><span class="prism-player-card-rank">#{rank}</span>&nbsp; {name}{shared_tag}</div>
        <div class="prism-player-card-score">{score:.2f}</div>
      </div>
      <div class="prism-player-card-footer"><span class="prism-role">{role}</span></div>
      <div class="prism-player-card-skills">
        <span>BAT <b>{float(player['batting']):.2f}</b></span>
        <span>BOWL <b>{float(player['bowling']):.2f}</b></span>
        <span>FIELD <b>{float(player['fielding']):.2f}</b></span>
      </div>
    </div>"""


def render_player_card(
    player,
    rank_lookup,
    shared_names=None,
    *,
    selected=False,
    checkbox_key=None,
    checkbox_disabled=False,
    container_key=None,
    on_change=None,
):
    'Render the shared HTML card, with its checkbox visually overlaid inside the card.'
    name = player["name"]
    with st.container(key=container_key) if container_key else st.container():
        card_col, checkbox_col = st.columns([1, 0.001], gap="small", vertical_alignment="center")
        with card_col:
            st.markdown(
                player_card_html(
                    player, rank_lookup, shared_names,
                    selected=selected, selectable=checkbox_key is not None,
                ),
                unsafe_allow_html=True,
            )
        with checkbox_col:
            if checkbox_key is not None:
                # Disabled checked controls serve as roster indicators in Team View.
                if checkbox_key not in st.session_state and checkbox_disabled:
                    st.session_state[checkbox_key] = True
                st.checkbox(
                    f"Select {name}",
                    key=checkbox_key,
                    disabled=checkbox_disabled,
                    label_visibility="collapsed",
                    on_change=on_change,
                    args=(name,) if on_change else None,
                )


def assignment_from_teams(team_result):
    team_a_names = {p["name"] for p in team_result["team_a"]}
    team_b_names = {p["name"] for p in team_result["team_b"]}
    assignment = {}
    for name in team_a_names & team_b_names:
        assignment[name] = "SHARED"
    for name in team_a_names - team_b_names:
        assignment[name] = "A"
    for name in team_b_names - team_a_names:
        assignment[name] = "B"
    return assignment


def display_changes(previous, current):
    """Compactly explain changes between matches when useful during testing."""
    if not previous:
        return
    old_assign = assignment_from_teams(previous)
    new_assign = assignment_from_teams(current)
    old_names, new_names = set(old_assign), set(new_assign)
    joined = sorted(new_names - old_names)
    left = sorted(old_names - new_names)
    moved = sorted((name, old_assign[name], new_assign[name]) for name in old_names & new_names
                   if old_assign[name] in ("A", "B") and new_assign[name] in ("A", "B") and old_assign[name] != new_assign[name])
    became_shared = sorted(name for name in old_names & new_names if old_assign[name] in ("A", "B") and new_assign[name] == "SHARED")
    no_longer_shared = sorted((name, new_assign[name]) for name in old_names & new_names if old_assign[name] == "SHARED" and new_assign[name] in ("A", "B"))
    parts = []
    if joined:
        parts.append("**Joined:** " + ", ".join(joined))
    if left:
        parts.append("**Left:** " + ", ".join(left))
    if moved:
        parts.append("**Moved:** " + "; ".join(f"{n} ({a} → {b})" for n, a, b in moved))
    if became_shared:
        parts.append("**Now shared:** " + ", ".join(became_shared))
    if no_longer_shared:
        parts.append("**No longer shared:** " + "; ".join(f"{n} → Team {t}" for n, t in no_longer_shared))
    st.caption("  ·  ".join(parts) if parts else "No player changes from the previous match.")


def selection_key(name):
    return f"select_player_{name}"


def sync_selection_widget_state(players):
    """Initialize widget values from durable selected-name state."""
    selected = st.session_state.setdefault("selected_player_names", set())
    for player in players:
        key = selection_key(player["name"])
        if key not in st.session_state:
            st.session_state[key] = player["name"] in selected


def on_player_checkbox_change(name):
    """Persist checkbox changes separately from widgets that search may hide."""
    selected = set(st.session_state.get("selected_player_names", set()))
    if st.session_state.get(selection_key(name), False):
        selected.add(name)
    else:
        selected.discard(name)
    st.session_state.selected_player_names = selected


def toggle_player_from_row(name):
    """Make the player detail area a click target as well as the checkbox."""
    selected = set(st.session_state.get("selected_player_names", set()))
    key = selection_key(name)
    if name in selected:
        selected.remove(name)
        st.session_state[key] = False
    else:
        selected.add(name)
        st.session_state[key] = True
    st.session_state.selected_player_names = selected


def set_selection(names, players):
    names = set(names)
    st.session_state.selected_player_names = names
    for player in players:
        st.session_state[selection_key(player["name"])] = player["name"] in names


def clear_selection_state(players):
    st.session_state.selected_player_names = set()
    for player in players:
        st.session_state.pop(selection_key(player["name"]), None)
    st.session_state.pop("match1_search", None)
    st.session_state.pop("edit_players_mode", None)
    st.session_state.pop("confirm_reset", None)
    st.session_state.pop("previous_match", None)
    st.session_state.pop("mobile_team_view", None)


@st.dialog(" ")
def reset_session_dialog():
    confirm_col, cancel_col = st.columns(2)
    with confirm_col:
        if st.button("Reset", type="primary", use_container_width=True, key="dialog_confirm_reset"):
            st.session_state.cricket_session = CricketSession()
            clear_selection_state(master_players)
            st.rerun()
    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="dialog_cancel_reset"):
            st.rerun()


# ============================================================
# APP HEADER
# ============================================================

# Keep the generated-team view intentionally minimal. The product header is
# shown only on the selection screen, not above the Team A / Team B cards.
edit_mode = bool(st.session_state.get("edit_players_mode", False))
if session.match_number == 0 or edit_mode:
    st.markdown('<div class="prism-eyebrow">PRISM · SUNDAY CRICKET</div>', unsafe_allow_html=True)
    st.title("Team Balancer")
    st.markdown('<div class="prism-subtitle">Balanced teams. Minimal reshuffling. Ready for match day.</div>', unsafe_allow_html=True)
    ranked_master = ranked_players(master_players)
    rank_lookup = {player["name"]: rank for rank, player in enumerate(ranked_master, start=1)}

    # For the first match, initialize an empty selection. For edit mode,
    # the current session's players are selected before this view is shown.
    if "selected_player_names" not in st.session_state:
        st.session_state.selected_player_names = set()

    st.markdown("## Select Players")
    search_text = st_keyup(
        "Search players", placeholder="Search by player name", key="match1_search_keyup",
        debounce=120, label_visibility="collapsed",
    ) or ""

    filtered_players = [p for p in ranked_master if p["name"].casefold().startswith(search_text.strip().casefold())]

    # Durable selected-name state is separate from visible checkbox widgets.
    # This prevents Streamlit from losing selections when search hides rows.
    selected_names = set(st.session_state.get("selected_player_names", set()))
    selected_players = [p for p in ranked_master if p["name"] in selected_names]
    generate_label = "Generate Teams" if session.match_number == 0 else "Generate Next Match"

    # Keep the selection count and primary action together inside one card,
    # positioned before the ranked player list for easy access.
    with st.container(key="selection-action-card"):
        action_count_col, clear_col, action_button_col = st.columns([1, 1, 1], vertical_alignment="center")
        with action_count_col:
            st.markdown(
                f'''<div class="prism-selection-card"><div><div class="prism-selection-label">Selected players</div>
                <div class="prism-selection-count">{len(selected_players)}</div>
                <div class="prism-selection-hint">Minimum 2 players</div></div></div>''',
                unsafe_allow_html=True,
            )
        with clear_col:
            if selected_players and st.button("Clear selection", use_container_width=True, key="clear_selected_players"):
                st.session_state.selected_player_names = set()
                for _player in ranked_master:
                    st.session_state.pop(selection_key(_player["name"]), None)
                st.session_state.pop("match1_search", None)
                st.session_state.pop("match1_search_keyup", None)
                st.rerun()
        with action_button_col:
            if st.button(generate_label, type="primary", disabled=len(selected_players) < 2, use_container_width=True, key="generate_selected_squad"):
                if session.match_number == 0:
                    session.set_initial_players(selected_players)
                    session.generate_match()
                    st.session_state.pop("previous_match", None)
                else:
                    # Reconcile selection through the existing session methods so the
                    # backend's add/remove and reshuffle behavior remains authoritative.
                    selected_by_name = {p["name"]: p for p in selected_players}
                    current_by_name = {p["name"]: p for p in session.players}
                    for current_name in list(current_by_name):
                        if current_name not in selected_by_name:
                            session.remove_player(current_name)
                    for selected_name, player in selected_by_name.items():
                        if selected_name not in current_by_name:
                            session.add_player(player)
                    previous = session.current_teams
                    session.generate_match()
                    st.session_state.previous_match = previous
                st.session_state.pop("edit_players_mode", None)
                st.session_state.pop("mobile_team_view", None)
                st.rerun()

    # Render a real HTML card for reliable typography/layout, with a native checkbox
    # as the selection control. This avoids Streamlit button labels flattening into text.
    for player in filtered_players:
        name = player["name"]
        rank = rank_lookup[name]  # Player rank comes from the master-ranked list.
        is_selected = name in selected_names
        checkbox_key = selection_key(name)
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = is_selected
        render_player_card(
            player,
            rank_lookup,
            selected=is_selected,
            checkbox_key=checkbox_key,
            checkbox_disabled=False,
            container_key=f"player-selection-row-{'selected-' if is_selected else ''}{rank}",
            on_change=on_player_checkbox_change,
        )



# ============================================================
# GENERATED MATCH — TEAM CARDS AND PLAYER DETAILS ONLY
# ============================================================

if session.current_teams and not st.session_state.get("edit_players_mode", False):
    result = session.current_teams
    team_a = result["team_a"]
    team_b = result["team_b"]

    ranked_master = ranked_players(master_players)
    rank_lookup = {player["name"]: rank for rank, player in enumerate(ranked_master, start=1)}

    # Desktop shows both summary cards. Mobile reuses the same HTML card design,
    # with a separate compact control for switching the player list below.
    if "mobile_team_view" not in st.session_state:
        st.session_state.mobile_team_view = "A"
    shared_names = {p["name"] for p in team_a} & {p["name"] for p in team_b}
    with st.container(key="desktop-team-summaries"):
        summary_a, summary_b = st.columns(2, gap="medium")
        with summary_a:
            render_team_summary("Team A", team_a, selected=False)
        with summary_b:
            render_team_summary("Team B", team_b, selected=False)

    with st.container(key="mobile-summary-buttons"):
        mobile_a, mobile_b = st.columns(2, gap="small")
        for team_label, team, column, team_key in [
            ("Team A", team_a, mobile_a, "A"), ("Team B", team_b, mobile_b, "B")
        ]:
            is_mobile_selected = st.session_state.mobile_team_view == team_key
            with column:
                render_team_summary(team_label, team, selected=is_mobile_selected)
                st.button(
                    "Viewing players" if is_mobile_selected else f"View {team_label}",
                    key=f"mobile_team_card_{team_key}",
                    use_container_width=True,
                    on_click=lambda k=team_key: st.session_state.update({"mobile_team_view": k}),
                )

    ordered_a = sorted(team_a, key=lambda p: (p["name"] not in shared_names, -player_score(p), p["name"].casefold()))
    ordered_b = sorted(team_b, key=lambda p: (p["name"] not in shared_names, -player_score(p), p["name"].casefold()))
    desktop_a, desktop_b = st.columns(2, gap="medium")
    with desktop_a:
        with st.container(key="team-a-desktop"):
            for player in ordered_a:
                rank = rank_lookup[player["name"]]
                render_player_card(
                    player, rank_lookup, shared_names, selected=False,
                    checkbox_key=f"team_view_a_checkbox_{rank}", checkbox_disabled=True,
                    container_key=f"team-a-player-{rank}",
                )
    with desktop_b:
        with st.container(key="team-b-desktop"):
            for player in ordered_b:
                rank = rank_lookup[player["name"]]
                render_player_card(
                    player, rank_lookup, shared_names, selected=False,
                    checkbox_key=f"team_view_b_checkbox_{rank}", checkbox_disabled=True,
                    container_key=f"team-b-player-{rank}",
                )

    with st.container(key="mobile-team-list"):
        mobile_team_key = st.session_state.mobile_team_view
        mobile_team = ordered_a if mobile_team_key == "A" else ordered_b
        for player in mobile_team:
            rank = rank_lookup[player["name"]]
            render_player_card(
                player, rank_lookup, shared_names, selected=False,
                checkbox_key=f"mobile_team_view_checkbox_{mobile_team_key}_{rank}", checkbox_disabled=True,
                container_key=f"mobile-team-player-{rank}",
            )

    # Controls stay at the bottom of the team view.
    action_edit, action_reset = st.columns(2, gap="medium")
    with action_edit:
        if st.button("Edit players", use_container_width=True, key="edit_players_from_team_view"):
            set_selection([p["name"] for p in session.players], ranked_master)
            st.session_state.edit_players_mode = True
            st.session_state.pop("match1_search", None)
            st.session_state.pop("match1_search_keyup", None)
            st.rerun()
    with action_reset:
        if st.button("Reset session", use_container_width=True, key="reset_from_team_view"):
            reset_session_dialog()

# No sidebar controls and no standalone Manual Team Builder / Comparison UI.
