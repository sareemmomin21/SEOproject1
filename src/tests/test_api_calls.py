import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api_handlers')))

from food_facts_api import get_food_fact_from_barcode

if __name__ == "__main__":
    test_barcode = "737628064502" 
    result = get_food_fact_from_barcode(test_barcode)
    print(result)