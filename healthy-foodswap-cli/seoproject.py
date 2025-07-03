import sys
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env next to this script
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path)

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_handlers.food_facts_api import (
    get_food_fact_from_barcode,
    search_alternative_products
)
from src.database.database import insert_scan, insert_alternative


def main():
    # Step 1: Ask user for a barcode
    print("\n" + "="*80)
    print("\nWelcome to the Healthy Food Swap CLI!\n")
    print("This tool helps you find healthier alternatives based on your dietary preferences and budget.")
    print("You can scan a product barcode to get started.\n")
    barcode = input("Enter a barcode to scan: ").strip()

    # Step 2: Call the OpenFoodFacts API for basic info
    product = get_food_fact_from_barcode(barcode)

    # Step 3: Check if the product was found
    if "error" in product:
        print("Error:", product["error"])
        return

    # Fetch full product data to grab nutriments for comparison
    full_resp = requests.get(
        f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    )
    full_data = full_resp.json().get("product", {})
    orig_nutri = full_data.get("nutriments", {})

    print("\nFetched Product Info:")
    print(product)

    # Step 4: Collect user preferences
    dietary_options = ["vegan", "vegetarian", "low-carb", "keto", "halal"]
    allergy_options = ["nuts", "gluten", "dairy", "soy", "shellfish"]

    print("\nAvailable Dietary Filters:")
    for idx, option in enumerate(dietary_options, start=1):
        print(f"{idx}. {option}")
    dietary_input = input("\nEnter dietary filter numbers (comma-separated): ")
    dietary_filters = [
        dietary_options[int(i.strip()) - 1]
        for i in dietary_input.split(",")
        if i.strip().isdigit() and 1 <= int(i.strip()) <= len(dietary_options)
    ]

    print("\nCommon Allergy Filters:")
    for idx, option in enumerate(allergy_options, start=1):
        print(f"{idx}. {option}")
    allergy_input = input("Enter allergy filter numbers (comma-separated): ")
    allergy_filters = [
        allergy_options[int(i.strip()) - 1]
        for i in allergy_input.split(",")
        if i.strip().isdigit() and 1 <= int(i.strip()) <= len(allergy_options)
    ]

    # Step 5: Optional budget — user can press Enter to skip
    budget_input = input("\nEnter your budget limit (e.g. 5.99) [press Enter to skip]: ").strip()
    if budget_input:
        while True:
            try:
                budget_limit = float(budget_input)
                if budget_limit <= 0:
                    raise ValueError
                break
            except ValueError:
                budget_input = input("⚠️ Invalid. Enter a positive number (or Enter to skip): ").strip()
                if not budget_input:
                    budget_limit = None
                    break
    else:
        budget_limit = None

    # Step 6: Insert the scan into the database
    scan_id = insert_scan(
        method="barcode",
        input_value=barcode,
        dietary_filters=dietary_filters,
        allergy_filters=allergy_filters,
        budget_limit=budget_limit,
    )

    # Step 7: Search for real alternatives
    alternatives = search_alternative_products(
        product_name=product["product_name"],
        dietary_filters=dietary_filters,
        allergy_filters=allergy_filters,
        max_price=budget_limit
    )

    if alternatives:
        alt = alternatives[0]
        alt_nutri = alt.get("nutriments", {})

        insert_alternative(
            scan_id=scan_id,
            product_name=alt.get("product_name", "Unknown"),
            nutrition_info=alt_nutri,
            estimated_cost=None if budget_limit is None else round(budget_limit * 0.9, 2),
            ai_insight="Recommended based on your filters.",
            user_rating="pending"
        )

        print("\n✅ Real alternative found and stored!")
        print("Alternative Product:", alt.get("product_name"))
        print("Alternative Barcode:", alt.get("code", "N/A"))

        # --- Nutrition comparison per 100g with arrow ---
        metrics = {
            "Calories": ("energy-kcal", "kcal"),
            "Sugar": ("sugars_100g", "g"),
            "Protein": ("proteins_100g", "g"),
            "Fat": ("fat_100g", "g"),
            "Carbohydrates": ("carbohydrates_100g", "g"),
        }
        print("\nNutrition comparison (per 100g):")
        for label, (key, unit) in metrics.items():
            o = orig_nutri.get(key)
            a = alt_nutri.get(key)
            if o is not None and a is not None:
                # always show higher→lower
                hi, lo = (o, a) if o >= a else (a, o)
                print(f" • {label}: {hi} {unit} → {lo} {unit}")

        # Short explanation of why it's better
        reasons = []
        if dietary_filters:
            reasons.append(f"Matches your {' & '.join(dietary_filters)} diet")
        if allergy_filters:
            reasons.append(f"avoids {', '.join(allergy_filters)}")
        if budget_limit is not None:
            reasons.append(f"fits within your budget of ${budget_limit:.2f}")
        explanation = " and ".join(reasons) if reasons else "is a great choice!"
        print("\nWhy it's better:\n", explanation)

    else:
        print("\n⚠️ No suitable alternatives found.")

if __name__ == "__main__":
    main()

# Barcode ex: 737628064502
# Barcode ex: 10600425
# 
#
