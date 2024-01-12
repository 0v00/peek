from fastapi import FastAPI
from .api.segment import router as segment_router

app = FastAPI()
app.include_router(segment_router)