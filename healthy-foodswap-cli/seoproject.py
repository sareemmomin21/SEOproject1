import sys
import os

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_handlers.food_facts_api import get_food_fact_from_barcode
from src.database.database import insert_scan, insert_alternative


def main():
    # Step 1: Ask user for a barcode
    print("\n" + "="*80)
    print("\nWelcome to the Healthy Food Swap CLI!\n")
    print("This tool helps you find healthier alternatives based on your dietary preferences and budget.")
    print("You can scan a product barcode to get started.\n")
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
    dietary_options = ["vegan", "vegetarian", "low-carb", "keto", "halal"]
    allergy_options = ["nuts", "gluten", "dairy", "soy", "shellfish"]

    print("\nAvailable Dietary Filters:")
    for option in dietary_options:
        print(f"- {option}")
    dietary_filters = input("\nEnter dietary filters (comma-separated): ").split(",")

    print("\nCommon Allergy Filters:")
    for option in allergy_options:
        print(f"- {option}")
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
    estimated_cost = budget_limit * 0.9
    ai_insight = "This is a placeholder suggestion."

    insert_alternative(
        scan_id=scan_id,
        product_name=product["product_name"],
        nutrition_info={"note": "Not fetched yet."},
        estimated_cost=estimated_cost,
        ai_insight=ai_insight,
        user_rating="pending"
    )

    print("\n✅ Scan and alternative successfully stored.")

    # Display the dummy alternative suggestion
    print("\n🔁 Suggested Alternative:")
    print(f"Product Name: {product['product_name']}")
    print(f"Estimated Cost: ${estimated_cost:.2f}")
    print(f"AI Insight: {ai_insight}")
    print("User Rating: pending")

if __name__ == "__main__":
    main()
