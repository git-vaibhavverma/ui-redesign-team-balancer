# ============================================================
# STREAMLIT FRONTEND — PRISM CRICKET TEAM BALANCER
# ============================================================
#
# Keep business logic in the backend wherever possible.
#
# Intended architecture:
#       Streamlit -> CricketSession -> Team Balancer
#
# This file redesigns the frontend only. It deliberately keeps
# the existing CricketSession and team_balancer calls in place.
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
# Palette matches .streamlit/config.toml:
# navy #0B1220 | slate #152238 | lime #B7F34A | off-white #F5F7FA
# Lime surfaces intentionally use dark text for readability.
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
        --prism-border: rgba(210, 224, 245, 0.13);
      }

      .stApp { background: var(--prism-bg); color: var(--prism-text); }
      [data-testid="stHeader"] { background: rgba(11,18,32,0.92); }
      [data-testid="stSidebar"] { background: var(--prism-panel); }
      .block-container { max-width: 1320px; padding-top: 1.7rem; padding-bottom: 6rem; }
      h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] { color: var(--prism-text); }
      h1 { letter-spacing: -0.035em; font-weight: 800; }
      h2, h3 { letter-spacing: -0.02em; }
      [data-testid="stCaptionContainer"] { color: var(--prism-muted); }

      div[data-testid="stTextInput"] input,
      div[data-testid="stSelectbox"] div[data-baseweb="select"],
      div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background: var(--prism-panel); border-color: var(--prism-border); border-radius: 12px;
      }
      div[data-testid="stTextInput"] input { color: var(--prism-text); }
      div[data-testid="stCheckbox"] label { gap: 0.45rem; }
      div[data-testid="stCheckbox"] label p { font-weight: 600; }

      .prism-eyebrow {
        color: var(--prism-lime); text-transform: uppercase; letter-spacing: .16em;
        font-size: .72rem; font-weight: 800; margin-bottom: .35rem;
      }
      .prism-subtitle { color: var(--prism-muted); font-size: .96rem; margin-top: -.4rem; }
      .prism-panel {
        background: linear-gradient(145deg, #152238 0%, #101B2D 100%);
        border: 1px solid var(--prism-border); border-radius: 18px;
        padding: 1rem 1.05rem; margin-bottom: .65rem;
      }
      .prism-player-name { font-size: 1rem; font-weight: 750; line-height: 1.25; }
      .prism-player-meta { color: var(--prism-muted); font-size: .79rem; margin-top: .32rem; }
      .prism-rank {
        color: var(--prism-lime); font-size: .78rem; font-weight: 800;
        background: rgba(183,243,74,.10); border: 1px solid rgba(183,243,74,.24);
        border-radius: 8px; padding: .28rem .45rem; display: inline-block;
      }
      .prism-role {
        color: #D8E1EF; border: 1px solid var(--prism-border); border-radius: 999px;
        padding: .15rem .48rem; font-size: .70rem; font-weight: 750; display: inline-block;
      }
      .prism-total { color: var(--prism-lime); font-weight: 800; font-size: 1.02rem; }
      .prism-skill-label { color: var(--prism-muted); font-size: .72rem; }
      .prism-skill-value { color: var(--prism-text); font-size: .8rem; font-weight: 700; }

      .prism-team-card {
        background: linear-gradient(145deg, #192A40 0%, #111D30 100%);
        border: 1px solid var(--prism-border); border-radius: 18px;
        padding: 1.05rem 1.1rem .9rem 1.1rem; min-height: 205px;
      }
      .prism-team-title { font-size: 1.02rem; font-weight: 800; margin-bottom: .15rem; }
      .prism-team-score { color: var(--prism-lime); font-size: 1.8rem; font-weight: 850; letter-spacing: -.04em; }
      .prism-team-small { color: var(--prism-muted); font-size: .78rem; }
      .prism-stat-pill {
        display: inline-block; margin: .2rem .22rem .05rem 0; padding: .27rem .48rem;
        border: 1px solid var(--prism-border); border-radius: 9px; font-size: .75rem;
        color: var(--prism-text); background: rgba(255,255,255,.025);
      }
      .prism-stat-pill b { color: var(--prism-lime); }
      .prism-bar-row { display: grid; grid-template-columns: 62px 1fr 38px; gap: 8px; align-items: center; margin-top: .55rem; }
      .prism-bar-label { color: var(--prism-muted); font-size: .76rem; }
      .prism-bar-track { height: 7px; background: #2A3B52; border-radius: 99px; overflow: hidden; }
      .prism-bar-fill { height: 100%; background: var(--prism-lime); border-radius: 99px; }
      .prism-bar-value { font-size: .76rem; font-weight: 750; text-align: right; }
      .prism-list-heading { color: var(--prism-muted); font-size: .74rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 800; }
      .prism-player-card {
        border: 1px solid var(--prism-border); border-radius: 13px; padding: .72rem .8rem;
        margin-bottom: .48rem; background: rgba(21,34,56,.55);
      }
      .prism-player-card.shared { border-color: rgba(183,243,74,.48); }
      .prism-player-card-top { display:flex; justify-content:space-between; gap:.5rem; align-items:center; }
      .prism-player-card-name { font-size:.9rem; font-weight:750; }
      .prism-player-card-rank { color:var(--prism-lime); font-size:.72rem; font-weight:800; white-space:nowrap; }
      .prism-player-card-skills { display:flex; flex-wrap:wrap; gap:.28rem .65rem; color:var(--prism-muted); font-size:.73rem; margin-top:.45rem; }
      .prism-player-card-skills b { color:var(--prism-text); font-weight:700; }
      .prism-player-card-footer { display:flex; justify-content:space-between; gap:.5rem; align-items:center; margin-top:.45rem; }
      .prism-shared-note { border-left: 3px solid var(--prism-lime); padding:.65rem .85rem; background:rgba(183,243,74,.07); border-radius:0 10px 10px 0; margin:.7rem 0 1rem; }
      .prism-muted { color:var(--prism-muted); }

      div.stButton > button[kind="primary"] {
        background: var(--prism-lime); color: #101827; border: 1px solid var(--prism-lime);
        border-radius: 12px; font-weight: 850; min-height: 2.8rem;
      }
      div.stButton > button[kind="primary"]:hover { background: #C9FF70; color:#101827; border-color:#C9FF70; }
      div.stButton > button:not([kind="primary"]) {
        border-radius: 11px; border-color: var(--prism-border); min-height: 2.55rem;
      }
      [data-testid="stMetric"] { background:var(--prism-panel); border:1px solid var(--prism-border); border-radius:13px; padding:.7rem .85rem; }
      [data-testid="stMetricValue"] { color:var(--prism-lime); }
      hr { border-color: var(--prism-border); }

      /* Player-selection rows are intentionally compact. */
      [class*="st-key-player-selection-row-"] { border-bottom: 1px solid var(--prism-border); padding: .18rem 0 .48rem; }
      .st-key-team-a-desktop, .st-key-team-b-desktop { display:block; }
      .st-key-mobile-team-picker, .st-key-mobile-team-list, .st-key-view_team_a, .st-key-view_team_b { display:none; }

      @media (max-width: 760px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.35rem !important; }
        .prism-team-card { min-height: 0; padding: .85rem; }
        .prism-team-score { font-size: 1.55rem; }
        .st-key-team-a-desktop, .st-key-team-b-desktop { display:none; }
        .st-key-mobile-team-picker, .st-key-mobile-team-list, .st-key-view_team_a, .st-key-view_team_b { display:block; }
        div[data-testid="stHorizontalBlock"] { gap: .55rem; }
        div[data-testid="stMetric"] { padding: .55rem; }
        [data-testid="stMetricLabel"] { font-size: .75rem; }
        [data-testid="stMetricValue"] { font-size: 1.2rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SERVICES
# ============================================================

@st.cache_resource
def get_player_service():
    return PlayerService("players.csv")


@st.cache_data
def get_master_players():
    return get_player_service().load_master_players()


master_players = get_master_players()


# ============================================================
# APPLICATION SESSION
# ============================================================
# CricketSession remains the source of truth for match state.
# ============================================================

if "cricket_session" not in st.session_state:
    st.session_state.cricket_session = CricketSession()

session = st.session_state.cricket_session


# ============================================================
# PRESENTATION HELPERS
# ============================================================

def player_role(player):
    """Return the display role without changing player data."""
    is_batsman = bool(player.get("is_batsman", False))
    is_bowler = bool(player.get("is_bowler", False))
    if is_batsman and is_bowler:
        return "ALL-ROUNDER"
    if is_batsman:
        return "BATTER"
    if is_bowler:
        return "BOWLER"
    return "FIELD"


def player_score(player):
    """Use the existing backend's weighted individual-strength score."""
    return float(player_strength(player))


def ranked_players(players):
    """Return a presentation-only ranking; no balancing logic is changed."""
    return sorted(players, key=lambda p: (-player_score(p), p["name"].casefold()))


def assignment_from_teams(team_result):
    """Convert team lists to player -> A / B / SHARED assignments."""
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
    """Explain match-to-match changes; shared-player transitions aren't movements."""
    if not previous:
        return

    previous_assignment = assignment_from_teams(previous)
    current_assignment = assignment_from_teams(current)
    previous_players = set(previous_assignment)
    current_players = set(current_assignment)
    new_players = current_players - previous_players
    removed_players = previous_players - current_players

    moved_players = []
    became_shared = []
    no_longer_shared = []
    for name in previous_players & current_players:
        old = previous_assignment[name]
        new = current_assignment[name]
        if old in ("A", "B") and new in ("A", "B") and old != new:
            moved_players.append((name, old, new))
        if old in ("A", "B") and new == "SHARED":
            became_shared.append(name)
        if old == "SHARED" and new in ("A", "B"):
            no_longer_shared.append((name, new))

    st.markdown("### Changes from previous match")
    changes_exist = bool(new_players or removed_players or moved_players or became_shared or no_longer_shared)
    if not changes_exist:
        st.caption("No player changes.")
        return
    if new_players:
        st.markdown("🟢 **Joined:** " + ", ".join(sorted(new_players)))
    if removed_players:
        st.markdown("🔴 **Left:** " + ", ".join(sorted(removed_players)))
    for name, old, new in sorted(moved_players):
        st.markdown(f"🔄 **{name}** · Team {old} → Team {new}")
    if became_shared:
        st.markdown("🤝 **Now shared:** " + ", ".join(sorted(became_shared)))
    for name, team in sorted(no_longer_shared):
        st.markdown(f"↔️ **{name}** · Shared → Team {team}")


def order_team_for_display(team, shared_player=None):
    """Shared player first, then individual strength descending; display-only."""
    shared_name = shared_player["name"] if shared_player else None
    shared = [p for p in team if shared_name and p["name"] == shared_name]
    normal = [p for p in team if not (shared_name and p["name"] == shared_name)]
    normal.sort(key=player_score, reverse=True)
    return shared + normal


def role_counts(team):
    """Count role categories; a dual-role player is an all-rounder."""
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
    """Average raw skill ratings for 0–10 visual progress bars."""
    if not team:
        return {"batting": 0.0, "bowling": 0.0, "fielding": 0.0}
    return {
        skill: sum(float(p[skill]) for p in team) / len(team)
        for skill in ("batting", "bowling", "fielding")
    }


def team_impact_counts(team):
    """Elite >= 9; Strong >= 8 and < 9, using existing individual strength score."""
    scores = [player_score(player) for player in team]
    return {
        "elite": sum(score >= 9 for score in scores),
        "strong": sum(8 <= score < 9 for score in scores),
    }


def render_skill_bar(label, value):
    value = max(0.0, min(10.0, float(value)))
    width = value * 10
    safe_label = html.escape(label)
    st.markdown(
        f"""<div class="prism-bar-row">
          <div class="prism-bar-label">{safe_label}</div>
          <div class="prism-bar-track"><div class="prism-bar-fill" style="width:{width:.1f}%"></div></div>
          <div class="prism-bar-value">{value:.2f}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_team_summary(team_name, team):
    """Render the visual summary card while retaining team_stats as source of team strength."""
    stats = team_stats(team)
    roles = role_counts(team)
    impact = team_impact_counts(team)
    averages = team_skill_averages(team)
    accent = "A" if team_name == "Team A" else "B"
    st.markdown(
        f"""<div class="prism-team-card">
          <div class="prism-team-title">TEAM {accent}</div>
          <div class="prism-team-score">{float(stats['strength']):.2f}</div>
          <div class="prism-team-small">Team strength · {len(team)} players</div>
          <div style="margin-top:.65rem">
            <span class="prism-stat-pill"><b>{impact['elite']}</b> Elite</span>
            <span class="prism-stat-pill"><b>{impact['strong']}</b> Strong</span>
            <span class="prism-stat-pill"><b>{roles['batters']}</b> Batters</span>
            <span class="prism-stat-pill"><b>{roles['bowlers']}</b> Bowlers</span>
            <span class="prism-stat-pill"><b>{roles['all_rounders']}</b> All-rounders</span>
            <span class="prism-stat-pill"><b>{roles['field_players']}</b> Field</span>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )
    render_skill_bar("Batting", averages["batting"])
    render_skill_bar("Bowling", averages["bowling"])
    render_skill_bar("Fielding", averages["fielding"])


def render_player_card(player, rank_lookup, shared_name=None):
    """Render a compact player card with pool rank and individual ratings."""
    name = html.escape(str(player["name"]))
    role = html.escape(player_role(player))
    rank = rank_lookup.get(player["name"], "—")
    score = player_score(player)
    shared_class = " shared" if shared_name and player["name"] == shared_name else ""
    shared_tag = '<span class="prism-role">SHARED</span>' if shared_name and player["name"] == shared_name else ""
    st.markdown(
        f"""<div class="prism-player-card{shared_class}">
          <div class="prism-player-card-top">
            <div class="prism-player-card-name">{name} {shared_tag}</div>
            <div class="prism-player-card-rank">#{rank} · {score:.2f}</div>
          </div>
          <div class="prism-player-card-skills">
            <span>BAT <b>{float(player['batting']):.2f}</b></span>
            <span>BOWL <b>{float(player['bowling']):.2f}</b></span>
            <span>FIELD <b>{float(player['fielding']):.2f}</b></span>
          </div>
          <div class="prism-player-card-footer"><span class="prism-role">{role}</span><span class="prism-muted" style="font-size:.72rem">Individual strength</span></div>
        </div>""",
        unsafe_allow_html=True,
    )


def clear_match_one_selection():
    """Clear Match 1 widget state when starting a fresh session."""
    for player in master_players:
        st.session_state.pop(f"select_player_{player['name']}", None)
    st.session_state.pop("match1_search", None)
    st.session_state.pop("mobile_team_view", None)


# ============================================================
# APP HEADER
# ============================================================

st.markdown('<div class="prism-eyebrow">PRISM · SUNDAY CRICKET</div>', unsafe_allow_html=True)
st.title("Team Balancer")
st.markdown('<div class="prism-subtitle">Balanced teams. Minimal reshuffling. Ready for match day.</div>', unsafe_allow_html=True)


# ============================================================
# MATCH 1 — RANKED PLAYER SELECTION
# ============================================================
# Only the UI changes here. The selected full player records
# still flow through set_initial_players() and generate_match().
# ============================================================

if session.match_number == 0:
    st.markdown("## Select your squad")
    st.caption("Search by name, then select the players who are playing this session. Rankings use the existing weighted individual-strength score.")

    ranked_master = ranked_players(master_players)
    rank_lookup = {player["name"]: rank for rank, player in enumerate(ranked_master, start=1)}

    # Initialize stable checkbox state once per browser session.
    for player in ranked_master:
        checkbox_key = f"select_player_{player['name']}"
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False

    search_col, count_col = st.columns([4, 1])
    with search_col:
        search_text = st.text_input(
            "Search players",
            placeholder="Type a player name…",
            key="match1_search",
            label_visibility="collapsed",
        )
    selected_names = {
        player["name"] for player in ranked_master
        if st.session_state.get(f"select_player_{player['name']}", False)
    }
    with count_col:
        st.metric("Selected", len(selected_names))

    # Keep the list sorted by individual strength, regardless of search.
    filtered_players = [
        player for player in ranked_master
        if search_text.strip().casefold() in player["name"].casefold()
    ]

    # Compact header row; skill values are ratings, total is weighted score.
    st.markdown(
        '<div class="prism-panel"><div class="prism-list-heading">Rank · Player · Role · Batting · Bowling · Fielding · Total</div></div>',
        unsafe_allow_html=True,
    )

    if not filtered_players:
        st.info("No players match that name.")
    else:
        for player in filtered_players:
            name = player["name"]
            rank = rank_lookup[name]
            role = player_role(player)
            checkbox_key = f"select_player_{name}"
            with st.container(key=f"player-selection-row-{rank}"):
                row_check, row_rank, row_details, row_total = st.columns([0.55, 0.55, 4.3, 0.85])
                with row_check:
                    st.checkbox(
                        "Select " + name,
                        key=checkbox_key,
                        label_visibility="collapsed",
                    )
                with row_rank:
                    st.markdown(f'<span class="prism-rank">#{rank}</span>', unsafe_allow_html=True)
                with row_details:
                    st.markdown(
                        f'''<div class="prism-player-name">{html.escape(str(name))}</div>
                        <div class="prism-player-meta"><span class="prism-role">{html.escape(role)}</span>
                        &nbsp; BAT <b>{float(player['batting']):.2f}</b>
                        &nbsp; BOWL <b>{float(player['bowling']):.2f}</b>
                        &nbsp; FIELD <b>{float(player['fielding']):.2f}</b></div>''',
                        unsafe_allow_html=True,
                    )
                with row_total:
                    st.markdown(f'<div class="prism-total">{player_score(player):.2f}</div><div class="prism-skill-label">Strength</div>', unsafe_allow_html=True)

    # Re-read state after the checkboxes have rendered.
    selected_names = {
        player["name"] for player in ranked_master
        if st.session_state.get(f"select_player_{player['name']}", False)
    }
    selected_players = [player for player in ranked_master if player["name"] in selected_names]

    st.divider()
    generate_col, note_col = st.columns([1.25, 3.75])
    with generate_col:
        generate_disabled = len(selected_players) < 2
        if st.button("🏏 Generate teams", type="primary", disabled=generate_disabled, use_container_width=True, key="generate_match_one"):
            session.set_initial_players(selected_players)
            session.generate_match()
            st.session_state.pop("previous_match", None)
            st.session_state.pop("mobile_team_view", None)
            st.rerun()
    with note_col:
        if len(selected_players) < 2:
            st.caption("Select at least 2 players to generate teams.")
        else:
            st.caption(f"Ready to balance {len(selected_players)} players. The backend balancing rules are unchanged.")


# ============================================================
# SUBSEQUENT MATCHES — ADD / REMOVE / GENERATE / RESET
# ============================================================
# Keep the complete existing session workflow available.
# On desktop these controls remain in the sidebar; on narrow
# screens Streamlit's sidebar can be opened from the menu.
# ============================================================

else:
    st.sidebar.markdown("## 🏏 Match controls")
    st.sidebar.metric("Current players", len(session.players))
    st.sidebar.metric("Current match", session.match_number)

    st.sidebar.divider()
    st.sidebar.markdown("### Add player")
    participating_names = {player["name"] for player in session.players}
    available_players = [player for player in master_players if player["name"] not in participating_names]
    if available_players:
        available_names = [player["name"] for player in available_players]
        player_to_add = st.sidebar.selectbox("Choose a player", available_names, key="add_player_select")
        if st.sidebar.button("Add player", use_container_width=True, key="add_player_button"):
            player = next(player for player in available_players if player["name"] == player_to_add)
            session.add_player(player)
            st.rerun()
    else:
        st.sidebar.caption("All master players are already in the session.")

    st.sidebar.markdown("### Remove player")
    current_names = [player["name"] for player in session.players]
    if current_names:
        player_to_remove = st.sidebar.selectbox("Choose a player", current_names, key="remove_player_select")
        if st.sidebar.button("Remove player", use_container_width=True, key="remove_player_button"):
            session.remove_player(player_to_remove)
            st.rerun()

    st.sidebar.divider()
    if len(session.players) >= 2:
        if st.sidebar.button("🏏 Generate next match", type="primary", use_container_width=True, key="generate_next_match"):
            # Save the previous result for the existing match-change summary.
            previous = session.current_teams
            session.generate_match()
            st.session_state.previous_match = previous
            st.session_state.pop("mobile_team_view", None)
            st.rerun()
    else:
        st.sidebar.warning("At least 2 players are required.")

    st.sidebar.divider()
    if st.sidebar.button("↻ Reset / start new session", use_container_width=True, key="request_reset"):
        st.session_state.confirm_reset = True

    if st.session_state.get("confirm_reset", False):
        st.sidebar.warning("This clears the current session and returns to Match 1.")
        reset_yes, reset_no = st.sidebar.columns(2)
        with reset_yes:
            if st.button("Yes, reset", key="confirm_reset_button", use_container_width=True):
                st.session_state.cricket_session = CricketSession()
                st.session_state.pop("previous_match", None)
                st.session_state.pop("confirm_reset", None)
                clear_match_one_selection()
                st.rerun()
        with reset_no:
            if st.button("Cancel", key="cancel_reset_button", use_container_width=True):
                st.session_state.pop("confirm_reset", None)
                st.rerun()


# ============================================================
# GENERATED MATCH — TEAM SUMMARIES AND PLAYER LISTS
# ============================================================

if session.current_teams:
    result = session.current_teams
    team_a = result["team_a"]
    team_b = result["team_b"]
    shared_player = result.get("shared_player")
    shared_name = shared_player["name"] if shared_player else None

    # Use ranks from the entire master list, not ranks within each team.
    ranked_master = ranked_players(master_players)
    rank_lookup = {player["name"]: rank for rank, player in enumerate(ranked_master, start=1)}

    st.markdown("---")
    header_col, session_col = st.columns([3, 1])
    with header_col:
        st.markdown(f"## Match {session.match_number}")
        st.caption(f"{len(session.players)} players in this match · teams ordered by individual strength for display")
    with session_col:
        if st.button("↻ Reset session", key="main_reset_request", use_container_width=True):
            st.session_state.confirm_reset = True
            st.rerun()

    if shared_player:
        st.markdown(
            f'<div class="prism-shared-note">🤝 <b>Shared player:</b> {html.escape(str(shared_name))} <span class="prism-muted">· appears on both teams under the existing odd-player rule</span></div>',
            unsafe_allow_html=True,
        )

    # Summary cards. On mobile, the team-selection buttons below
    # control which list is displayed beneath the cards.
    summary_a, summary_b = st.columns(2)
    with summary_a:
        render_team_summary("Team A", team_a)
    with summary_b:
        render_team_summary("Team B", team_b)

    # Mobile-only picker; desktop still shows both teams side by side.
    with st.container(key="mobile-team-picker"):
        mobile_a, mobile_b = st.columns(2)
        with mobile_a:
            if st.button("View Team A", key="view_team_a", use_container_width=True):
                st.session_state.mobile_team_view = "A"
        with mobile_b:
            if st.button("View Team B", key="view_team_b", use_container_width=True):
                st.session_state.mobile_team_view = "B"

    if "mobile_team_view" not in st.session_state:
        st.session_state.mobile_team_view = "A"

    ordered_a = order_team_for_display(team_a, shared_player)
    ordered_b = order_team_for_display(team_b, shared_player)

    # Desktop: both lists side by side. CSS hides these two containers on mobile.
    list_a, list_b = st.columns(2)
    with list_a:
        with st.container(key="team-a-desktop"):
            st.markdown("### 🅰️ Team A players")
            st.caption(f"{len(team_a)} players")
            for player in ordered_a:
                render_player_card(player, rank_lookup, shared_name)
    with list_b:
        with st.container(key="team-b-desktop"):
            st.markdown("### 🅱️ Team B players")
            st.caption(f"{len(team_b)} players")
            for player in ordered_b:
                render_player_card(player, rank_lookup, shared_name)

    # Mobile: a single list below the team cards; selection changes this list.
    with st.container(key="mobile-team-list"):
        mobile_team_key = st.session_state.mobile_team_view
        mobile_team = ordered_a if mobile_team_key == "A" else ordered_b
        st.markdown(f"### {'🅰️ Team A' if mobile_team_key == 'A' else '🅱️ Team B'} players")
        st.caption(f"{len(mobile_team)} players · choose a team above to switch this list")
        for player in mobile_team:
            render_player_card(player, rank_lookup, shared_name)

    # Existing backend score outputs remain visible, unchanged.
    st.markdown("---")
    st.markdown("### Balance details")
    score1, score2, score3 = st.columns(3)
    with score1:
        st.metric("Balance score", f"{float(result['balance_score']):.2f}")
    with score2:
        st.metric("Reshuffle penalty", f"{float(result['reshuffle_score']):.2f}")
    with score3:
        st.metric("Total score", f"{float(result['score']):.2f}")

    previous = st.session_state.get("previous_match")
    if previous:
        st.markdown("---")
        display_changes(previous, result)

# No standalone Team Builder / Comparison UI is rendered here by design.
