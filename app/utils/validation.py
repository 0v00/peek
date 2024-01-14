from fastapi import UploadFile, HTTPException
from PIL import Image
from io import BytesIO
import subprocess
import os

async def validate_image(image_stream: BytesIO):
    try:
        Image.open(image_stream).verify()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

async def validate_video(temp_file_path):
    try:
        result = subprocess.run(
            ["ffprobe", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        if result.returncode != 0:
            os.remove(temp_file_path)
            raise ValueError("Invalid video file")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid video file: {str(e)}")
