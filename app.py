# ============================================================
# STREAMLIT FRONTEND
# ============================================================
#
# This file is currently our frontend.
#
# IMPORTANT:
#
# Keep business logic out of this file wherever possible.
#
# The intended architecture is:
#
#       Streamlit
#          ↓
#   CricketSession
#          ↓
#   Team Balancer
#
# Later, Streamlit could be replaced with:
#
#       React / Next.js / Mobile App
#               ↓
#              API
#               ↓
#        Same backend
#
# without rewriting the actual team-balancing logic.
# ============================================================
import streamlit as st

from backend.player_service import PlayerService
from backend.session_manager import CricketSession
from backend.team_balancer import team_stats, player_strength

from backend.team_builder import TeamBuilder

from backend.team_comparator import (
    compare_teams,
    order_players_by_strength,
)



# ============================================================
# PAGE CONFIGURATION
# ============================================================

# st.set_page_config(
#     page_title="Sunday Cricket Team Balancer",
#     page_icon="🏏",
#     layout="wide",
# )

st.set_page_config(
    page_title="Sunday Cricket Team Balancer",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------
# GLOBAL UI STYLING
# --------------------------------------------------------

st.markdown(
    """
    <style>

    /* --------------------------------------------------
       Main application layout
       -------------------------------------------------- */

    [data-testid="stAppViewContainer"] {
        background-color: #F5F7FA;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* --------------------------------------------------
       Sidebar
       -------------------------------------------------- */

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }


    /* --------------------------------------------------
       Main title
       -------------------------------------------------- */

    h1 {
        color: #0F172A;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    h2 {
        color: #0F172A;
        font-weight: 750;
    }

    h3 {
        color: #1E293B;
        font-weight: 700;
    }


    /* --------------------------------------------------
       Buttons
       -------------------------------------------------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        font-weight: 600;
        min-height: 42px;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #15803D;
        color: #15803D;
    }


    /* --------------------------------------------------
       Primary buttons
       -------------------------------------------------- */

    .stButton > button[kind="primary"] {
        background-color: #15803D;
        border-color: #15803D;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #166534;
        border-color: #166534;
        color: white;
    }


    /* --------------------------------------------------
       Metrics
       -------------------------------------------------- */

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #64748B;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #0F172A;
        font-weight: 750;
    }


    /* --------------------------------------------------
       Expanders
       -------------------------------------------------- */

    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-bottom: 10px;
    }


    /* --------------------------------------------------
       Info / warning / success messages
       -------------------------------------------------- */

    [data-testid="stAlert"] {
        border-radius: 10px;
    }


    /* --------------------------------------------------
       Select boxes / multiselects
       -------------------------------------------------- */

    [data-testid="stSelectbox"] > div,
    [data-testid="stMultiSelect"] > div {
        border-radius: 10px;
    }


    /* --------------------------------------------------
       Horizontal divider
       -------------------------------------------------- */

    hr {
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 1.5rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SERVICES
# ============================================================
#
# Streamlit reruns the script frequently.
#
# @st.cache_resource keeps the service object alive rather
# than creating it from scratch on every rerun.
# ============================================================

@st.cache_resource
def get_player_service():

    return PlayerService(
        "players.csv"
    )


# ------------------------------------------------------------
# Cache the master player list.
#
# The CSV doesn't normally change during a Sunday session,
# so there is no reason to reload it on every Streamlit
# interaction.
# ------------------------------------------------------------

@st.cache_data
def get_master_players():

    service = get_player_service()

    return service.load_master_players()


player_service = (
    get_player_service()
)

master_players = (
    get_master_players()
)


# ============================================================
# APPLICATION SESSION
# ============================================================
#
# Streamlit reruns app.py from top to bottom whenever the user
# interacts with the application.
#
# st.session_state allows our CricketSession object to survive
# those reruns.
# ============================================================

if "cricket_session" not in st.session_state:

    st.session_state.cricket_session = (
        CricketSession()
    )


session = (
    st.session_state.cricket_session
)


# ============================================================
# HELPER: CONVERT TEAMS TO ASSIGNMENTS
# ============================================================

def assignment_from_teams(team_result):
    """
    Convert a match result into:

        player -> A
        player -> B
        player -> SHARED

    This is mainly used by the UI to explain what changed
    between matches.
    """

    team_a_names = {
        p["name"]
        for p in team_result["team_a"]
    }

    team_b_names = {
        p["name"]
        for p in team_result["team_b"]
    }

    assignment = {}

    # A player appearing in both lists is shared.
    for name in (
        team_a_names
        & team_b_names
    ):

        assignment[name] = "SHARED"

    # Players appearing only in Team A.
    for name in (
        team_a_names
        - team_b_names
    ):

        assignment[name] = "A"

    # Players appearing only in Team B.
    for name in (
        team_b_names
        - team_a_names
    ):

        assignment[name] = "B"

    return assignment


# ============================================================
# HELPER: DISPLAY PLAYER
# ============================================================

def display_player(player):
    """
    Display one player's information.

    Ratings are displayed with exactly two decimal places.

    IMPORTANT:
    This is presentation formatting only.

    The actual backend continues using the underlying floating
    point values.
    """

    roles = []

    if player["is_batsman"]:
        roles.append("BAT")

    if player["is_bowler"]:
        roles.append("BOWL")

    # Players with neither role are treated as fielding-only.
    role_text = (
        " / ".join(roles)
        if roles
        else "FIELD"
    )

    st.write(
        f"**{player['name']}** "
        f"— Bat {player['batting']:.2f} | "
        f"Bowl {player['bowling']:.2f} | "
        f"Field {player['fielding']:.2f} "
        f"({role_text})"
    )


# ============================================================
# HELPER: DISPLAY TEAM STATISTICS
# ============================================================

def display_team_stats(team):
    """
    Display the calculated statistics for a team.
    """

    stats = team_stats(team)

    # --------------------------------------------------------
    # Main numerical statistics
    # --------------------------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "Batting",
            f"{stats['batting']:.2f}",
        )

    with col2:

        st.metric(
            "Bowling",
            f"{stats['bowling']:.2f}",
        )

    with col3:

        st.metric(
            "Fielding",
            f"{stats['fielding']:.2f}",
        )

    with col4:

        st.metric(
            "Strength",
            f"{stats['strength']:.2f}",
        )

    # --------------------------------------------------------
    # Role and impact information
    # --------------------------------------------------------

    st.markdown(
        f"""
        **Roles**

        🏏 Batters: **{stats['batsmen']}**  
        🎯 Bowlers: **{stats['bowlers']}**

        **Impact**

        🔥 Elite Batters: **{stats['elite_batters']}**  
        🔥 Elite Bowlers: **{stats['elite_bowlers']}**  
        ⭐ Strong Batters: **{stats['strong_batters']}**  
        ⭐ Strong Bowlers: **{stats['strong_bowlers']}**
        """
    )


# ============================================================
# HELPER: DISPLAY MATCH CHANGES
# ============================================================

def display_changes(previous, current):
    """
    Explain what changed between two consecutive matches.

    We deliberately distinguish:

        A -> B / B -> A
            = actual movement

        A -> SHARED
        B -> SHARED
        SHARED -> A
        SHARED -> B
            = not a movement

    This mirrors the reshuffle rules in the backend.
    """

    if not previous:
        return

    previous_assignment = (
        assignment_from_teams(
            previous
        )
    )

    current_assignment = (
        assignment_from_teams(
            current
        )
    )

    previous_players = set(
        previous_assignment
    )

    current_players = set(
        current_assignment
    )

    # --------------------------------------------------------
    # Players who joined
    # --------------------------------------------------------

    new_players = (
        current_players
        - previous_players
    )

    # --------------------------------------------------------
    # Players who left
    # --------------------------------------------------------

    removed_players = (
        previous_players
        - current_players
    )

    # --------------------------------------------------------
    # Actual A <-> B movements
    # --------------------------------------------------------
    #
    # Shared transitions are intentionally excluded.
    # --------------------------------------------------------

    moved_players = []

    for name in (
        previous_players
        & current_players
    ):

        old = previous_assignment[name]
        new = current_assignment[name]

        if (
            old in ("A", "B")
            and new in ("A", "B")
            and old != new
        ):

            moved_players.append(
                (name, old, new)
            )

    # --------------------------------------------------------
    # Players who became shared
    # --------------------------------------------------------

    became_shared = []

    for name in (
        previous_players
        & current_players
    ):

        old = previous_assignment[name]
        new = current_assignment[name]

        if (
            old in ("A", "B")
            and new == "SHARED"
        ):

            became_shared.append(
                name
            )

    # --------------------------------------------------------
    # Players who stopped being shared
    # --------------------------------------------------------

    no_longer_shared = []

    for name in (
        previous_players
        & current_players
    ):

        old = previous_assignment[name]
        new = current_assignment[name]

        if (
            old == "SHARED"
            and new in ("A", "B")
        ):

            no_longer_shared.append(
                (name, new)
            )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    st.subheader(
        "Changes from Previous Match"
    )

    if new_players:

        st.write(
            "🟢 **New players:** "
            + ", ".join(
                sorted(new_players)
            )
        )

    if removed_players:

        st.write(
            "🔴 **Players who left:** "
            + ", ".join(
                sorted(removed_players)
            )
        )

    if moved_players:

        for name, old, new in (
            moved_players
        ):

            st.write(
                f"🔄 **{name}**: "
                f"Team {old} → Team {new}"
            )

    if became_shared:

        st.write(
            "🤝 **Now shared:** "
            + ", ".join(
                sorted(became_shared)
            )
        )

    if no_longer_shared:

        for name, team in (
            no_longer_shared
        ):

            st.write(
                f"↔️ **{name}**: "
                f"Shared → Team {team}"
            )

    # --------------------------------------------------------
    # If nothing changed, make that explicit.
    # --------------------------------------------------------

    if not (
        new_players
        or removed_players
        or moved_players
        or became_shared
        or no_longer_shared
    ):

        st.write(
            "No player changes."
        )


# ============================================================
# HELPER: DISPLAY TEAMS IN ORDER (TOTAL STRENGTH)
# ============================================================

def order_team_for_display(team, shared_player=None):
    """
    Order players for presentation purposes only.

    Display order:
        1. Shared player, if applicable
        2. All other players by overall strength descending

    This does NOT affect the team-balancing algorithm.
    It only changes the order in which players are shown
    on the screen.
    """

    # --------------------------------------------------------
    # Separate the shared player from the normal players.
    #
    # We identify the shared player by name rather than object
    # identity because player records are dictionaries and may
    # have been copied during session processing.
    # --------------------------------------------------------

    shared = []
    normal_players = []

    shared_name = (
        shared_player["name"]
        if shared_player
        else None
    )

    for player in team:

        if (
            shared_name
            and player["name"] == shared_name
        ):
            shared.append(player)

        else:
            normal_players.append(player)

    # --------------------------------------------------------
    # Sort normal players by their weighted overall strength.
    #
    # Reverse=True means strongest player appears first.
    #
    # player_strength() already uses the configured weights:
    #
    #   Batting  = 35%
    #   Bowling  = 45%
    #   Fielding = 20%
    # --------------------------------------------------------

    normal_players.sort(
        key=player_strength,
        reverse=True,
    )

    # --------------------------------------------------------
    # Shared player always comes first.
    # --------------------------------------------------------

    return (
        shared
        + normal_players
    )


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title(
    "🏏 Sunday Cricket Team Balancer"
)

st.caption(
    "Select players for each match and generate balanced "
    "teams while minimizing unnecessary reshuffling."
)



# ============================================================
# MATCH 1 — PLAYER SELECTION
# ============================================================
#
# Match 1 is different from later matches.
#
# At this point we only know the master player pool.
# The user must tell us who is actually playing.
# ============================================================

if session.match_number == 0:

    st.header(
        "Select Players for Match 1"
    )

    st.info(
        "The master player list contains everyone who is "
        "available. Select only the players who are playing "
        "this Sunday session."
    )

    # Extract names for the multiselect widget.
    master_names = [
        p["name"]
        for p in master_players
    ]

    selected_names = st.multiselect(
        "Players playing Match 1",
        options=master_names,
    )

    # Convert the selected names back into full player records.
    selected_players = [
        p
        for p in master_players
        if p["name"]
        in selected_names
    ]

    st.write(
        f"Selected players: "
        f"**{len(selected_players)}**"
    )

    # At least two players are required to form teams.
    if len(selected_players) >= 2:

        if st.button(
            "🏏 Generate Match 1",
            type="primary",
        ):

            # Store the selected players in the session.
            session.set_initial_players(
                selected_players
            )

            # Generate the first team arrangement.
            session.generate_match()

            # Refresh the UI so Match 1 is displayed.
            st.rerun()

    else:

        st.warning(
            "Select at least 2 players."
        )


# ============================================================
# SUBSEQUENT MATCHES
# ============================================================
#
# From Match 2 onward, the current player pool is already known.
#
# The user can:
#
#   - Add someone from the master list.
#   - Remove someone currently playing.
#   - Generate the next match.
# ============================================================

else:

    st.sidebar.title(
        "🏏 Sunday Cricket"
    )

    st.sidebar.metric(
        "Current Players",
        len(session.players),
    )

    st.sidebar.metric(
        "Match",
        session.match_number,
    )

    # --------------------------------------------------------
    # RESET SESSION
    # --------------------------------------------------------
    #
    # Resetting clears the current cricket match session and
    # returns the app to Match 1.
    #
    # A confirmation step is used to prevent accidentally
    # resetting an active match.
    # --------------------------------------------------------

    st.sidebar.divider()

    if st.sidebar.button(
        "🔄 Reset / Start New Session",
        help="Clear the current matches and start again from Match 1.",
    ):

        # Don't reset immediately.
        # Instead, ask the user for confirmation.

        st.session_state.confirm_reset = True


    # --------------------------------------------------------
    # RESET CONFIRMATION
    # --------------------------------------------------------

    if st.session_state.get(
        "confirm_reset",
        False,
    ):

        st.sidebar.warning(
            "⚠️ Are you sure? This will clear the "
            "current match session and return to Match 1."
        )

        confirm_col1, confirm_col2 = (
            st.sidebar.columns(2)
        )

        with confirm_col1:

            if st.button(
                "Yes, Reset",
                key="confirm_reset_button",
            ):

                # Remove the current cricket session.
                del st.session_state.cricket_session

                # Remove previous-match information.
                st.session_state.pop(
                    "previous_match",
                    None,
                )

                # Remove the confirmation flag.
                st.session_state.pop(
                    "confirm_reset",
                    None,
                )

                # Create a fresh CricketSession immediately.
                st.session_state.cricket_session = (
                    CricketSession()
                )

                st.rerun()


        with confirm_col2:

            if st.button(
                "Cancel",
                key="cancel_reset_button",
            ):

                st.session_state.pop(
                    "confirm_reset",
                    None,
                )

                st.rerun()

    # ========================================================
    # ADD PLAYER
    # ========================================================

    st.sidebar.subheader(
        "Add Player"
    )

    # Names of people already participating.
    participating_names = {
        p["name"]
        for p in session.players
    }

    # Only master players who aren't currently playing
    # can be selected.
    available_players = [
        p
        for p in master_players
        if p["name"]
        not in participating_names
    ]

    if available_players:

        available_names = [
            p["name"]
            for p in available_players
        ]

        player_to_add = (
            st.sidebar.selectbox(
                "Select player",
                available_names,
            )
        )

        if st.sidebar.button(
            "Add Player"
        ):

            # Find the complete player record.
            player = next(
                p
                for p in available_players
                if p["name"]
                == player_to_add
            )

            # Session manager handles validation and addition.
            session.add_player(
                player
            )

            st.rerun()

    else:

        st.sidebar.caption(
            "No additional master players available."
        )

    # ========================================================
    # REMOVE PLAYER
    # ========================================================

    st.sidebar.subheader(
        "Remove Player"
    )

    current_names = [
        p["name"]
        for p in session.players
    ]

    if current_names:

        player_to_remove = (
            st.sidebar.selectbox(
                "Select player to remove",
                current_names,
            )
        )

        if st.sidebar.button(
            "Remove Player"
        ):

            session.remove_player(
                player_to_remove
            )

            st.rerun()

    # ========================================================
    # GENERATE NEXT MATCH
    # ========================================================

    st.sidebar.divider()

    if len(session.players) >= 2:

        if st.sidebar.button(
            "🏏 Generate Next Match",
            type="primary",
        ):

            # Save the previous result so the UI can explain
            # what changed after the new match is generated.
            previous = (
                session.current_teams
            )

            session.generate_match()

            st.session_state.previous_match = (
                previous
            )

            st.rerun()

    else:

        st.sidebar.warning(
            "At least 2 players are required."
        )


# ============================================================
# CURRENT MATCH DISPLAY
# ============================================================
#
# Everything below this point is presentation.
#
# The actual team selection has already been performed by
# CricketSession -> team_balancer.
# ============================================================

if session.current_teams:

    result = (
        session.current_teams
    )

    st.header(
        f"Match {session.match_number}"
    )

    # --------------------------------------------------------
    # Shared player
    # --------------------------------------------------------

    if result["shared_player"]:

        st.info(
            "🤝 Shared player: "
            f"**{result['shared_player']['name']}**"
        )

    # --------------------------------------------------------
    # Two team columns
    # --------------------------------------------------------

    col_a, col_b = (
        st.columns(2)
    )

    # ========================================================
    # TEAM A
    # ========================================================

    with col_a:

        st.subheader(
            "🅰️ Team A"
        )

        team_a_display = order_team_for_display(
            result["team_a"],
            result["shared_player"],
        )

        for player in team_a_display:

            display_player(
                player
            )

        st.divider()

        display_team_stats(
            result["team_a"]
        )

    # ========================================================
    # TEAM B
    # ========================================================

    with col_b:

        st.subheader(
            "🅱️ Team B"
        )

        team_b_display = order_team_for_display(
            result["team_b"],
            result["shared_player"],
        )

        for player in team_b_display:

            display_player(
                player
            )

        st.divider()

        display_team_stats(
            result["team_b"]
        )

    # ========================================================
    # BALANCE SUMMARY
    # ========================================================

    st.divider()

    st.subheader(
        "Balance Summary"
    )

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "Balance Score",
            f"{result['balance_score']:.2f}",
        )

    with col2:

        st.metric(
            "Reshuffle Penalty",
            f"{result['reshuffle_score']:.2f}",
        )

    with col3:

        st.metric(
            "Total Score",
            f"{result['score']:.2f}",
        )

    # ========================================================
    # CHANGES FROM PREVIOUS MATCH
    # ========================================================

    previous = (
        st.session_state.get(
            "previous_match"
        )
    )

    if previous:

        st.divider()

        display_changes(
            previous,
            result,
        )


# ============================================================
# MANUAL TEAM BUILDER & TEAM COMPARISON
# ============================================================
#
# This section is independent from the Sunday Match Balancer
# above.
#
# The Sunday Match Balancer automatically calculates an optimal
# 2-team split.
#
# This section allows the user to MANUALLY create any number
# of teams and choose which players belong to each team.
#
# IMPORTANT:
#
# The total number of players assigned to teams does NOT have
# to equal the number of players in the master CSV.
#
# Example with 34 players:
#
#     Team A = 7
#     Team B = 7
#
#     Remaining = 20
#
# This is completely valid.
# ============================================================


st.divider()

st.header("Team Builder & Comparison")

st.write(
    """
    Manually create teams from the master player pool and
    compare their skill and player composition.

    Players do not have to be assigned to a team.
    Any unused players remain available in the pool.
    """
)


# ============================================================
# INITIALIZE TEAM BUILDER
# ============================================================
#
# Streamlit reruns the entire app whenever the user interacts
# with a widget.
#
# Therefore, the TeamBuilder object must live inside
# st.session_state so that our manually created teams are
# preserved between reruns.
# ============================================================

if "team_builder" not in st.session_state:

    st.session_state.team_builder = TeamBuilder(
        get_master_players()
    )


team_builder = st.session_state.team_builder


# ============================================================
# CREATE A NEW TEAM
# ============================================================

st.subheader("Create Teams")


create_team_col1, create_team_col2 = st.columns(
    [3, 1]
)


with create_team_col1:

    new_team_name = st.text_input(
        "Team name",
        placeholder="Example: Team A",
        key="manual_team_name",
    )


with create_team_col2:

    # Add some vertical spacing so the button lines up
    # reasonably with the text input.

    st.write("")
    st.write("")

    if st.button(
        "Add Team",
        key="add_manual_team",
    ):

        try:

            team_builder.add_team(
                new_team_name
            )

            st.success(
                f"Team '{new_team_name}' created."
            )

            # Rerun so that the newly created team immediately
            # appears in the UI.

            st.rerun()

        except ValueError as error:

            st.error(str(error))


# ============================================================
# PLAYER ASSIGNMENT
# ============================================================
#
# Players that are already assigned to a team are removed
# from the available-player selector.
#
# Therefore a player can only belong to one manually created
# team at a time.
# ============================================================

if team_builder.teams:

    st.subheader("Assign Players")


    # Get the players who have not yet been assigned.

    available_players = (
        team_builder.get_available_players()
    )

    available_player_names = [
        player["name"]
        for player in available_players
    ]


    assignment_col1, assignment_col2 = st.columns(2)


    with assignment_col1:

        # The user first selects which team they want to
        # populate.

        selected_team = st.selectbox(
            "Select team",
            options=list(
                team_builder.teams.keys()
            ),
            key="manual_selected_team",
        )


    with assignment_col2:

        # Only unassigned players appear here.

        selected_players = st.multiselect(
            "Select players",
            options=available_player_names,
            key="manual_selected_players",
        )


    if st.button(
        "Add Selected Players to Team",
        key="assign_players_to_manual_team",
    ):

        if not selected_players:

            st.warning(
                "Please select at least one player."
            )

        else:

            try:

                # Add every selected player to the chosen
                # team.

                for player_name in selected_players:

                    team_builder.add_player_to_team(
                        player_name,
                        selected_team,
                    )

                st.success(
                    f"{len(selected_players)} player(s) "
                    f"added to {selected_team}."
                )

                # Rerun so the available-player list gets
                # refreshed and those players disappear from it.

                st.rerun()

            except ValueError as error:

                st.error(str(error))


# ============================================================
# DISPLAY CURRENT TEAMS
# ============================================================
#
# Each manually created team is shown separately.
#
# Players inside a team are ordered by overall strength,
# highest first.
#
# This is only presentation ordering.
# ============================================================

if team_builder.teams:

    st.subheader("Current Teams")


    team_names = list(
        team_builder.teams.keys()
    )


    for team_name in team_names:

        team_players = (
            team_builder.get_team_players(
                team_name
            )
        )


        # Use an expander so that a large number of teams
        # does not make the page unnecessarily long.

        with st.expander(
            f"{team_name} — "
            f"{len(team_players)} players",
            expanded=True,
        ):

            if not team_players:

                st.info(
                    "No players assigned to this team yet."
                )

            else:

                # Sort strongest players first for display.

                ordered_players = (
                    order_players_by_strength(
                        team_players
                    )
                )


                for player in ordered_players:

                    player_col1, player_col2 = (
                        st.columns([5, 1])
                    )


                    with player_col1:

                        # Reuse your existing player display
                        # function so that player information
                        # looks consistent across the app.

                        display_player(player)


                    with player_col2:

                        if st.button(
                            "Remove",
                            key=(
                                "remove_manual_player_"
                                f"{team_name}_"
                                f"{player['name']}"
                            ),
                        ):

                            # Removing the player puts them
                            # back into the available pool.

                            team_builder.remove_player_from_team(
                                player["name"],
                                team_name,
                            )

                            st.rerun()


            # ------------------------------------------------
            # REMOVE ENTIRE TEAM
            # ------------------------------------------------
            #
            # Removing a team also releases all players in
            # that team back into the available pool.
            # ------------------------------------------------

            if st.button(
                f"Remove {team_name}",
                key=(
                    f"remove_manual_team_"
                    f"{team_name}"
                ),
            ):

                team_builder.remove_team(
                    team_name
                )

                st.rerun()


# ============================================================
# AVAILABLE PLAYER POOL
# ============================================================
#
# This shows everyone who has not yet been assigned.
#
# This is intentionally NOT an error when players remain here.
#
# For example:
#
#     34 total players
#     7 Team A
#     7 Team B
#     20 available
#
# is a perfectly valid state.
# ============================================================

st.subheader("Available Player Pool")


available_players = (
    team_builder.get_available_players()
)


st.write(
    f"**{len(available_players)} players "
    "remaining unassigned**"
)


if available_players:

    ordered_available_players = (
        order_players_by_strength(
            available_players
        )
    )


    for player in ordered_available_players:

        display_player(player)

else:

    st.info(
        "All players are currently assigned to teams."
    )


# ============================================================
# TEAM COMPARISON
# ============================================================
#
# Comparison becomes useful as soon as at least one team
# exists.
#
# An individual team can therefore be inspected even before
# the user has created Team B, Team C, etc.
#
# No ranking or automatic "winner" is produced here.
# We simply expose the statistics for the user to compare.
# ============================================================

if team_builder.teams:

    st.divider()

    st.header("Team Comparison")


    # Get all teams with their complete player objects.

    all_teams = team_builder.get_all_teams()


    # Calculate statistics for every team.

    team_comparisons = compare_teams(
        all_teams
    )


    # ========================================================
    # COMPARISON TABLE
    # ========================================================
    #
    # A compact table makes it easy to compare several teams
    # at the same time.
    # ========================================================

    comparison_rows = []


    for team_name in team_names:

        stats = team_comparisons[
            team_name
        ]


        comparison_rows.append(
            {
                "Team": team_name,

                "Players": stats[
                    "player_count"
                ],

                "Bat Avg": round(
                    stats["batting_average"],
                    2,
                ),

                "Bowl Avg": round(
                    stats["bowling_average"],
                    2,
                ),

                "Field Avg": round(
                    stats["fielding_average"],
                    2,
                ),

                "Overall Avg": round(
                    stats["strength_average"],
                    2,
                ),

                "Batsmen": stats[
                    "batsmen"
                ],

                "Bowlers": stats[
                    "bowlers"
                ],

                "Elite Bat": stats[
                    "elite_batters"
                ],

                "Elite Bowl": stats[
                    "elite_bowlers"
                ],

                "Strong Bat": stats[
                    "strong_batters"
                ],

                "Strong Bowl": stats[
                    "strong_bowlers"
                ],
            }
        )


    st.dataframe(
        comparison_rows,
        use_container_width=True,
        hide_index=True,
    )


    # ========================================================
    # DETAILED COMPARISON
    # ========================================================
    #
    # Show each team as its own column so the user can inspect
    # the composition and averages in more detail.
    # ========================================================

    st.subheader(
        "Detailed Team Comparison"
    )


    comparison_columns = st.columns(
        len(team_names)
    )


    for column, team_name in zip(
        comparison_columns,
        team_names,
    ):

        with column:

            st.markdown(
                f"### {team_name}"
            )


            stats = team_comparisons[
                team_name
            ]


            st.metric(
                "Players",
                stats["player_count"],
            )


            st.metric(
                "Batting Average",
                f"{stats['batting_average']:.2f}",
            )


            st.metric(
                "Bowling Average",
                f"{stats['bowling_average']:.2f}",
            )


            st.metric(
                "Fielding Average",
                f"{stats['fielding_average']:.2f}",
            )


            st.metric(
                "Overall Strength",
                f"{stats['strength_average']:.2f}",
            )


            st.write(
                f"**Batsmen:** "
                f"{stats['batsmen']}"
            )


            st.write(
                f"**Bowlers:** "
                f"{stats['bowlers']}"
            )


            st.write(
                f"**Elite Batters:** "
                f"{stats['elite_batters']}"
            )


            st.write(
                f"**Elite Bowlers:** "
                f"{stats['elite_bowlers']}"
            )


            st.write(
                f"**Strong Batters:** "
                f"{stats['strong_batters']}"
            )


            st.write(
                f"**Strong Bowlers:** "
                f"{stats['strong_bowlers']}"
            )