from fastapi import APIRouter
from pydantic import BaseModel

from graph.workflow import DagenGoWorkflow


class QueryRequest(BaseModel):
    """Request payload for query execution."""

    query: str


router = APIRouter()

workflow = DagenGoWorkflow()


@router.post("/query")
async def query(
    request: QueryRequest,
):

    state = {
        "query": request.query,
        "retry_count": 0,
    }

    result = await workflow.ainvoke(
        state
    )

    return {
        "answer": result["final_answer"],
        "citations": result.get(
            "citations",
            [],
        ),
        "confidence": result.get(
            "confidence",
            {},
        ),
        "hallucination": result.get(
            "hallucination",
            {},
        ),
        "groundedness": result.get(
            "groundedness",
            {},
        ),
    }