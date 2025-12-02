from typing import Dict, Any

from app.graph import app
from app.tools import load_player_statuses_from_csv, fetch_and_store_injuries


def main() -> None:
    print("NBA Injury Assistant (LangGraph) — Interactive Mode")

    # Ensure we have local data: load CSV or fetch & store
    players = load_player_statuses_from_csv()
    if not players:
        print("No local CSV found or it's empty. Fetching injuries from ESPN...")
        players = fetch_and_store_injuries()
        print(f"Stored {len(players)} player status rows to CSV.")

    print("\nType a question (or 'exit' to quit):")

    # Use a fixed thread_id for demo session to satisfy checkpointer
    config = {"configurable": {"thread_id": "cli-session"}}

    while True:
        try:
            user_query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_query:
            continue
        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        initial_state: Dict[str, Any] = {
            "user_query": user_query,
            "team": None,
            "player": None,
            "player_statuses": [],
            "retrieved_context": "",
            "answer": "",
        }

        printed = False
        for event in app.stream(initial_state, config=config, stream_mode="values"):
            answer = event.get("answer")
            if answer:
                print(answer)
                printed = True

        if not printed:
            final_state = app.invoke(initial_state, config=config)
            answer = final_state.get("answer")
            if answer:
                print(answer)
            else:
                print("[No answer produced]")


if __name__ == "__main__":
    main()
