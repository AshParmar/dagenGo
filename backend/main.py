from fastapi import FastAPI
from api.query import router as query_router

app = FastAPI(title="LangGraph API", version="0.1.0")
app.include_router(query_router)
@app.get("/")
async def root():
    return {"message": "Ayyy yo! DagenGo!"}