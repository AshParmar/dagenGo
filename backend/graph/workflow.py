from graph.builder import DagenGoGraph


class DagenGoWorkflow:

    def __init__(self):

        self.graph = (
            DagenGoGraph()
            .build()
            .compile()
        )

    def invoke(
        self,
        state: dict,
    ):

        return self.graph.invoke(state)

    async def ainvoke(
        self,
        state: dict,
    ):

        return await self.graph.ainvoke(state)

    def stream(
        self,
        state: dict,
    ):

        return self.graph.stream(state)

    async def astream(
        self,
        state: dict,
    ):

        async for event in self.graph.astream(state):
            yield event