from PIL import Image, ImageDraw
import io

def generate_test_image(width, height, color=(255, 0, 0), format="PNG"):
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf

def make_high_contrast_png(width, height):
    # Create a high-contrast image to pass contrast checks 
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    # Left half black, right half white
    draw.rectangle([0, 0, width // 2, height], fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
