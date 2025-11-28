import os
from pathlib import Path
from typing import List

import pandas as pd
from langchain_openai import ChatOpenAI

from .state import PlayerStatus

ESPN_INJURIES_URL = "https://www.espn.in/nba/injuries"

# Where to store structured data
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "nba_injuries.csv"

llm = ChatOpenAI(model="gpt-5", temperature=0)  


def fetch_espn_injuries_raw() -> pd.DataFrame:
    """
    Fetch NBA injury tables from ESPN and return a DataFrame.
    """
    tables = pd.read_html(ESPN_INJURIES_URL) 
    if not tables:
        raise RuntimeError("No tables found on ESPN injuries page")

    combined = pd.concat(tables, ignore_index=True)
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

        expected_return = row.get("EST. RETURN DATE") if "EST. RETURN DATE" in df.columns else None
        comment = row.get("COMMENT") if "COMMENT" in df.columns else None

        player_statuses.append(
            PlayerStatus(
                team=None,  # can be filled later by another function if you want
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
        players.append(
            PlayerStatus(
                team=row.get("team"),
                player_name=row["player_name"],
                status=row["status"],
                reason=row.get("reason"),
                expected_return=row.get("expected_return"),
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
