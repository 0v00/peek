from fastapi.testclient import TestClient
from app.main import app
from PIL import Image
from io import BytesIO

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
    assert response.headers["content-type"] == "image/jpeg"

def test_format_get_movie_screenshot():
    movie_id = 1
    response = client.get(f"/movies/{movie_id}/screenshot")
    image = Image.open(BytesIO(response.content))
    assert image.format == "JPEG"

def test_get_movie_gif():
    movie_id = 3
    response = client.get(f"/movies/{movie_id}/gif")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"

def test_format_get_movie_gif():
    movie_id = 3
    response = client.get(f"/movies/{movie_id}/gif")
    image = Image.open(BytesIO(response.content))
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