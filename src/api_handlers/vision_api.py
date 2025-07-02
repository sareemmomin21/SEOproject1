import os
from google.cloud import vision_api
from dotenv import load_dotenv
import requests
load_dotenv()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
import requests

def detect_food_from_image(img_path):
    try:
        client = vision_api.ImageAnnotatorClient()

        with open(img_path, "rb") as img_file:
            content = img_file.read()

        image = vision_api.Image(content=content)
        response = client.label_detection(image=image)
        labels = response.label_annotations

        filtered_labels = [label.description for label in labels if label.score > 0.6]

        if filtered_labels:
            return filter_labels[0]
        else:
            return "No high-confidence food label detected"
        
    except Exception as e:
        return f"Error detecting food: {e}"
