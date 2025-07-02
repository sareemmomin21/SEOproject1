import requests
import re

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

# Utility to build a good search query from name + categories
def build_search_query(name, categories):
    # Common words to ignore
    stopwords = {
        "the","and","with","includes","contains","kit","pack","extra","natural",
        "organic","flavored","flavour","flavor","new"
    }

    # 1) Tokenize and lowercase
    words = re.findall(r'\w+', name.lower())

    # 2) Filter out stopwords and digits-only tokens
    keywords = [w for w in words if w not in stopwords and not w.isdigit()]

    # 3) If we have at least 2 keywords, use up to three of them
    if len(keywords) >= 2:
        return " ".join(keywords[:3])

    # 4) Else fallback to first category tag (if any)
    if categories:
        # categories look like ["en:breakfast-cereals", …]
        cats = [c.split(":",1)[1] for c in categories if ":" in c]
        if cats:
            return cats[0].replace("-", " ")

    # 5) Otherwise just return whatever keywords we have
    return " ".join(keywords)

def search_alternative_products(product_name, dietary_filters, allergy_filters, max_price):
    # Assume `categories_tags` is a list of tags from the API
    # e.g. product.get("categories_tags", [])
    from src.api_handlers.food_facts_api import get_food_fact_from_barcode  # if needed

    # Build our smart query
    # You’d pass in the original product dict instead
    # but here we accept name + categories separately
    query = build_search_query(
        name=product_name,
        categories=[]  # replace with product.get("categories_tags", [])
    )

    response = requests.get(
        "https://world.openfoodfacts.org/cgi/search.pl",
        params={
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 20
        }
    )
    if response.status_code != 200:
        return []

    products = response.json().get("products", [])
    results = []
    for prod in products:
        text = " ".join([
            prod.get("product_name",""),
            prod.get("ingredients_text",""),
            " ".join(prod.get("labels_tags", [])),
            " ".join(prod.get("categories_tags", []))
        ]).lower()

        # Loosely filter — allow neutral or positive matches
        score = 0
        for df in dietary_filters:
            if df.lower() in text:
                score += 1
        for af in allergy_filters:
            if af.lower() in text:
                score -= 1

        # Price filtering can go here if you have price data
        if score >= 0:
            results.append(prod)

    return results

if __name__ == "__main__":
    test_barcode = "737628064502" 
    result = get_food_fact_from_barcode(test_barcode)
    print(result)