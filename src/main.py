from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
import os
from .services import *

class Metadata(BaseModel):
    market: Optional[str] = None
    placement: Optional[str] = None
    audience: Optional[str] = None
    category: Optional[str] = None

class CreativeApprovalResponse(BaseModel):
    status: str
    reasons: list[str]
    img_format: str
    img_width: int
    img_height: int
    img_size: int

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
def get_health():
    return {
        "status": "ok",
        "service": "creative-approval-api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/creative-approval", response_model=CreativeApprovalResponse)
async def creative_approval(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    meta_dict = json.loads(metadata) if metadata else {}

    # Default response
    response = {
            "status": "APPROVED",
            "reasons": [],
            "img_format": "",
            "img_width": 0,
            "img_height": 0,
            "img_size": 0
            }
        
    # 1. Check File Properties

    # 2. Keyword Filters

    # 3. Metadata checks

    return CreativeApprovalResponse(**response)
    




