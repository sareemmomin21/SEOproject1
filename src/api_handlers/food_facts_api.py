import requests

def get_food_fact_from_barcode(barcode):
    url =  f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1:
            product = data["product"]
            return {
                "product_name": product.get("product_name", "Unknown"),
                "brands": product.get("brands", {}),
                "ingredients": product.get("ingredients_text", "N/A")
            }
        else:
            return {"error": "Product not found."}
    else:
        return {"error": "API request failed."}


