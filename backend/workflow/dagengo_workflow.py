from fastapi import FastAPI,FastRouter,Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
router = FastRouter()
@router.post('/query')
class dagengo_workflow(BaseModel):
    def run_workflow(self, query):
        return JSONResponse(content={"message": "Workflow executed successfully"})
