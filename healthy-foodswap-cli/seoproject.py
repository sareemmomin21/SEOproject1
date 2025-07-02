import sys
import os

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_handlers.food_facts_api import get_food_fact_from_barcode
from src.database.database import insert_scan, insert_alternative


def main():
    # Step 1: Ask user for a barcode
    barcode = input("Enter a barcode to scan: ")

    # Step 2: Call the OpenFoodFacts API
    product = get_food_fact_from_barcode(barcode)

    # Step 3: Check if the product was found
    if "error" in product:
        print("Error:", product["error"])
        return

    print("\nFetched Product Info:")
    print(product)

    # Step 4: Collect user preferences
    dietary_filters = input("Enter dietary filters (comma-separated): ").split(",")
    allergy_filters = input("Enter allergy filters (comma-separated): ").split(",")
    budget_limit = float(input("Enter your budget limit (e.g. 5.99): "))

    # Step 5: Insert the scan into the database
    scan_id = insert_scan(
        method="barcode",
        input_value=barcode,
        dietary_filters=[f.strip() for f in dietary_filters if f.strip()],
        allergy_filters=[f.strip() for f in allergy_filters if f.strip()],
        budget_limit=budget_limit
    )

    # Step 6: Insert a dummy alternative (placeholder)
    insert_alternative(
        scan_id=scan_id,
        product_name=product["product_name"],
        nutrition_info={"note": "Not fetched yet."},
        estimated_cost=budget_limit * 0.9,  # Example estimate
        ai_insight="This is a placeholder suggestion.",
        user_rating="pending"
    )

    print("\n✅ Scan and alternative successfully stored.")

if __name__ == "__main__":
    main()
