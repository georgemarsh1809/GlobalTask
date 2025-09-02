from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import json
import os
from .services import *
from .rules import *
from .models import *

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
    meta = Metadata(**json.loads(metadata)) if metadata else Metadata()

    img, file_format, contents  = await open_file(file)

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
    if aspect_ratio > 2 or aspect_ratio < 0.5: # if ratio is greater than 2:1
        response["status"] = "REQUIRES_REVIEW"
        response["reasons"].append(
            f"Aspect ratio is too high: {aspect_ratio:.2f}"
        )   

    # 2. Keyword Filters
    # 2.1 Check filename for restricted/prohibited terms
    status, reasons = check_filename(file.filename)
    if status != "APPROVED":
        response["status"] = status
        response["reasons"].extend(reasons)

    # 3. Metadata checks
    if meta:
        status, reasons = check_metadata(meta)
        if status != "APPROVED":
            response["status"] = status
            response["reasons"].extend(reasons)

    return CreativeApprovalResponse(**response)

