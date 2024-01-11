from fastapi import APIRouter, HTTPException
from ..database import get_all_movies, get_movie_by_id
from ..image_processing.detr_resnet_101 import detectObjects
from ..image_processing.segment_images import segment_image, predict
from ..utils.ffmpeg_utils import take_screenshot, get_movie_duration
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

@router.get("/movies/{movie_id}/segmentscreenshot")
async def segment_whole_screenshot(movie_id: int):
    MAX_ATTEMPTS = 5
    for _ in range(MAX_ATTEMPTS):
        encoded_screenshot, detr_output = take_screenshot_with_detr(movie_id)
        person_objects = [obj for obj in detr_output if obj['label'] == 'person']
        if person_objects:
            segmented_screenshot = segment_image(encoded_screenshot)
            return {
                "screenshot": encoded_screenshot,
                "segmented_screenshot": segmented_screenshot,
                "detr_output": detr_output
            }
    raise HTTPException(status_code=404, detail="no living things found in movie, weird.")

@router.get("/movies/{movie_id}/singleprediction")
async def get_single_prediction(movie_id: int):
    MAX_ATTEMPTS = 5
    for _ in range(MAX_ATTEMPTS):
        encoded_screenshot, detr_output = take_screenshot_with_detr(movie_id)
        person_objects = [obj for obj in detr_output if obj['label'] == 'person']
        if person_objects:
            highest_confidence = max(person_objects, key=lambda x: x['confidence'])
            prediction = predict(encoded_screenshot, highest_confidence['box'])
            return {
                "screenshot": encoded_screenshot,
                "prediction": prediction,
                "detr_output": detr_output
            }
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
    encoded_screenshot = base64.b64encode(image_data).decode('utf-8')
    return encoded_screenshot, detr_output