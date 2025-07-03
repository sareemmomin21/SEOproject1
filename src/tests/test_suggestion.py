import builtins
import pytest

# we import seoproject.py by path; adjust if you renamed the folder to a valid module name
import runpy

@pytest.fixture(autouse=True)
def stub_everything(monkeypatch):
    # stub out all external dependencies before module load
    monkeypatch.setenv("DB_NAME", "")
    monkeypatch.setenv("DB_USER", "")
    monkeypatch.setenv("DB_PASSWORD", "")
    monkeypatch.setenv("DB_HOST", "")
    monkeypatch.setenv("DB_PORT", "")

    # stub the API handlers
    monkeypatch.setattr(
        "src.api_handlers.food_facts_api.get_food_fact_from_barcode",
        lambda code: {"product_name": "X", "brands": "B", "ingredients": "I"}
    )
    monkeypatch.setattr(
        "src.api_handlers.food_facts_api.search_alternative_products",
        lambda **kw: [{"product_name": "Y", "code": "999", "nutriments": {"energy-kcal": 10}}]
    )

    # stub the database
    monkeypatch.setattr(
        "src.database.database.insert_scan",
        lambda **kw: 1
    )
    monkeypatch.setattr(
        "src.database.database.insert_alternative",
        lambda **kw: None
    )

def test_cli_happy_path(monkeypatch, capsys, tmp_path):
    # feed inputs: barcode, dietary filters, allergy filters, skip budget
    seq = iter(["000", "1", "", ""])
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(seq))

    # execute the script in its own namespace
    runpy.run_path(
        str(tmp_path.parent / "healthy-foodswap-cli" / "seoproject.py"),
        run_name="__main__"
    )

    out = capsys.readouterr().out
    assert "Welcome to the Healthy Food Swap CLI" in out
    assert "Alternative Product: Y" in out
    assert "Alternative Barcode: 999" in out
