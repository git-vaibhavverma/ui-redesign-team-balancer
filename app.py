# ============================================================
# PRISM CRICKET TEAM BALANCER — STREAMLIT FRONTEND
# ============================================================
# Keep balancing and session business logic in the backend.
# This file is presentation and interaction only.
# ============================================================

import html
import streamlit as st

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

      /* Player rows */
      [class*="st-key-player-selection-row-"] {
        position:relative; background:rgba(21,34,56,.58); border:1px solid var(--prism-border); border-radius:13px;
        padding:.52rem .72rem; margin-bottom:.42rem; transition:transform .16s ease, border-color .16s ease, background .16s ease, box-shadow .16s ease;
      }
      [class*="st-key-player-selection-row-"]:hover {
        transform:translateY(-2px); border-color:rgba(183,243,74,.55); background:#182941;
        box-shadow:0 8px 22px rgba(0,0,0,.18);
      }
      [class*="st-key-player-selection-row-"] [data-testid="stHorizontalBlock"] { align-items:center; gap:.55rem; }
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] { margin-top:0; }
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] label { padding:0; }
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] label p { display:none; }
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] { position:relative; z-index:4; }
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] input,
      [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] label { pointer-events:auto; }
      .prism-rank { color:var(--prism-lime); font-size:.75rem; font-weight:850; white-space:nowrap; }
      .prism-player-name { color:var(--prism-text); font-size:.94rem; font-weight:780; line-height:1.25; }
      .prism-player-meta { color:var(--prism-muted); font-size:.74rem; margin-top:.28rem; line-height:1.5; }
      .prism-role { color:#D8E1EF; border:1px solid var(--prism-border); border-radius:999px; padding:.12rem .42rem; font-size:.64rem; font-weight:800; display:inline-block; white-space:nowrap; }
      .prism-total { color:var(--prism-lime); font-weight:850; font-size:.96rem; text-align:right; white-space:nowrap; }
      .prism-skill-label { color:var(--prism-muted); font-size:.66rem; text-align:right; }
      .prism-row-click-hint { display:none; }

      /* Streamlit button inside the details area acts as a full-row click target. */
      [class*="st-key-player-selection-row-"] [data-testid="stButton"] {
        position:absolute !important; inset:0 !important; z-index:2; opacity:0 !important;
        width:100% !important; height:100% !important; margin:0 !important; padding:0 !important;
        pointer-events:none;
      }
      [class*="st-key-player-selection-row-"] [data-testid="stButton"] > button { pointer-events:auto; }
      [class*="st-key-player-selection-row-"] [data-testid="stButton"] > button {
        position:absolute; inset:0; width:100%; height:100%; min-height:100%; background:transparent; color:var(--prism-text); border:0; border-radius:8px;
        padding:0; box-shadow:none; text-align:left; font-size:.01rem; line-height:.01rem;
      }
      [class*="st-key-player-selection-row-"] [data-testid="stButton"] > button:hover { background:rgba(183,243,74,.07); color:var(--prism-text); border:0; }

      /* Primary action */
      div.stButton > button[kind="primary"], div.stButton > button[data-testid="stBaseButton-primary"] {
        background:var(--prism-lime) !important; color:#101827 !important; border:1px solid var(--prism-lime) !important;
        border-radius:12px; font-weight:850; min-height:2.85rem; box-shadow:none;
      }
      div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="stBaseButton-primary"]:hover { background:#C9FF70 !important; color:#101827 !important; border-color:#C9FF70 !important; transform:translateY(-1px); }
      div.stButton > button:not([kind="primary"]) { border-radius:11px; border-color:var(--prism-border); min-height:2.55rem; }

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

      .st-key-team-a-card-select, .st-key-team-b-card-select { display:none; }
      .st-key-team-a-desktop, .st-key-team-b-desktop { display:block; }
      .st-key-mobile-team-list { display:none; }

      /* Player details below the team cards */
      .prism-player-card { border:1px solid var(--prism-border); border-radius:13px; padding:.7rem .8rem; margin-bottom:.45rem; background:rgba(21,34,56,.58); }
      .prism-player-card.shared { border-color:rgba(183,243,74,.42); }
      .prism-player-card-top { display:flex; justify-content:space-between; gap:.5rem; align-items:center; }
      .prism-player-card-name { display:flex; align-items:center; flex-wrap:wrap; min-width:0; font-size:.9rem; font-weight:780; }
      .prism-player-card-rank { color:var(--prism-lime); font-size:.72rem; font-weight:850; white-space:nowrap; }
      .prism-player-card-skills { display:flex; flex-wrap:wrap; gap:.28rem .7rem; color:var(--prism-muted); font-size:.72rem; margin-top:.43rem; }
      .prism-player-card-skills b { color:var(--prism-text); font-weight:750; }
      .prism-player-card-footer { margin-top:.38rem; }

      /* The Streamlit dialog is centered by Streamlit; keep it on-brand. */
      [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p { color:var(--prism-text); }
      [data-testid="stDialog"] { border:1px solid var(--prism-border); }

      @media (max-width:760px) {
        .block-container { padding-left:.85rem; padding-right:.85rem; padding-top:.8rem; }
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
        [class*="st-key-player-selection-row-"] { padding:.48rem .42rem; }
        .st-key-team-a-desktop, .st-key-team-b-desktop { display:none; }
        .st-key-mobile-team-list { display:block; }
        .st-key-team-a-card-select, .st-key-team-b-card-select { display:block; position:absolute !important; inset:0 !important; opacity:0; z-index:10; pointer-events:none; }
        .st-key-team-a-card-select [data-testid="stButton"], .st-key-team-b-card-select [data-testid="stButton"] { position:absolute !important; inset:0 !important; height:100% !important; width:100% !important; pointer-events:auto; }
        .st-key-team-a-card-select button, .st-key-team-b-card-select button { position:absolute; inset:0; width:100%; height:100%; min-height:100%; padding:0; }
        .st-key-team-card-a, .st-key-team-card-b { position:relative; }

        [class*="st-key-player-selection-row-"] [data-testid="stHorizontalBlock"] { gap:.25rem; }
        [class*="st-key-player-selection-row-"] [data-testid="stCheckbox"] { min-width:1.35rem; }
        [class*="st-key-player-selection-row-"] .prism-player-name { overflow-wrap:anywhere; }
        [class*="st-key-player-selection-row-"] [data-testid="stMarkdownContainer"] { min-width:0; }
        .st-key-selection-action-card div.stButton > button[kind="primary"] { color:#101827 !important; }
        .st-key-team-a-card-select, .st-key-team-b-card-select { inset:0 !important; }
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


def team_skill_averages(team):
    if not team:
        return {"batting": 0.0, "bowling": 0.0, "fielding": 0.0}
    return {skill: sum(float(p[skill]) for p in team) / len(team) for skill in ("batting", "bowling", "fielding")}


def team_impact_counts(team):
    scores = [player_score(player) for player in team]
    return {"elite": sum(score >= 9 for score in scores), "strong": sum(8 <= score < 9 for score in scores)}


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
    stats = team_stats(team)
    roles = role_counts(team)
    impact = team_impact_counts(team)
    averages = team_skill_averages(team)
    selected_tag = '<span class="prism-selected-tag">PLAYERS SHOWN</span>' if selected else ''
    selected_class = " is-selected" if selected else ""
    st.markdown(
        f'''<div class="prism-team-card{selected_class}">
          <div class="prism-team-summary-head"><div>
            <div class="prism-team-title">{html.escape(team_name)}</div>
            <div class="prism-team-score">{float(stats['strength']):.2f}</div>
            <div class="prism-team-small">TEAM STRENGTH · {len(team)} PLAYERS</div>
          </div>{selected_tag}</div>
          <div style="margin-top:.55rem"><span class="prism-stat-pill"><b>{impact['elite']}</b> Elite</span>
            <span class="prism-stat-pill"><b>{impact['strong']}</b> Strong</span></div>
          <div style="margin-top:.25rem"><span class="prism-stat-pill"><b>{roles['batters']}</b> Batters</span>
            <span class="prism-stat-pill"><b>{roles['bowlers']}</b> Bowlers</span>
            <span class="prism-stat-pill"><b>{roles['all_rounders']}</b> All-rounders</span>
            <span class="prism-stat-pill"><b>{roles['field_players']}</b> Fielders</span></div>
          <div class="prism-bar-row"><div class="prism-bar-label">Batting</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(10.0,averages['batting'])) * 10:.1f}%"></div></div><div class="prism-bar-value">{averages['batting']:.2f}</div></div>
          <div class="prism-bar-row"><div class="prism-bar-label">Bowling</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(10.0,averages['bowling'])) * 10:.1f}%"></div></div><div class="prism-bar-value">{averages['bowling']:.2f}</div></div>
          <div class="prism-bar-row"><div class="prism-bar-label">Fielding</div><div class="prism-bar-track"><div class="prism-bar-fill" style="width:{max(0.0,min(10.0,averages['fielding'])) * 10:.1f}%"></div></div><div class="prism-bar-value">{averages['fielding']:.2f}</div></div>
        </div>''',
        unsafe_allow_html=True,
    )


def render_player_card(player, rank_lookup, shared_names=None):
    name = html.escape(str(player["name"]))
    role = html.escape(player_role(player))
    rank = rank_lookup.get(player["name"], "—")
    score = player_score(player)
    shared_names = shared_names or set()
    is_shared = player["name"] in shared_names
    shared_tag = '<span class="prism-shared-tag">SHARED</span>' if is_shared else ''
    st.markdown(
        f'''<div class="prism-player-card{' shared' if is_shared else ''}">
          <div class="prism-player-card-top">
            <div class="prism-player-card-name"><span class="prism-player-card-rank">#{rank}</span>&nbsp; {name}{shared_tag}</div>
            <div class="prism-player-card-rank">{score:.2f}</div>
          </div>
          <div class="prism-player-card-skills">
            <span>BAT <b>{float(player['batting']):.2f}</b></span>
            <span>BOWL <b>{float(player['bowling']):.2f}</b></span>
            <span>FIELD <b>{float(player['fielding']):.2f}</b></span>
          </div>
          <div class="prism-player-card-footer"><span class="prism-role">{role}</span></div>
        </div>''',
        unsafe_allow_html=True,
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
    st.session_state.match1_search = ""


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
    st.session_state.match1_search = ""


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


@st.dialog("Reset the session?")
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
    sync_selection_widget_state(ranked_master)

    st.markdown("## Select Players")
    search_text = st.text_input(
        "Search players", placeholder="Search by player name", key="match1_search",
        label_visibility="collapsed", on_change=None,
    )

    filtered_players = [p for p in ranked_master if p["name"].casefold().startswith(search_text.strip().casefold())]

    # Durable selected-name state is separate from visible checkbox widgets.
    # This prevents Streamlit from losing selections when search hides rows.
    selected_names = set(st.session_state.get("selected_player_names", set()))
    selected_players = [p for p in ranked_master if p["name"] in selected_names]
    generate_label = "Generate teams" if session.match_number == 0 else f"Generate Match {session.match_number + 1}"

    # Keep the selection count and primary action together inside one card,
    # positioned before the ranked player list for easy access.
    with st.container(key="selection-action-card"):
        action_count_col, action_button_col = st.columns([1, 1.65], vertical_alignment="center")
        with action_count_col:
            st.markdown(
                f'''<div class="prism-selection-card"><div><div class="prism-selection-label">Selected players</div>
                <div class="prism-selection-count">{len(selected_players)}</div>
                <div class="prism-selection-hint">Minimum 2 players</div></div></div>''',
                unsafe_allow_html=True,
            )
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

    # Individual player rows: the details area is also a click target.
    for player in filtered_players:
        name = player["name"]
        rank = rank_lookup[name]
        key = selection_key(name)
        with st.container(key=f"player-selection-row-{rank}"):
            check_col, details_col, total_col = st.columns([0.42, 4.4, 0.78])
            with check_col:
                st.checkbox(
                    f"Select {name}", key=key, label_visibility="collapsed",
                    on_change=on_player_checkbox_change, args=(name,),
                )
            with details_col:
                role = html.escape(player_role(player))
                safe_name = html.escape(str(name))
                st.markdown(
                    f'''<div class="prism-player-name"><span class="prism-rank">#{rank}</span>&nbsp; {safe_name}</div>
                    <div class="prism-player-meta"><span class="prism-role">{role}</span>
                    &nbsp; BAT <b>{float(player['batting']):.2f}</b>
                    &nbsp; BOWL <b>{float(player['bowling']):.2f}</b>
                    &nbsp; FIELD <b>{float(player['fielding']):.2f}</b></div>''',
                    unsafe_allow_html=True,
                )
                st.button(
                    "Toggle player selection", key=f"toggle_player_{rank}",
                    use_container_width=True,
                    on_click=toggle_player_from_row, args=(name,),
                )
            with total_col:
                st.markdown(f'<div class="prism-total">{player_score(player):.2f}</div><div class="prism-skill-label">Strength</div>', unsafe_allow_html=True)



# ============================================================
# GENERATED MATCH — TEAM CARDS AND PLAYER DETAILS ONLY
# ============================================================

if session.current_teams and not st.session_state.get("edit_players_mode", False):
    result = session.current_teams
    team_a = result["team_a"]
    team_b = result["team_b"]

    ranked_master = ranked_players(master_players)
    rank_lookup = {player["name"]: rank for rank, player in enumerate(ranked_master, start=1)}

    # Responsive team summary cards: side-by-side on desktop and mobile.
    if "mobile_team_view" not in st.session_state:
        st.session_state.mobile_team_view = "A"
    shared_names = {p["name"] for p in team_a} & {p["name"] for p in team_b}
    summary_a, summary_b = st.columns(2, gap="medium")
    with summary_a:
        with st.container(key="team-card-a"):
            render_team_summary("Team A", team_a, selected=st.session_state.mobile_team_view == "A")
            with st.container(key="team-a-card-select"):
                st.button("Select Team A", key="select_team_a_card", use_container_width=True,
                          on_click=lambda: st.session_state.update({"mobile_team_view": "A"}))
    with summary_b:
        with st.container(key="team-card-b"):
            render_team_summary("Team B", team_b, selected=st.session_state.mobile_team_view == "B")
            with st.container(key="team-b-card-select"):
                st.button("Select Team B", key="select_team_b_card", use_container_width=True,
                          on_click=lambda: st.session_state.update({"mobile_team_view": "B"}))

    ordered_a = sorted(team_a, key=lambda p: (p["name"] not in shared_names, -player_score(p), p["name"].casefold()))
    ordered_b = sorted(team_b, key=lambda p: (p["name"] not in shared_names, -player_score(p), p["name"].casefold()))
    desktop_a, desktop_b = st.columns(2, gap="medium")
    with desktop_a:
        with st.container(key="team-a-desktop"):
            for player in ordered_a:
                render_player_card(player, rank_lookup, shared_names)
    with desktop_b:
        with st.container(key="team-b-desktop"):
            for player in ordered_b:
                render_player_card(player, rank_lookup, shared_names)

    with st.container(key="mobile-team-list"):
        mobile_team = ordered_a if st.session_state.mobile_team_view == "A" else ordered_b
        for player in mobile_team:
            render_player_card(player, rank_lookup, shared_names)

    # Controls stay at the bottom of the team view.
    action_edit, action_reset = st.columns(2, gap="medium")
    with action_edit:
        if st.button("Edit players", use_container_width=True, key="edit_players_from_team_view"):
            set_selection([p["name"] for p in session.players], ranked_master)
            st.session_state.edit_players_mode = True
            st.session_state.pop("match1_search", None)
            st.rerun()
    with action_reset:
        if st.button("Reset session", use_container_width=True, key="reset_from_team_view"):
            reset_session_dialog()

# No sidebar controls and no standalone Manual Team Builder / Comparison UI.
