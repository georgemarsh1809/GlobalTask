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
    format, width, height, size = await validate_image(file)

    # Default response
    response = {
        "status": "APPROVED",
        "reasons": [],
        "img_format": format,
        "img_width": width,
        "img_height": height,
        "img_size": size
    }

    # 1.2 Check contrast
    contrast = calculate_contrast(img)
    if contrast < 15:
        response["status"] = "REQUIRES REVIEW"
        response["reasons"].append(
            f"Image contrast too low (score {contrast:.2f})"
    )

    # 1.3 Check resolution
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        response["status"] = "REQUIRES_REVIEW"
        response["reasons"].append(
            f"Image resolution too low: {width}x{height}px"
        )

    if width > MAX_WIDTH or height > MAX_HEIGHT:
        response["status"] = "REJECTED"
        response["reasons"].append(
            f"Image resolution too high: {width}x{height}px"
        )

    # 1.4 Check aspect ratio
    aspect_ratio = width / height
    if aspect_ratio > 2 or aspect_ratio < 0.5:
        response["status"] = "REQUIRES_REVIEW"
        response["reasons"].append(
            f"Aspect ratio is too high: {aspect_ratio:.2f}"
        )

    # 2. Keyword Filters

    # 3. Metadata checks

    return CreativeApprovalResponse(**response)

