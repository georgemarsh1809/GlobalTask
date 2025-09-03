import json
from pydantic import ValidationError
from typing import Optional
from datetime import datetime
from fastapi import (
    FastAPI, 
    File, 
    Form, 
    UploadFile, 
    HTTPException
)
from .models import CreativeApprovalResponse, Metadata
from .services import (
    open_file, 
    validate_image, 
    calculate_contrast, 
    get_gif_info, 
)
from .checks import (
    check_filename, 
    check_metadata
)
from .rules import (
    MIN_CONTRAST, 
    MIN_WIDTH, 
    MIN_HEIGHT, 
    MAX_WIDTH, 
    MAX_HEIGHT, 
    MAX_ASPECT_RATIO, 
    MIN_ASPECT_RATIO, 
    MAX_FILE_BYTES
)
from .constants import (
    STATUS_APPROVED, 
    STATUS_REJECTED, 
    STATUS_REQUIRES_REVIEW
)

app = FastAPI(
    title="Creative Approval API", 
    version="0.1.0", 
    description="An API to return a creative approval response based on some simple heuristics"
)

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
    
    try:
        meta = Metadata.model_validate_json(metadata) if metadata else Metadata()
    except (ValidationError, ValueError) as e:
        detail = {
            "message": "Invalid metadata",
            "errors": e.errors() if isinstance(e, ValidationError) else str(e),
        }
        raise HTTPException(status_code=422, detail=detail)

    # Open the file
    img, size_bytes  = await open_file(file)
    size_mb = round(size_bytes / (1024 * 1024), 2)

    # Check file size is not over limit → if truthy, raise 422 error
    limit_mb = round(MAX_FILE_BYTES / (1024 * 1024))
    if size_bytes > MAX_FILE_BYTES: 
        raise HTTPException(status_code=422, detail=f"File too large: {size_mb} MB (limit {limit_mb} MB)")

    # 1. Check File Properties
    # 1.1 Validate file format
        # Returns a 422 error if invalid:
    img_format, width, height = await validate_image(img)

    # Default response, with file format, width, height, and size in mb
    response = {
        "status": STATUS_APPROVED,
        "reasons": [],
        "img_format": img_format,
        "img_width": width,
        "img_height": height,
        "img_size_mb": size_mb
    }

    # 1.2 Check resolution
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        response["status"] = STATUS_REQUIRES_REVIEW
        response["reasons"].append(
            f"Image resolution too low: {width}x{height}px"
        )

    if width > MAX_WIDTH or height > MAX_HEIGHT:
        response["status"] = STATUS_REJECTED
        response["reasons"].append(
            f"Image resolution too high: {width}x{height}px"
        )

    # 1.3 Check aspect ratio
    aspect_ratio = width / height
    if aspect_ratio > MAX_ASPECT_RATIO or aspect_ratio < MIN_ASPECT_RATIO: # if ratio is greater than 2:1
        response["status"] = STATUS_REQUIRES_REVIEW
        response["reasons"].append(
            f"Aspect ratio out of bounds (0.5-2.0): {aspect_ratio:.2f}"
        )   

    # 1.4 Check contrast 
    contrast = calculate_contrast(img)
    if contrast < MIN_CONTRAST:
        response["status"] = STATUS_REQUIRES_REVIEW
        response["reasons"].append(
            f"Image contrast too low (score {contrast:.2f})"
    )
        
    # 2. Check filename for restricted/prohibited terms
    status, reasons = check_filename(file.filename)
    if status != STATUS_APPROVED:
        response["status"] = status
        response["reasons"].extend(reasons)

    # 3. Metadata checks
    if meta:
        status, reasons = check_metadata(meta)
        if status != STATUS_APPROVED:
            response["status"] = status
            response["reasons"].extend(reasons)

    return CreativeApprovalResponse(**response)
