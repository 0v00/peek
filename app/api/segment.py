from fastapi import APIRouter, HTTPException, Form, UploadFile
from ..image_processing.detr_resnet_101 import detectObjects
from ..image_processing.segment_images import overlay_with_mask, extract_and_save_obj
from ..utils.validation import validate_image
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

def process_image_with_detr(file_stream):
    image_stream = BytesIO(file_stream)
    image = Image.open(image_stream)
    detr_output = detectObjects(image)
    encoded_image = base64.b64encode(file_stream).decode('utf-8')
    return encoded_image, detr_output