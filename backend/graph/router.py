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
            state["retry_count"] = retry_count + 1
            return "reflection"

        return "end"
