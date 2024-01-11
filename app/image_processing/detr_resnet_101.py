from transformers import DetrImageProcessor, DetrForObjectDetection
import torch

processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-101", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-101", revision="no_timm")

def detectObjects(image: bytes):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    detected_objects = []
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        detected_objects.append({
            "label": model.config.id2label[label.item()],
            "confidence": round(score.item(), 3),
            "box": [round(i, 2) for i in box.tolist()]
        })
    return detected_objects