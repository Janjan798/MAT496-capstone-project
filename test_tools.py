from typing import List

from app.state import PlayerStatus
from app.tools import (
    fetch_espn_injuries_raw,
    df_to_player_statuses,
    fetch_and_store_injuries,
    summarize_injuries_with_llm,
)


def main() -> None:
    print("Fetching ESPN injury table...")
    df = fetch_espn_injuries_raw()

    print("Columns in ESPN DF:", list(df.columns))
    print("First 5 rows:")
    print(df.head())

    print("\nConverting full DF to PlayerStatus list...")
    players: List[PlayerStatus] = df_to_player_statuses(df)
    print(f"Found {len(players)} players with injury rows")

    # Show first 5 as sanity check
    for p in players[:5]:
        print(p.model_dump())

    print("\nSaving players to CSV + reloading...")
    stored_players = fetch_and_store_injuries()
    print(f"Stored and reloaded {len(stored_players)} players")

    print("\nAsking LLM to summarize injuries...")
    summary = summarize_injuries_with_llm(stored_players)
    print("\n====== LLM SUMMARY ======")
    print(summary)


if __name__ == "__main__":
    main()
