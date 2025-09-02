from PIL import Image, ImageStat
import io
from .terms import PROHIBITED_THEMES_KEYWORDS, AGE_PROHIBITED_THEMES_KEYWORDS, RESTRICTED_COUNTRY_KEYWORDS, RESTRICTED_THEMES_KEYWORDS
from fastapi import HTTPException, UploadFile

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

# check dimensions/resolution
def check_resolution(file):
    pass

# check aspect ratio
def check_aspect_ratio(file):
    pass

# check contrast
def calculate_contrast(img: Image.Image) -> float:
    grayscale = img.convert("L")
    stat = ImageStat.Stat(grayscale)
    return stat.stddev[0]

# check file complexity
def check_complexity(file):
    pass


# 2. Keyword Matches
# check against PROHIBITED_THEMES_KEYWORDS
# respond with REJECTION or None

# check against RESTRICTED_COUNTRY_KEYWORDS
# respond with REQUIRES_REVIEW or None

# check against RESTRICTED_THEMES_KEYWORDS
# respond with REQUIRES_REVIEW or None


# 3. Meta-data based checks (if parsed)
# check against AGE_PROHIBITED_THEMES_KEYWORDS  
# respond with REJECTION or None
