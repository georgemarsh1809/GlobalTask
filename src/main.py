from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
import os
from .services import *
from .rules import *

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

    img, _, _  = await open_file(file)

    # 1. Check File Properties
    # 1.1 Validate file format
    # Returns a 422 error if invalid:
    file_format, width, height, size = await validate_image(file)

    # Default response
    response = {
        "status": "APPROVED",
        "reasons": [],
        "img_format": file_format,
        "img_width": width,
        "img_height": height,
        "img_size": size
    }

    # 1.2 Calculate contrast
    contrast = calculate_contrast(img)
    if contrast < 15:
        response["status"] = "REQUIRES REVIEW"
        response["reasons"].append(
            f"Image contrast too low (score {contrast:.2f})"
    )

    # check_resolution(file)
    # check_aspect_ratio(file)
    # check_complexity(file)

    # 2. Keyword Filters

    # 3. Metadata checks

    return CreativeApprovalResponse(**response)

