# Retail Performance Analytics

## Business problem

An online retailer wants to better understand its commercial performance.

The project will analyze transactional data to answer questions about revenue,
customers, products, countries, sales trends and cancellations.

## Main business questions

1. How does revenue change over time?
2. Which products generate the most revenue?
3. Which countries generate the most sales?
4. Which customers are the most valuable?
5. What percentage of customers make repeat purchases?
6. How much revenue is affected by cancellations?
7. Which products have unusually high cancellation rates?

## Planned solution

The project will combine:

- Python and Pandas for data preparation
- SQL for business analysis
- Streamlit for an interactive dashboard
- Git and GitHub for version control and documentation

## Data-cleaning decisions

- Exact duplicate rows were removed to avoid double-counting.
- Missing customer IDs were retained because the rows remain useful for sales analysis.
- Missing product descriptions were replaced with `Unknown product`.
- Rows with invalid dates, quantities or prices were stored separately.
- Zero and negative prices were excluded from the main analytical dataset.
- Negative quantities were retained because they may represent cancellations or returns.
- Cancellations were identified using invoice numbers beginning with `C`.

## SQL analysis

The cleaned transactional data is loaded into a local SQLite database.

The SQL analysis includes:

- total revenue and average order value;
- monthly performance;
- top products;
- customer value;
- repeat-customer analysis;
- country performance;
- cancellations;
- month-over-month growth.

The main SQL queries are available in:

`sql/business_queries.sql`