from graph.builder import DagenGoGraph
from graph.state import DagenGoState


class DagenGoWorkflow:

    def __init__(self):

        self.graph = (
            DagenGoGraph()
            .build()
            .compile()
        )

    def invoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        return self.graph.invoke(state)

    async def ainvoke(
        self,
        state: DagenGoState,
    ) -> DagenGoState:

        return await self.graph.ainvoke(state)

    def stream(
        self,
        state: DagenGoState,
    ):

        return self.graph.stream(state)

    async def astream(
        self,
        state: DagenGoState,
    ):

        async for event in self.graph.astream(state):
            yield event