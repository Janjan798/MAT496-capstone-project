from typing import Dict, Any

from app.graph import app


def main():
    print("Streaming a question through the LangGraph app...\n")
    initial_state: Dict[str, Any] = {
        "messages": [
            {
                "role": "user",
                "content": "What is LeBron James' current injury status?",
            }
        ]
    }

    for event in app.stream(initial_state, stream_mode="values"):
        messages = event.get("messages", [])
        for m in messages:
            # m is a LangChain AIMessage/ToolMessage; print content safely
            content = getattr(m, "content", None)
            if content:
                print(content)


if __name__ == "__main__":
    main()
