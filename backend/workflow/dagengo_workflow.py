from graph.state import DagenGoState
from graph.workflow import DagenGoWorkflow


class DagenGoWorkflowRunner:
    """Thin adapter around the compiled graph workflow."""

    def __init__(self) -> None:
        self.workflow = DagenGoWorkflow()

    async def run(self, state: DagenGoState) -> DagenGoState:
        """Invoke workflow asynchronously."""
        return await self.workflow.ainvoke(state)
