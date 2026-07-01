from graph.state import DagenGoState


class Router:
    """Routes graph execution between control-flow branches."""

    @staticmethod
    def judge_route(state: DagenGoState) -> str:
        """Route to reflection if not approved and retry budget remains."""
        approved = bool(state.get("approved", False))
        retry_count = int(state.get("retry_count", 0))

        if approved:
            return "end"

        if retry_count < 2:
            return "reflection"

        return "end"

    @staticmethod
    def reflection_route(state: DagenGoState) -> str:
        """Route back to rewrite/retrieval/graph or end based on reflection action."""
        action = state.get("next_action")

        if action in ("retrieve_again", "web_search"):
            return "rewrite"
        elif action == "graph_retrieve":
            return "graph"

        return "end"

