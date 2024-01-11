from fastapi import APIRouter, HTTPException
from ..database import get_all_movies, get_movie_by_id
from ..image_processing.detr_resnet_101 import detectObjects
from ..image_processing.segment_images import segment_image
from ..utils.ffmpeg_utils import generate_gif, take_screenshot, get_movie_duration
from PIL import Image
from io import BytesIO
import random
import os
import base64

router = APIRouter()

movie_files_directory = "app/movie_files/"

@router.get("/movies")
async def get_movies():
    all_movies = get_all_movies()
    return all_movies

@router.get("/movies/{movie_id}/screenshot")
async def get_movie_screenshot(movie_id: int):
    MAX_ATTEMPTS = 5
    for _ in range(MAX_ATTEMPTS):
        screenshot_data, detr_output = take_screenshot_with_detr(movie_id)
        if any(obj['label'] in ['person'] for obj in detr_output):
            encoded_image = base64.b64encode(screenshot_data).decode('utf-8')
            segmented_image = segment_image(encoded_image)
            return {"screenshot": encoded_image, "segmented_screenshot": segmented_image, "detr_output": detr_output}
    raise HTTPException(status_code=404, detail="no living things found in movie, weird.")

def take_screenshot_with_detr(movie_id: int):
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="movie not found")
    
    file_path = os.path.join(movie_files_directory, movie[-1])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="movie file path not found")
    
    duration = get_movie_duration(file_path)
    screenshot_time = random.uniform(0, duration - 1)
    image_data = take_screenshot(file_path, screenshot_time)
    image = Image.open(BytesIO(image_data))
    detr_output = detectObjects(image)
    return image_data, detr_output

    
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
        base64_encoded_gif = generate_gif(file_path, start_time)
        return {"data": base64_encoded_gif}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error generating gif: {e}")