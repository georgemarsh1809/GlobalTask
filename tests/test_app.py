import json
from tests.test_img_gen import (
    generate_test_image, 
    make_high_contrast_png
)

# T.1: Test happy path with a PNG → APPROVED
async def test_happy_path_png(client):
    img = make_high_contrast_png(400, 400) # High-contrast image needed to pass contrast threshold check
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"market": "UK"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "APPROVED"
    assert body["img_format"] == "PNG"

# T.2: Test happy path with a JPEG → APPROVED
async def test_happy_path_jpg(client):
    img = make_high_contrast_png(400, 400) # High-contrast image needed to pass contrast threshold check
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"market": "US"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "APPROVED"
    assert body["img_format"] == "PNG"

# T.3: Test prohibited term in filename, 'tobacco' → REJECTED
async def test_prohibited_filename_rejected(client):
    img = generate_test_image(400, 400)
    response = await client.post(
        "/creative-approval",
        files={"file": ("tobacco_ad.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert any("tobacco" in r.lower() for r in body["reasons"])

# T.4: Test restricted terms in filename, 'vape', 'taxi' → REQUIRES_REVIEW
async def test_restricted_filename_requires_review(client):
    img = generate_test_image(400, 400)
    response = await client.post(
        "/creative-approval",
        files={"file": ("taxi_vape.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert any("taxi" in r.lower() for r in body["reasons"])
    assert any("vape" in r.lower() for r in body["reasons"])

# T.5: Test restricted country in filename, 'iran' → REQUIRES_REVIEW
async def test_restricted_country_filename_requires_review(client):
    img = generate_test_image(400, 400)
    response = await client.post(
        "/creative-approval",
        files={"file": ("iran.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Restricted country name in filename: iran"in body["reasons"]

# T.6: Test resolution too high, 400x10001px → REQUIRES_REVIEW
async def test_high_resolution_requires_review(client):
    img = generate_test_image(400, 10001)
    response = await client.post(
        "/creative-approval",
        files={"file": ("img.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Image resolution too high: 400x10001px" in body["reasons"]

# T.7: Test resolution too low, 100x100px → REQUIRES_REVIEW
async def test_low_resolution_requires_review(client):
    img = generate_test_image(100, 100)
    response = await client.post(
        "/creative-approval",
        files={"file": ("img.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Image resolution too low: 100x100px" in body["reasons"]

# T.8: Test aspect ratio too high, 300:900 (1:3) → REQUIRES_REVIEW
async def test_out_of_range_aspect_ratio_requires_review(client):
    img = make_high_contrast_png(300, 900)
    response = await client.post(
        "/creative-approval",
        files={"file": ("img.png", img, "image/png")}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert 'Aspect ratio out of bounds (0.5-2.0): 0.33' in body["reasons"]

# T.9: Test if metadata contains prohibited themes → REJECTED
async def test_metadata_prohibited_themes(client):
    img = make_high_contrast_png(400, 400) # High-contrast image needed to pass contrast threshold check
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"category": "tobacco"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert "Prohibited term found in metadata: tobacco" in body["reasons"]

# T.10: Test if metadata contains restricted themes → REJECTED
async def test_metadata_restricted_themes(client):
    img = make_high_contrast_png(400, 400) 
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"category": "crypto"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Restricted term found in metadata: crypto" in body["reasons"]

# T.11: Test restricted country in metadata {"market": "iran"} → REQUIRES_REVIEW
async def test_metadata_restricted_country(client):
    img = make_high_contrast_png(400, 400) 
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"market": "iran"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Restricted country found in metadata: iran" in body["reasons"]

# T.12: Test child-related placement → REQUIRES_REVIEW
async def test_metadata_child_related_placement(client):
    img = make_high_contrast_png(400, 400) 
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"placement": "school"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Child-related placement found: school" in body["reasons"]

# T.13: Test child-related placement AND age-prohibited category → REJECTED
async def test_metadata_child_related_placement_and_age_prohibited_category(client):
    img = make_high_contrast_png(400, 400) #
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"category": "alcohol", "placement": "school"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert "Child-related placement found: school. Category not allowed." in body["reasons"]

# T.14: Test child-related audience → REQUIRES_REVIEW
async def test_metadata_child_related_audience(client):
    img = make_high_contrast_png(400, 400) 
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"audience": "kids"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REQUIRES_REVIEW"
    assert "Child-related audience found: kids" in body["reasons"]

# T.15: Test child-related audience AND age-prohibited category → REJECTED
async def test_metadata_child_related_audience_and_age_prohibited_category(client):
    img = make_high_contrast_png(400, 400) 
    response = await client.post(
        "/creative-approval",
        files={"file": ("test.png", img, "image/png")},
        data={"metadata": json.dumps({"audience": "kids", "category": "alcohol"})}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert "Child-related audience found: kids. Category not allowed." in body["reasons"]

# T.16: Test missing files → 422 error thrown
async def test_missing_file(client): 
    response = await client.post("/creative-approval", data={})
    assert response.status_code == 422  

