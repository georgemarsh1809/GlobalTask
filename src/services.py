import io
from PIL import Image, ImageStat, ImageSequence
from fastapi import HTTPException, UploadFile

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

def get_gif_info(img: Image.Image) -> tuple[int, list[int]]:
    frame_count = 0
    durations = []  

    for frame in ImageSequence.Iterator(img):
        frame_count += 1
        duration = frame.info.get("duration", 0)
        durations.append(duration)

    return frame_count, durations

def is_child_audience(audience: str | None) -> bool:
    if not audience:
        return False
    text = audience.lower()
    return any(term in text for term in CHILD_AUDIENCE_KEYWORDS)

def is_child_placement(placement: str | None) -> bool:
    if not placement:
        return False
    text = placement.lower()
    return any(term in text for term in CHILD_PLACEMENT_KEYWORDS)

