import psycopg2
from psycopg2.extras import Json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root .env file
dotenv_path = Path(__file__).resolve().parents[2] / "healthy-foodswap-cli" / ".env"
load_dotenv(dotenv_path=dotenv_path)

def connect_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def insert_scan(method, input_value, dietary_filters, allergy_filters, budget_limit):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO scans (method, input, dietary_filters, allergy_filters, budget_limit)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (method, input_value, dietary_filters, allergy_filters, budget_limit))
    scan_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return scan_id

def insert_alternative(scan_id, product_name, nutrition_info, estimated_cost, ai_insight, user_rating):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO alternatives (scan_id, product_name, nutrition_info, estimated_cost, ai_insight, user_rating)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (scan_id, product_name, Json(nutrition_info), estimated_cost, ai_insight, user_rating))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # Test run — insert dummy data
    scan_id = insert_scan(
        method="barcode",
        input_value="123456789012",
        dietary_filters=["vegan"],
        allergy_filters=["nuts"],
        budget_limit=4.99
    )
    print(f"Inserted scan with ID: {scan_id}")

    insert_alternative(
        scan_id=scan_id,
        product_name="Healthy Bar",
        nutrition_info={"calories": 150, "protein": 5},
        estimated_cost=3.50,
        ai_insight="Better protein and lower sugar.",
        user_rating="thumbs_up"
    )
    print("Inserted alternative.")
