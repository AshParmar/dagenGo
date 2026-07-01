import json
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from graph.workflow import DagenGoWorkflow


class QueryRequest(BaseModel):
    """Request payload for query execution."""

    query: str
    settings: dict | None = None


router = APIRouter()

workflow = DagenGoWorkflow()


def _safe_score(value: Any) -> float | None:
    if isinstance(value, dict):
        for key in ("confidence_score", "groundedness_score", "hallucination_score", "score"):
            if key in value:
                return _safe_score(value[key])
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return None


def _normalize_citation(item: dict, index: int) -> dict:
    url = item.get("url") or item.get("link") or item.get("source_url")
    domain = item.get("domain") or item.get("website") or item.get("source")
    return {
        "id": str(item.get("id") or item.get("url") or f"citation-{index}"),
        "title": item.get("title") or item.get("name") or f"Source {index + 1}",
        "source": item.get("source"),
        "website": item.get("website") or domain,
        "domain": domain,
        "provider": item.get("provider"),
        "publication_date": item.get("publication_date") or item.get("published_date") or item.get("date"),
        "language": item.get("language"),
        "confidence": _safe_score(item.get("confidence") or item.get("score") or item.get("relevance")),
        "snippet": item.get("snippet") or item.get("text") or item.get("content"),
        "url": url,
        "favicon_url": item.get("favicon_url") or item.get("favicon"),
    }


def _knowledge_graph_from_result(result: dict) -> dict:
    knowledge_graph = result.get("knowledge_graph")
    if isinstance(knowledge_graph, dict):
        return {
            "nodes": knowledge_graph.get("nodes") or [],
            "edges": knowledge_graph.get("edges") or [],
        }

    nodes = []
    for index, entity in enumerate(result.get("entities") or []):
        if isinstance(entity, dict):
            entity_id = entity.get("id") or entity.get("name") or f"entity-{index}"
            nodes.append(
                {
                    "id": str(entity_id),
                    "label": entity.get("label") or entity.get("name") or f"Entity {index + 1}",
                    "type": entity.get("type") or "entity",
                }
            )

    edges = []
    for index, relation in enumerate(result.get("relations") or []):
        if isinstance(relation, dict):
            source = relation.get("source") or relation.get("from")
            target = relation.get("target") or relation.get("to")
            if source and target:
                edges.append(
                    {
                        "from": str(source),
                        "to": str(target),
                        "label": relation.get("relation") or relation.get("label"),
                    }
                )

    return {"nodes": nodes, "edges": edges}


def _normalize_response(result: dict, query: str) -> dict:
    execution_steps = result.get("execution_steps") or []
    retrieved_documents = result.get("retrieved_documents") or []
    chunks = result.get("chunks") or []
    citations = result.get("citations") or retrieved_documents
    metadata = result.get("metadata") or {}

    return {
        "query": result.get("query") or query,
        "answer": result.get("final_answer") or result.get("answer") or "",
        "citations": [
            _normalize_citation(citation, index)
            for index, citation in enumerate(citations)
            if isinstance(citation, dict)
        ],
        "execution_steps": execution_steps,
        "timeline": result.get("timeline") or [],
        "knowledge_graph": _knowledge_graph_from_result(result),
        "metrics": {
            "confidence": _safe_score(result.get("confidence")),
            "groundedness": _safe_score(result.get("groundedness")),
            "hallucination": _safe_score(result.get("hallucination")),
        },
        "metadata": {
            "documents_retrieved": metadata.get("documents_retrieved", len(retrieved_documents)),
            "chunks": metadata.get("chunks", len(chunks)),
            "provider": metadata.get("provider", "Gemini"),
            "latency": metadata.get(
                "latency",
                sum(step.get("elapsedMs", 0) for step in execution_steps if isinstance(step, dict))
                / 1000,
            ),
        },
    }


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.post("/query")
async def query(request: QueryRequest):
    from llm.models import request_settings
    request_settings.set(request.settings or {})
    state = {
        "query": request.query,
        "settings": request.settings or {},
        "retry_count": 0,
    }
    result = await workflow.ainvoke(state)
    return _normalize_response(result, request.query)


def _get_language_name(code: str) -> str:
    lang_map = {
        "en": "English",
        "fr": "French",
        "de": "German",
        "ja": "Japanese",
        "zh": "Chinese",
        "es": "Spanish",
        "hi": "Hindi",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ko": "Korean",
    }
    return lang_map.get(str(code).lower().split("-")[0], "English")


@router.post("/query/stream")
async def query_stream(request: QueryRequest):
    async def events():
        from llm.models import request_settings
        request_settings.set(request.settings or {})
        state = {
            "query": request.query,
            "settings": request.settings or {},
            "retry_count": 0,
        }
        yield _sse("start", {"query": request.query})

        # Initialize final_state with the starting state
        final_state = dict(state)
        emitted_steps = 0
        try:
            async for chunk in workflow.astream(state):
                if not isinstance(chunk, dict):
                    continue

                # Accumulate all updates from nodes into final_state
                for node_name, node_state in chunk.items():
                    if isinstance(node_state, dict):
                        final_state.update(node_state)

                # Ensure language is mapped to a human-readable name in final_state
                if "language" in final_state:
                    final_state["language"] = _get_language_name(final_state["language"])

                steps = final_state.get("execution_steps") or []
                for step in steps[emitted_steps:]:
                    if isinstance(step, dict):
                        yield _sse("stage", {"stage": step})
                emitted_steps = len(steps)

                answer = final_state.get("final_answer") or final_state.get("answer")
                if answer:
                    yield _sse("answer", {"answer": answer})

            yield _sse("result", _normalize_response(final_state, request.query))
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
