CREATE TABLE IF NOT EXISTS transactions (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date TEXT,
    unit_price REAL,
    customer_id REAL,
    country TEXT,
    is_cancellation INTEGER,
    revenue REAL,
    year INTEGER,
    month INTEGER,
    year_month TEXT,
    day_of_week TEXT,
    hour INTEGER,
    has_customer_id INTEGER
);