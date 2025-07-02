import sys
import os

# Add the root project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api_handlers.food_facts_api import get_food_fact_from_barcode, search_alternative_products
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

    # Show numbered dietary options
    print("\nAvailable Dietary Filters:")
    for idx, option in enumerate(dietary_options, start=1):
        print(f"{idx}. {option}")
    dietary_input = input("\nEnter dietary filter numbers (comma-separated): ")
    dietary_filters = [dietary_options[int(i.strip()) - 1] for i in dietary_input.split(",") if i.strip().isdigit() and 1 <= int(i.strip()) <= len(dietary_options)]

    # Show numbered allergy options
    print("\nCommon Allergy Filters:")
    for idx, option in enumerate(allergy_options, start=1):
        print(f"{idx}. {option}")
    allergy_input = input("Enter allergy filter numbers (comma-separated): ")
    allergy_filters = [allergy_options[int(i.strip()) - 1] for i in allergy_input.split(",") if i.strip().isdigit() and 1 <= int(i.strip()) <= len(allergy_options)]


    while True:
        try:
            budget_input = input("Enter your budget limit (e.g. 5.99): ").strip()
            if not budget_input:
                print("⚠️ Budget cannot be empty. Please try again.")
                continue
            budget_limit = float(budget_input)
            if budget_limit <= 0:
                print("⚠️ Please enter a budget greater than 0.")
                continue
            break
        except ValueError:
            print("⚠️ Invalid input. Please enter a number like 4.99.")


    # Step 5: Insert the scan into the database
    scan_id = insert_scan(
        method="barcode",
        input_value=barcode,
        dietary_filters=[f.strip() for f in dietary_filters if f.strip()],
        allergy_filters=[f.strip() for f in allergy_filters if f.strip()],
        budget_limit=budget_limit
    )

    # Step 6: Insert a dummy alternative (placeholder)
    # Step 6: Search for real alternative
    alternatives = search_alternative_products(
        product_name=product["product_name"],
        dietary_filters=dietary_filters,
        allergy_filters=allergy_filters,
        max_price=budget_limit
    )

    if alternatives:
        alt = alternatives[0]  # Just take the first valid match
        insert_alternative(
            scan_id=scan_id,
            product_name=alt.get("product_name", "Unknown"),
            nutrition_info=alt.get("nutriments", {}),
            estimated_cost=budget_limit * 0.9,
            ai_insight="Recommended based on your filters.",
            user_rating="pending"
        )
        print("\n✅ Real alternative found and stored!")
        print("Alternative Product:", alt.get("product_name"))
    else:
        print("\n⚠️ No suitable alternatives found.")


if __name__ == "__main__":
    main()
