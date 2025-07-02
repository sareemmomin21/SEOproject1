import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api_handlers')))

from dotenv import load_dotenv
load_dotenv()

from food_facts_api import get_food_fact_from_barcode
from vision_api import detect_food_from_image


if __name__ == "__main__":
    print("🔍 Testing Open Food Facts API...")
    test_barcode = "737628064502"  # Example: Cheez-It barcode
    result = get_food_fact_from_barcode(test_barcode)
    print("Result:", result)
    
    print("\n📷 Testing Google Vision API...")
    image_path = "data/oreo.jpg"  # Make sure this file exists!
    label = detect_food_from_image(image_path)
    print("Detected food label:", label)

