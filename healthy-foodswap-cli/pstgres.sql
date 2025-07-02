-- Table to log scanned food items
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    method TEXT NOT NULL,             -- 'barcode' or 'image'
    input TEXT NOT NULL,              -- barcode number or image path
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dietary_filters TEXT[],           -- array of filters (e.g., ['vegan', 'halal'])
    allergy_filters TEXT[],           -- array of allergies
    budget_limit NUMERIC              -- budget user sets (e.g., 5.99)
);

-- Table for suggested healthier alternatives
CREATE TABLE IF NOT EXISTS alternatives (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    nutrition_info JSONB,             -- store calories, fat, protein etc.
    estimated_cost NUMERIC,
    ai_insight TEXT,                  -- GenAI tip
    user_rating TEXT                  -- e.g., 'thumbs_up' or 'thumbs_down'
);
