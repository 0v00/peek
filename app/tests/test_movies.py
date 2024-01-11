from fastapi.testclient import TestClient
from app.main import app
from PIL import Image
from io import BytesIO
import base64

client = TestClient(app)

def test_get_movies():
    expected_movies = [
        {"id": 1, "title": "Blood Sport", "year": 1988, "director": "Newt Arnold"},
        {"id": 2, "title": "Boiling Point", "year": 1990, "director": "Takeshi Kitano"},
        {"id": 3, "title": "Ghost in the Shell", "year": 1995, "director": "Mamoru Oshii"}
    ]

    response = client.get("/movies")
    assert response.status_code == 200
    assert response.json() == expected_movies

def test_get_movie_screenshot():
    movie_id = 1
    response = client.get(f"/movies/{movie_id}/screenshot")
    assert response.status_code == 200
    assert "screenshot" in response.json()
    assert "detr_output" in response.json()

def test_format_get_movie_screenshot():
    movie_id = 1
    response = client.get(f"/movies/{movie_id}/screenshot")
    screenshot_data = response.json().get("screenshot")
    assert screenshot_data is not None
    screenshot_binary = base64.b64decode(screenshot_data)
    image = Image.open(BytesIO(screenshot_binary))
    assert image.format == "JPEG"

def test_get_movie_gif():
    movie_id = 3
    response = client.get(f"/movies/{movie_id}/gif")
    assert response.status_code == 200

def test_format_get_movie_gif():
    movie_id = 3
    response = client.get(f"/movies/{movie_id}/gif")
    gif_data = response.json().get("data")
    assert gif_data is not None
    gif_binary = base64.b64decode(gif_data)
    image = Image.open(BytesIO(gif_binary))
    assert image.format == "GIF"

def test_invalid_movie_screenshot_id():
    movie_id = 999
    response = client.get(f"/movies/{movie_id}/screenshot")
    assert response.status_code == 404
    assert response.json().get("detail") == "movie not found"

def test_invalid_movie_gif_id():
    movie_id = 999
    response = client.get(f"/movies/{movie_id}/gif")
    assert response.status_code == 404
    assert response.json().get("detail") == "movie not found"