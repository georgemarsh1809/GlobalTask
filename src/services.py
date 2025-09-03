import io
from PIL import Image, ImageStat, ImageSequence
from fastapi import HTTPException, UploadFile
from .terms import CHILD_AUDIENCE_KEYWORDS, CHILD_PLACEMENT_KEYWORDS

# Open file - return the Image object, as well as the size in bytes for consumption in main.py
async def open_file(file: UploadFile) -> tuple[Image.Image, int]:
    contents = await file.read()
    
    try:
        img = Image.open(io.BytesIO(contents))
        img.load()  
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid or unreadable image file")
    
    size_bytes = len(contents)

    return img, size_bytes

# validate image format, width, height and size
async def validate_image(img) -> tuple[str, int, int]:
    format = img.format
    width, height = img.size

    if format not in ["PNG", "JPEG", "GIF"]:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported image format: {format}. Please upload a PNG, JPEG or GIF."
        )

    return format, width, height

# Calculate contrast
def calculate_contrast(img: Image.Image) -> float:
    grayscale = img.convert("L")
    stat = ImageStat.Stat(grayscale)
    return stat.stddev[0]

def get_gif_info(img: Image.Image) -> tuple[int, float]:
    frame_count = 0
    durations = []  # each frame's duration in ms

    for frame in ImageSequence.Iterator(img):
        frame_count += 1
        durations.append(frame.info.get("duration", 0))

    if durations:
        avg_duration = sum(durations) / len(durations)  # ms
        fps = 1000 / avg_duration if avg_duration > 0 else 0
    else:
        fps = 0

    return frame_count, fps

# Use CHILD_AUDIENCE_KEYWORDS to confirm if audience is related to children, 'u18', 'kids', etc.
def is_child_audience(audience: str | None) -> bool:
    if not audience:
        return False
    text = audience.lower()
    return any(term in text for term in CHILD_AUDIENCE_KEYWORDS)

# Use CHILD_PLACEMENT_KEYWORDS to confirm if placement is related to children, 'school', 'nursery'
def is_child_placement(placement: str | None) -> bool:
    if not placement:
        return False
    text = placement.lower()
    return any(term in text for term in CHILD_PLACEMENT_KEYWORDS)

