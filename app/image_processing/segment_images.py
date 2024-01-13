import os
import io
from PIL import Image
import base64
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_anns(anns, ax):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=lambda x: x['area'], reverse=True)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:, :, 3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)

def segment_image(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    checkpoint_path = os.path.join(os.path.dirname(__file__), '../../sam_vit_h_4b8939.pth')
    sam = sam_model_registry["vit_h"](checkpoint=checkpoint_path)
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    sam.to(device=device)

    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image)
    plt.figure(figsize=(20, 20))
    ax = plt.gca()
    show_anns(masks, ax)
    plt.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', bbox_inches='tight')
    buf.seek(0)
    base64_encoded_result = base64.b64encode(buf.read()).decode('utf-8')

    return base64_encoded_result

def predict(base64_image, coordinates):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    checkpoint_path = os.path.join(os.path.dirname(__file__), '../../sam_vit_h_4b8939.pth')
    sam = sam_model_registry["vit_h"](checkpoint=checkpoint_path)
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    sam.to(device=device)

    predictor = SamPredictor(sam)
    predictor.set_image(image)

    input_box = np.array(coordinates)

    masks, _, _ = predictor.predict(
        point_coords=None,
        point_labels=None,
        box=input_box[None, :],
        multimask_output=False,
    )

    mask = masks[0]

    fig, ax = plt.subplots()
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    show_mask(mask, ax)

    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    base64_encoded_result = base64.b64encode(buf.read()).decode('utf-8')

    return base64_encoded_result

def extract_and_save_masked_area(base64_image, coordinates):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    checkpoint_path = os.path.join(os.path.dirname(__file__), '../../sam_vit_h_4b8939.pth')
    sam = sam_model_registry["vit_h"](checkpoint=checkpoint_path)
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    sam.to(device=device)

    predictor = SamPredictor(sam)
    predictor.set_image(image)
    input_box = np.array(coordinates)

    masks, _, _ = predictor.predict(
        point_coords=None,
        point_labels=None,
        box=input_box[None, :],
        multimask_output=False,
    )

    mask = masks[0]
    mask = (mask > 0).astype(np.uint8) * 255

    unique_values = np.unique(mask)
    if set(unique_values) != {0, 255}:
        raise ValueError("Mask contains values other than 0 and 255, which is unexpected.")

    masked_image = cv2.bitwise_and(image, image, mask=mask)
    masked_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)

    alpha_channel = mask
    r, g, b = cv2.split(masked_image)
    rgba_image = cv2.merge([r, g, b, alpha_channel]) 

    final_image = Image.fromarray(rgba_image)

    crop_box = (coordinates[0], coordinates[1], coordinates[2], coordinates[3])
    cropped_image = final_image.crop(crop_box)

    output_buffer = io.BytesIO()
    cropped_image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    base64_encoded_result = base64.b64encode(output_buffer.read()).decode('utf-8')

    return base64_encoded_result