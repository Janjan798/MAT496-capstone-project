from typing import TypedDict, List, Optional
from pydantic import BaseModel


class PlayerStatus(BaseModel):
    team: str
    player_name: str
    status: str          # "OUT" | "DTD (day to day)" | "HEALTHY"
    reason: Optional[str] = None
    expected_return: Optional[str] = None


class AppState(TypedDict):
    # user input
    user_query: str

    # parsed intent
    team: Optional[str]
    player: Optional[str]

    # structured data
    player_statuses: List[PlayerStatus]

    # retrieved text context (for RAG)
    retrieved_context: str

    # final answer
    answer: str
