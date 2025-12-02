import os
from pathlib import Path
from typing import List

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from .state import PlayerStatus

ESPN_INJURIES_URL = "https://www.espn.in/nba/injuries"

# Where to store structured data
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "nba_injuries.csv"

llm = ChatOpenAI(model="gpt-5", temperature=0)  


def fetch_espn_injuries_raw() -> pd.DataFrame:
    """
    Fetch NBA injury tables from ESPN and return a single DataFrame
    with an extra TEAM column filled correctly.
    """
    tables = pd.read_html(ESPN_INJURIES_URL)
    if not tables:
        raise RuntimeError("No tables found on ESPN injuries page")

    frames = []
    for team_name, df in zip(NBA_TEAMS, tables):
        df = df.copy()
        # Add TEAM column so we can store it later
        df["TEAM"] = team_name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    return combined



def df_to_player_statuses(df: pd.DataFrame) -> List[PlayerStatus]:
    """
    Convert the ESPN injury DataFrame into a list of PlayerStatus objects.
    """
    required_cols = {"NAME", "STATUS"}
    if not required_cols.issubset(set(df.columns)):
        raise ValueError(f"DataFrame missing required columns: {required_cols}")

    player_statuses: List[PlayerStatus] = []

    for _, row in df.iterrows():
        name = row.get("NAME")
        status = row.get("STATUS")
        if pd.isna(name) or pd.isna(status):
            continue

        # TEAM column is added in fetch_espn_injuries_raw; use it when present
        team_raw = row.get("TEAM") if "TEAM" in df.columns else None
        team = None if team_raw is None or pd.isna(team_raw) else str(team_raw)

        expected_return = row.get("EST. RETURN DATE") if "EST. RETURN DATE" in df.columns else None
        comment = row.get("COMMENT") if "COMMENT" in df.columns else None

        player_statuses.append(
            PlayerStatus(
                team=team,
                player_name=str(name),
                status=str(status),
                reason=str(comment) if comment is not None and not pd.isna(comment) else None,
                expected_return=str(expected_return)
                if expected_return is not None and not pd.isna(expected_return)
                else None,
            )
        )

    return player_statuses


def save_player_statuses_to_csv(players: List[PlayerStatus]) -> None:
    """
    Save a list, PlayerStatus to csv.
    """
    if not players:
        return

    df = pd.DataFrame([p.model_dump() for p in players])
    df.to_csv(CSV_PATH, index=False)


def load_player_statuses_from_csv() -> List[PlayerStatus]:
    """
    Load PlayerStatus objects back from csv.
    """
    if not CSV_PATH.exists():
        return []

    df = pd.read_csv(CSV_PATH)
    players: List[PlayerStatus] = []
    for _, row in df.iterrows():
        team_val = row.get("team")
        reason_val = row.get("reason")
        exp_ret_val = row.get("expected_return")

        team = None if pd.isna(team_val) else str(team_val)
        reason = None if pd.isna(reason_val) else str(reason_val)
        expected_return = None if pd.isna(exp_ret_val) else str(exp_ret_val)

        players.append(
            PlayerStatus(
                team=team,
                player_name=str(row["player_name"]),
                status=str(row["status"]),
                reason=reason,
                expected_return=expected_return,
            )
        )
    return players


def fetch_and_store_injuries() -> List[PlayerStatus]:
    """
    High-level helper:
    1. Fetch ESPN injuries
    2. Convert to PlayerStatus list
    3. Save to CSV
    4. Return the list
    """
    df = fetch_espn_injuries_raw()
    players = df_to_player_statuses(df)
    # Enrich with inferred teams before persisting
    players = with_inferred_teams(players)
    save_player_statuses_to_csv(players)
    return players


def summarize_injuries_with_llm(players: List[PlayerStatus]) -> str:
    """
    Use GPT to generate a human-readable summary from PlayerStatus.
    """
    if not players:
        return "No injuries were found in the current dataset."

    # Build a compact bullet list for the LLM
    bullet_lines = []
    for p in players[:50]:  # cap to avoid huge prompt
        line = f"- {p.player_name}: {p.status}"
        if p.reason:
            line += f" ({p.reason})"
        bullet_lines.append(line)

    prompt = (
        "You are an assistant summarizing NBA injury reports for fans.\n"
        "Here is a list of players and their statuses:\n\n"
        + "\n".join(bullet_lines)
        + "\n\nWrite a short summary grouped by status (Out / Day-To-Day / others). "
        "Be concise and clear."
    )

    resp = llm.invoke(prompt)
    return resp.content


NBA_TEAMS = [
    "Atlanta Hawks",
    "Boston Celtics",
    "Brooklyn Nets",
    "Charlotte Hornets",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Dallas Mavericks",
    "Denver Nuggets",
    "Detroit Pistons",
    "Golden State Warriors",
    "Houston Rockets",
    "Indiana Pacers",
    "LA Clippers",
    "Los Angeles Lakers",
    "Memphis Grizzlies",
    "Miami Heat",
    "Milwaukee Bucks",
    "Minnesota Timberwolves",
    "New Orleans Pelicans",
    "New York Knicks",
    "Oklahoma City Thunder",
    "Orlando Magic",
    "Philadelphia 76ers",
    "Phoenix Suns",
    "Portland Trail Blazers",
    "Sacramento Kings",
    "San Antonio Spurs",
    "Toronto Raptors",
    "Utah Jazz",
    "Washington Wizards",
]

