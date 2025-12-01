from typing import List

from app.state import PlayerStatus
from app.tools import fetch_espn_injuries_raw, df_to_player_statuses


def main() -> None:
    print("Fetching ESPN injury tables...")
    df = fetch_espn_injuries_raw()

    print("Columns in ESPN DF:", list(df.columns))
    print("First 5 rows:")
    print(df.head())

    print("\nConverting injuries to PlayerStatus objects...")
    statuses: List[PlayerStatus] = df_to_player_statuses(df)

    print(f"Found {len(statuses)} player status rows:")
    for s in statuses:
        print(s.model_dump())


if __name__ == "__main__":
    main()
