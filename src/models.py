from pydantic import BaseModel, ConfigDict
from typing import Optional

class Metadata(BaseModel):
    # Forbid unknown fields in metadata payloads
    model_config = ConfigDict(extra='forbid')
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
    img_size_mb: float
