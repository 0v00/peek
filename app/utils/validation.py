from fastapi import UploadFile, HTTPException
from PIL import Image
from io import BytesIO

async def validate_image(image_stream: BytesIO):
    try:
        Image.open(image_stream).verify()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")