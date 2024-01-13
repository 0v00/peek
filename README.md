# peek
( ͡° ͜ʖ ͡°)	

Playing around with [segment-anything](https://github.com/facebookresearch/segment-anything), [detr-resnet-101](https://huggingface.co/facebook/detr-resnet-101), FastAPI, and FFmpeg. Text to object segmentation (although currently I only look for objects labeled `person`), and then return a semi-transparent mask overlaid on an image, or return an extracted object with a transparent background.

You'll need ffmpeg installed, and a [model checkpoint](https://github.com/facebookresearch/segment-anything#model-checkpoints) placed in the root dir.

This example uses a [forked version of segment-anything](https://github.com/0v00/segment-anything) (with a single, minor change) to get this working with MPS.

1. `uvicorn app.main:app --reload`
2. make a POST request:
```bash
curl -X POST "http://localhost:8000/segment/upload/single_extract" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/some/video" \
     | jq -r '.screenshot + " " + .extracted_obj' \
     | (read screenshot extracted_obj; echo $screenshot | base64 --decode > screenshot.jpg; echo $prediction | base64 --decode > extracted_obj.png)
```
3. enjoy the screenshot. print it out. frame it.

### Single Extract

- **Endpoint**: `POST /segment/upload/single_extract`
- **Description**: Accepts a video and extracts a frame at random. Performs object detection and segmentation to isolate the object from the background. The segmented object is cropped and rendered with transparency in `PNG` format.
- **Returns**: A JSON object containing:
    - screenshot: `base64` encoded string of the original frame
    - extracted_mask: `base64` encoded string of the `PNG` with the extracted object
    - detr_output: An array of objects representing detected items in the screenshot. Each object includes the label, confidence score, and bounding box coordinates.

```json
{
  "screenshot": "base64_image_data...",
  "extracted_obj": "base64_image_data...",
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

<img src="extracted.png" alt="extracted prediction" width="200"/>
<img src="extracted.jpg" alt="original screenshot" width="500"/>

_*Boiling Point (1990) - Takeshi Kitano*_

### Single Prediction

- **Endpoint**: `POST /segment/upload/single_prediction`
- **Description**: Accepts a video and extracts a frame at random. Performs object detection and segmentation. This should only take a few seconds using MPS.
- **Returns**: A JSON object containing:
    - screenshot: `base64` encoded string of the original frame
    - prediction: `base64` encoded string of the frame with the segmented object overlaid with a semi-transparent mask
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