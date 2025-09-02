from PIL import Image, ImageStat, ImageSequence
import io
from .terms import PROHIBITED_THEMES_KEYWORDS, AGE_PROHIBITED_THEMES_KEYWORDS, RESTRICTED_COUNTRY_KEYWORDS, RESTRICTED_THEMES_KEYWORDS, CHILD_AUDIENCE_KEYWORDS
from fastapi import HTTPException, UploadFile
from .models import Metadata

# 1. File Props
async def open_file(file: UploadFile):
    contents = await file.read()
    
    try:
        img = Image.open(io.BytesIO(contents))
        img.load()  
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid or unreadable image file")

    await file.seek(0)

    return img, img.format, contents


# validate image format, width, height and size
async def validate_image(file):
    img, file_format, contents  = await open_file(file)

    width, height = img.size
    size = len(contents)

    if file_format not in ["PNG", "JPEG", "GIF"]:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported image format: {file_format}. Please upload a PNG, JPEG or GIF."
        )

    return file_format, width, height, size

# check contrast
def calculate_contrast(img: Image.Image) -> float:
    grayscale = img.convert("L")
    stat = ImageStat.Stat(grayscale)
    return stat.stddev[0]

# check file complexity
def check_complexity(file):
    pass

def get_gif_info(img: Image.Image) -> tuple[int, list[int]]:
    frame_count = 0
    durations = []  

    for frame in ImageSequence.Iterator(img):
        frame_count += 1
        duration = frame.info.get("duration", 0)
        durations.append(duration)

    return frame_count, durations


# 2. Keyword Matches
# check against PROHIBITED_THEMES_KEYWORDS
# respond with REJECTION or None

# check against RESTRICTED_COUNTRY_KEYWORDS
# respond with REQUIRES_REVIEW or None

# check against RESTRICTED_THEMES_KEYWORDS
# respond with REQUIRES_REVIEW or None
def check_filename(filename: str) -> tuple[str, list[str]]:
    text = filename.lower()
    reasons = []

    for word in PROHIBITED_THEMES_KEYWORDS:
        if word in text:
            return "REJECTED", [f"Prohibited term in filename: {word}"]

    for word in RESTRICTED_THEMES_KEYWORDS:
        if word in text:
            reasons.append(f"Restricted term in filename: {word}")

    for word in RESTRICTED_COUNTRY_KEYWORDS:
        if word in text:
            reasons.append(f"Restricted country name in filename: {word}")

    if reasons:
        return "REQUIRES_REVIEW", reasons

    return "APPROVED", []

def is_child_audience(audience: str | None) -> bool:
    if not audience:
        return False
    text = audience.lower()
    return any(term in text for term in CHILD_AUDIENCE_KEYWORDS)


# 3. Meta-data based checks (if parsed)
def check_metadata(meta: Metadata) -> tuple[str, list[str]]:
    reasons = []
    text_fields = [meta.market, meta.placement, meta.audience, meta.category]

    # Flatten into a single lowercase string for scanning
    combined_text = " ".join([t for t in text_fields if t]).lower()

    if is_child_audience(meta.audience) or meta.placement == 'near_school':
        if meta.category and any(
            word in meta.category.lower()
            for word in AGE_PROHIBITED_THEMES_KEYWORDS
        ):
            return "REJECTED", [f"Child-related audience found: {meta.audience}. Category not allowed."]

        reasons.append(f"Child-related audience found: {meta.audience}")
        return "REQUIRES_REVIEW", reasons

    # Prohibited → immediate rejection
    for word in PROHIBITED_THEMES_KEYWORDS:
        if word in combined_text:
            return "REJECTED", [f"Prohibited term found in metadata: {word}"]
        
    for word in AGE_PROHIBITED_THEMES_KEYWORDS:
        if word in combined_text :
            return "REJECTED", [f"Age restricted term found in metadata: {word}"]

    # Restricted → requires review
    for word in RESTRICTED_THEMES_KEYWORDS:
        if word in combined_text:
            reasons.append(f"Restricted term found in metadata: {word}")

    for country in RESTRICTED_COUNTRY_KEYWORDS:
        if country in meta.market:
            reasons.append(f"Restricted country found in metadata: {country}")

    if reasons:
        return "REQUIRES_REVIEW", reasons

    return "APPROVED", []


# check against AGE_PROHIBITED_THEMES_KEYWORDS  
# respond with REJECTION or None
