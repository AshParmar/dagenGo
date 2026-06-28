from fastapi import FastAPI

from api.query import router as query_router


app = FastAPI(
    title="DagenGo",
    version="1.0.0",
    description="Cross-Lingual Research & Fact Verification Agent"
)

app.include_router(
    query_router,
    prefix="/api",
    tags=["Research"]
)


@app.get("/")
async def root():

    return {
        "message": "Welcome to DagenGo API",
        "status": "running"
    }