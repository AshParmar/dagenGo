from fastapi import FastAPI,FastRouter,Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
app=FastAPI()
router = FastRouter()

class query(BaseModel):
    query_text:str
@router.post('/query')
async def query(query:query):
    wq=query.query_text
    if wq:
        return JSONResponse(content={"message": f"Query received: {wq}"})
    else:
        return JSONResponse(content={"message": "No query received"})
