import json
from tests.test_img_gen import generate_test_image, make_contrasty_png

async def test_happy_path(client):
    img = make_contrasty_png((400, 400)) # High-contrast image needed to pass contrast threshold check
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"market": "UK"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "APPROVED"
    assert body["img_format"] == "PNG"

async def test_reject_prohibited_filename(client):
    img = generate_test_image()
    response = await client.post(
        "/creative-approval",
        files={"file": ("tobacco_ad.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert any("tobacco" in r.lower() for r in body["reasons"])

async def test_missing_file(client):
    response = await client.post("/creative-approval", data={})
    assert response.status_code == 422  

