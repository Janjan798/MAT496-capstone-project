from typing import Dict, Any

from app.graph import app


def main():
    print("Streaming a question through the LangGraph app...\n")
    initial_state: Dict[str, Any] = {
        "user_query": "What is Lebron James' current injury status?",
        "team": None,
        "player": None,
        "player_statuses": [],
        "retrieved_context": "",
        "answer": "",
    }

    # MemorySaver checkpointer requires a thread_id in config
    config = {"configurable": {"thread_id": "demo-thread"}}

    printed = False
    for event in app.stream(initial_state, config=config, stream_mode="values"):
        answer = event.get("answer")
        if answer:
            print(answer)
            printed = True

    if not printed:
        # Fallback: directly invoke and print the final state
        final_state = app.invoke(initial_state, config=config)
        answer = final_state.get("answer")
        if answer:
            print(answer)
        else:
            print("[debug] Final state had no 'answer':", final_state)


if __name__ == "__main__":
    main()