# --- Team inference helpers ---
TEAM_KEYWORDS = {
    "hawks": "Atlanta Hawks",
    "celtics": "Boston Celtics",
    "nets": "Brooklyn Nets",
    "hornets": "Charlotte Hornets",
    "bulls": "Chicago Bulls",
    "cavaliers": "Cleveland Cavaliers",
    "mavericks": "Dallas Mavericks",
    "nuggets": "Denver Nuggets",
    "pistons": "Detroit Pistons",
    "warriors": "Golden State Warriors",
    "rockets": "Houston Rockets",
    "pacers": "Indiana Pacers",
    "clippers": "LA Clippers",
    "lakers": "Los Angeles Lakers",
    "grizzlies": "Memphis Grizzlies",
    "heat": "Miami Heat",
    "bucks": "Milwaukee Bucks",
    "timberwolves": "Minnesota Timberwolves",
    "pelicans": "New Orleans Pelicans",
    "knicks": "New York Knicks",
    "thunder": "Oklahoma City Thunder",
    "magic": "Orlando Magic",
    "76ers": "Philadelphia 76ers",
    "sixers": "Philadelphia 76ers",
    "suns": "Phoenix Suns",
    "trail blazers": "Portland Trail Blazers",
    "kings": "Sacramento Kings",
    "spurs": "San Antonio Spurs",
    "raptors": "Toronto Raptors",
    "jazz": "Utah Jazz",
    "wizards": "Washington Wizards",
}

def canonical_team_name(name: str) -> str | None:
    if not name:
        return None
    n = name.strip().lower()
    # Exact full name match
    for full in NBA_TEAMS:
        if n == full.lower():
            return full
    # Keyword-based mapping (nicknames/short forms)
    for key, full in TEAM_KEYWORDS.items():
        if key in n:
            return full
    return None


def infer_team_from_text(text: str | None) -> str | None:
    """
    Infer team from ESPN comment text, avoiding opponent mentions.
    We only accept patterns indicating affiliation, not matchup context.
    Accepted examples:
      - "the Hawks recalled..."
      - "Celtics' official site reports"
      - "the Lakers announced..."
    Rejected examples (opponents):
      - "game against the 76ers"
      - "vs. the Knicks"
    """
    if not text:
        return None
    lower = text.lower()

    def is_opponent_context(team_key: str) -> bool:
        return (
            f"against the {team_key}" in lower
            or f"vs the {team_key}" in lower
            or f"vs. the {team_key}" in lower
            or f"versus the {team_key}" in lower
        )

    for key, full in TEAM_KEYWORDS.items():
        if is_opponent_context(key):
            # Mentioned as opponent; skip
            continue

        # Possessive or org-owned phrasing suggests affiliation
        if (
            f"the {key} " in lower
            or f" {key}'s" in lower
            or f" {key} official" in lower
        ):
            return full

        # Direct bare keyword can be noisy; require a nearby verb/noun
        if key in lower:
            # Require verbs indicating actions by the org (recalled, ruled out, announced)
            window_ok = any(
                phrase in lower for phrase in (
                    f"{key} recalled",
                    f"{key} ruled",
                    f"{key} announced",
                    f"{key} signed",
                    f"{key} placed",
                )
            )
            if window_ok and not is_opponent_context(key):
                return full
    return None


def with_inferred_teams(players: List[PlayerStatus]) -> List[PlayerStatus]:
    enriched: List[PlayerStatus] = []
    for p in players:
        team = p.team or infer_team_from_text(p.reason)
        enriched.append(
            PlayerStatus(
                team=team,
                player_name=p.player_name,
                status=p.status,
                reason=p.reason,
                expected_return=p.expected_return,
            )
        )
    return enriched


# --- LangChain tool functions ---
@tool
def refresh_injuries() -> str:
    """Fetch latest ESPN injuries and store them to CSV. Returns a short status string."""
    players = fetch_and_store_injuries()
    return f"Refreshed injuries: stored {len(players)} rows to CSV."
@tool
def get_injury_status(player_name: str) -> str:
    """Return the injury status summary for a given player name."""
    players = load_player_statuses_from_csv()
    if not players:
        players = fetch_and_store_injuries()
    players = with_inferred_teams(players)

    matches = [p for p in players if p.player_name.lower() == player_name.lower()]
    if not matches:
        return f"No injury info found for {player_name}."

    lines = []
    for p in matches:
        line = f"{p.player_name}"
        if p.team:
            line += f" ({p.team})"
        line += f": {p.status}"
        if p.reason:
            line += f" — {p.reason}"
        if p.expected_return:
            line += f"; expected return: {p.expected_return}"
        lines.append(line)
    return "\n".join(lines)


@tool
def get_team_roster(team_name: str) -> str:
    """Return injured players matching a given NBA team name."""
    players = load_player_statuses_from_csv()
    if not players:
        players = fetch_and_store_injuries()
    # Prefer explicit team field from CSV; inference only as fallback
    team_full = canonical_team_name(team_name) or team_name
    team_lower = team_full.lower()
    team_players = [p for p in players if (p.team or "").lower() == team_lower]

    if not team_players:
        # Fallback: try inference from comments
        enriched = with_inferred_teams(players)
        team_players = [p for p in enriched if (p.team or "").lower() == team_lower]

    if not team_players:
        return f"No injured players found for team: {team_full}."

    lines = [f"Injured players for {team_full}:"]
    for p in team_players:
        line = f"- {p.player_name}: {p.status}"
        if p.expected_return:
            line += f" (return: {p.expected_return})"
        lines.append(line)
    return "\n".join(lines)
