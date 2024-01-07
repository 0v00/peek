from fastapi import APIRouter, HTTPException, Response
from ..database import get_movie_by_id, get_db_connection
from ..utils.ffmpeg_utils import generate_gif, take_screenshot, get_movie_duration
import subprocess
import random
import os

router = APIRouter()

movie_files_directory = "app/movie_files/"

@router.get("/movies")
async def get_movies():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, title, year, director FROM movies')
    # fetchall() returns a list of tuples
    movies_tuples_list = c.fetchall()
    conn.close()
    # transform it into a list of dict items
    return [{"id": id, "title": title, "year": year, "director": director} for id, title, year, director in movies_tuples_list]

@router.get("/movies/{movie_id}/screenshot")
async def get_movie_screenshot(movie_id: int):
    movie = get_movie_by_id(movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="movie not found")
    
    file_path = os.path.join(movie_files_directory, movie[-1])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="movie file path not found")

    try:
        duration = get_movie_duration(file_path)
        screenshot_time = random.uniform(0, duration - 1)
        image_data = take_screenshot(file_path, screenshot_time)
        return Response(content=image_data, media_type="image/jpeg")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail="error taking screenshot")
    
@router.get("/movies/{movie_id}/gif")
async def get_movie_gif(movie_id: int):
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found")
    
    file_path = os.path.join(movie_files_directory, movie[-1])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="movie file path not found")
    
    try:
        duration = get_movie_duration(file_path)
        if duration <= 10:
            raise HTTPException(status_code=400, detail="movie too short")
        start_time = random.uniform(0, duration - 10)
        gif_data = generate_gif(file_path, start_time)
        return Response(content=gif_data, media_type="image/gif")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error generating gif: {e}")