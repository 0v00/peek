from fastapi import APIRouter, HTTPException, File, UploadFile
from ..image_processing.detr_resnet_101 import detectObjects
from ..image_processing.segment_images import segment_image, predict, extract_and_save_masked_area
from ..utils.ffmpeg_utils import take_screenshot, get_movie_duration
from PIL import Image
from io import BytesIO
import random
import os
import base64
import shutil
import tempfile

router = APIRouter()

@router.post("/segment/upload/single_prediction")
async def single_prediction(file: UploadFile):
    MAX_ATTEMPTS = 5

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    for _ in range(MAX_ATTEMPTS):
        encoded_screenshot, detr_output = take_screenshot_with_detr_in_mem(temp_file_path)
        person_objects = [obj for obj in detr_output if obj['label'] == 'person']
        if person_objects:
            highest_confidence = max(person_objects, key=lambda x: x['confidence'])
            prediction = predict(encoded_screenshot, highest_confidence['box'])
            os.remove(temp_file_path)
            return {
                "screenshot": encoded_screenshot,
                "prediction": prediction,
                "detr_output": detr_output
            }
    
    os.remove(temp_file_path)
    raise HTTPException(status_code=404, detail="no objects detected")

@router.post("/segment/upload/single_extract")
async def single_extract(file: UploadFile):
    MAX_ATTEMPTS = 5

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    for _ in range(MAX_ATTEMPTS):
        encoded_screenshot, detr_output = take_screenshot_with_detr_in_mem(temp_file_path)
        person_objects = [obj for obj in detr_output if obj['label'] == 'person']
        if person_objects:
            highest_confidence = max(person_objects, key=lambda x: x['confidence'])
            extracted_mask = extract_and_save_masked_area(encoded_screenshot, highest_confidence['box'])
            os.remove(temp_file_path)
            return {
                "screenshot": encoded_screenshot,
                "extracted_mask": extracted_mask,
                "detr_output": detr_output
            }
    
    os.remove(temp_file_path)
    raise HTTPException(status_code=404, detail="no objects detected")

def take_screenshot_with_detr_in_mem(file_path: str):
    duration = get_movie_duration(file_path)
    screenshot_time = random.uniform(0, duration - 1)
    image_data = take_screenshot(file_path, screenshot_time)
    image = Image.open(BytesIO(image_data))
    detr_output = detectObjects(image)
    encoded_screenshot = base64.b64encode(image_data).decode('utf-8')
    return encoded_screenshot, detr_output