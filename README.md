# peek
( ͡° ͜ʖ ͡°)	

Playing around with [segment-anything](https://github.com/facebookresearch/segment-anything), [detr-resnet-101](https://huggingface.co/facebook/detr-resnet-101), FastAPI, and FFmpeg.

A single endpoint to upload a video - in return, you get a screenshot with a single mask applied to it, as well as the original screenshot, and detr resnet output. You'll need ffmpeg installed, and a [model checkpoint](https://github.com/facebookresearch/segment-anything#model-checkpoints) placed in the root dir.

This example uses a [forked version of segment-anything](https://github.com/0v00/segment-anything) (with a single, minor change) to get this working with MPS.

1. `uvicorn app.main:app --reload`
2. make a POST request:
```bash
curl -X POST "http://localhost:8000/segment/upload/single_prediction" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/some/video" \
     | jq -r '.screenshot + " " + .prediction' \
     | (read screenshot prediction; echo $screenshot | base64 --decode > screenshot.jpg; echo $prediction | base64 --decode > prediction.jpg)
```
3. enjoy the screenshot. print it out. frame it.


### Single Prediction

- **Endpoint**: `POST /segment/upload/single_prediction`
- **Description**: Retrieves a random screenshot from the movie specified by the given movie_id. Performs object detection and single prediction and returns details of detected objects. This should only take a few seconds using MPS.
- **Param**: 
    - `movie_id`
- **Returns**: A JSON object containing:
    - screenshot: `base64` screenshot
    - prediction: `base64` screenshot with single mask
    - detr_output: An array of objects representing detected items in the screenshot. Each object includes the label, confidence score, and bounding box coordinates.

```json
{
  "screenshot": "base64_image_data...",
  "prediction": "base64_image_data...",
  "detr_output": [
    {
      "label": "person",
      "confidence": 0.98,
      "box": [163.98, 97.83, 550.38, 581.16]
    },
    // ... more detected objects ...
  ]
}
```

<img src="prediction.jpg" alt="single prediction mask" width="500"/>
<img src="screenshot.jpg" alt="original screenshot" width="500"/>

_*Boiling Point (1990) - Takeshi Kitano*_