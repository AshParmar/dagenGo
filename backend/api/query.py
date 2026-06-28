from fastapi import APIRouter

from schemas.query import QueryRequest
from graph.workflow import DagenGoWorkflow


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