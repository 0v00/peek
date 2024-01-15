from fastapi import APIRouter, HTTPException, Form, UploadFile
from ..image_processing.detr_resnet_101 import detectObjects
from ..image_processing.segment_images import overlay_with_mask, extract_and_save_obj
from ..utils.ffmpeg_utils import take_screenshot, get_movie_duration
from ..utils.validation import validate_image, validate_video
from PIL import Image
from io import BytesIO
import random
import os
import base64
import shutil
import tempfile

router = APIRouter()

@router.post("/segment/overlay_mask")
async def overlay_mask(file: UploadFile, label: str = Form(...)):    
    file_stream = await file.read()
    image_stream = BytesIO(file_stream)
    await validate_image(image_stream)
    encoded_image, detr_output = process_image_with_detr(file_stream)
    label_objects = [obj for obj in detr_output if obj['label'] == label]
    if label_objects:
        highest_confidence = max(label_objects, key=lambda x: x['confidence'])
        image_with_mask = overlay_with_mask(encoded_image, highest_confidence['box'])
        return {
            "image_with_mask": image_with_mask,
            "detr_output": detr_output
        }
    raise HTTPException(status_code=404, detail=f"No objects of type '{label}' detected")

@router.post("/segment/extract_obj_with_label")
async def extract_obj_with_label(file: UploadFile, label: str = Form(...)):
    file_stream = await file.read()
    image_stream = BytesIO(file_stream)
    await validate_image(image_stream)
    encoded_image, detr_output = process_image_with_detr(file_stream)
    label_objects = [obj for obj in detr_output if obj['label'] == label]
    if label_objects:
        highest_confidence = max(label_objects, key=lambda x: x['confidence'])
        extracted_obj = extract_and_save_obj(encoded_image, highest_confidence['box'])
        return {
            "extracted_obj": extracted_obj,
            "detr_output": detr_output
        }
    raise HTTPException(status_code=404, detail=f"No objects of type '{label}' detected")

@router.post("/segment/extract_obj_from_video")
async def extract_obj_from_video(file: UploadFile):    
    MAX_ATTEMPTS = 5

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    await validate_video(temp_file_path)

    for _ in range(MAX_ATTEMPTS):
        encoded_screenshot, detr_output = take_screenshot_with_detr(temp_file_path)
        person_objects = [obj for obj in detr_output if obj['label'] == 'person']
        if person_objects:
            highest_confidence = max(person_objects, key=lambda x: x['confidence'])
            extracted_obj = extract_and_save_obj(encoded_screenshot, highest_confidence['box'])
            os.remove(temp_file_path)
            return {
                "screenshot": encoded_screenshot,
                "extracted_obj": extracted_obj,
                "detr_output": detr_output
            }
    
    os.remove(temp_file_path)
    raise HTTPException(status_code=404, detail="no objects detected")

def take_screenshot_with_detr(file_path: str):
    duration = get_movie_duration(file_path)
    screenshot_time = random.uniform(0, duration - 1)
    image_data = take_screenshot(file_path, screenshot_time)
    image = Image.open(BytesIO(image_data))
    detr_output = detectObjects(image)
    encoded_screenshot = base64.b64encode(image_data).decode('utf-8')
    return encoded_screenshot, detr_output

def process_image_with_detr(file_stream):
    image_stream = BytesIO(file_stream)
    image = Image.open(image_stream)
    detr_output = detectObjects(image)
    encoded_image = base64.b64encode(file_stream).decode('utf-8')
    return encoded_image, detr_output