import pytest
import requests
from src.api_handlers.food_facts_api import get_food_fact_from_barcode, build_search_query, search_alternative_products

class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json

def test_get_food_fact_success(monkeypatch):
    # simulate a 200 + status=1 payload
    payload = {
        "status": 1,
        "product": {
            "product_name": "Test Product",
            "brands": "BrandX",
            "ingredients_text": "Water, Sugar"
        }
    }
    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(200, payload))

    result = get_food_fact_from_barcode("000")
    assert result == {
        "product_name": "Test Product",
        "brands": "BrandX",
        "ingredients": "Water, Sugar"
    }

def test_get_food_fact_not_found(monkeypatch):
    # simulate 200 + status=0
    payload = {"status": 0}
    monkeypatch.setattr(requests, "get", lambda url: DummyResponse(200, payload))

    result = get_food_fact_from_barcode("999")
    assert "error" in result and result["error"] == "Product not found."

def test_build_search_query_keywords():
    name = "Organic Rainbow Veggie Pack"
    # After removing stopwords, we still have at least 2 keywords
    q = build_search_query(name, categories=[])
    # should pick first up to 3 meaningful words
    assert "organic" not in q  # stopword
    assert "rainbow" in q
    assert "veggie" in q

def test_search_alternative_products_filters(monkeypatch):
    # fake a search.pl response with two products
    fake = [
        {"product_name": "Bar", "ingredients_text": "Bar is vegan", "labels_tags": [], "categories_tags": [], "code": "123"},
        {"product_name": "Foo", "ingredients_text": "Foo has nuts", "labels_tags": [], "categories_tags": [], "code": "456"}
    ]
    monkeypatch.setattr(
        requests, "get",
        lambda url, params: DummyResponse(200, {"products": fake})
    )
    # only vegan filter, so the second product (with "nuts") gets score -1 -> dropped
    res = search_alternative_products("Bar", ["vegan"], ["nuts"], max_price=None)
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0]["product_name"] == "Bar"
