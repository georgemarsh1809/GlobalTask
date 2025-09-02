from PIL import Image, ImageDraw
import io

def generate_test_image(size=(200, 200), color=(255, 0, 0), format="PNG"):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf

def make_contrasty_png(size=(400, 400)):
    """Create a simple high-contrast image to pass contrast checks."""
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    # Left half black, right half white
    draw.rectangle([0, 0, size[0] // 2, size[1]], fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
