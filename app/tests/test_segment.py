from fastapi.testclient import TestClient
from app.main import app
import pytest
from io import BytesIO
import base64

client = TestClient(app)

@pytest.fixture(scope="module")
def test_image():
    with open('test_data.png', 'rb') as file:
        yield file.read()

@pytest.fixture(scope="module")
def invalid_image_data():
    return BytesIO(b"This is not a valid image file")

def test_overlay_mask(test_image):
    response = client.post("/segment/overlay_mask", files={"file": test_image}, data={"label": "person"})
    assert response.status_code == 200
    assert "image_with_mask" in response.json()
    assert "detr_output" in response.json()

def test_overlay_mask_base64(test_image):
    response = client.post("/segment/overlay_mask", files={"file": test_image}, data={"label": "person"})
    data = response.json()
    image_with_mask = data['image_with_mask']
    base64_bytes = image_with_mask.encode('utf-8')
    decoded_image = base64.b64decode(base64_bytes, validate=True)
    assert isinstance(decoded_image, bytes)

def test_overlay_mask_output_list(test_image):
    response = client.post("/segment/overlay_mask", files={"file": test_image}, data={"label": "person"})
    data = response.json()
    assert isinstance(data['detr_output'], list)

def test_overlay_mask_no_label_found(test_image):
    response = client.post("/segment/overlay_mask", files={"file": test_image}, data={"label": "non_existent_label"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No objects of type 'non_existent_label' detected"}

def test_overlay_mask_invalid_image(invalid_image_data):
    response = client.post("/segment/overlay_mask", files={"file": ("invalid_image.txt", invalid_image_data)}, data={"label": "person"})
    assert response.status_code == 400
    assert "Invalid image file" in response.json().get("detail", "")

def test_extract_obj_with_label(test_image):
    response = client.post("/segment/extract_obj_with_label", files={"file": test_image}, data={"label": "person"})
    assert response.status_code == 200
    assert "extracted_obj" in response.json()
    assert "detr_output" in response.json()

def test_extracted_obj_base64(test_image):
    response = client.post("/segment/extract_obj_with_label", files={"file": test_image}, data={"label": "person"})
    data = response.json()
    extracted_obj = data['extracted_obj']
    base64_bytes = extracted_obj.encode('utf-8')
    decoded_image = base64.b64decode(base64_bytes, validate=True)
    assert isinstance(decoded_image, bytes)

def test_extracted_detr_output_list(test_image):
    response = client.post("/segment/extract_obj_with_label", files={"file": test_image}, data={"label": "person"})
    data = response.json()
    assert isinstance(data['detr_output'], list)

def test_extract_obj_with_label_no_label_found(test_image):
    response = client.post("/segment/extract_obj_with_label", files={"file": test_image}, data={"label": "non_existent_label"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No objects of type 'non_existent_label' detected"}

def test_extract_obj_with_label_invalid_image(invalid_image_data):
    response = client.post("/segment/extract_obj_with_label", files={"file": ("invalid_image.txt", invalid_image_data)}, data={"label": "person"})
    assert response.status_code == 400
    assert "Invalid image file" in response.json().get("detail", "")