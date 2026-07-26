## Total revenue ##
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue
FROM transactions
WHERE is_cancellation = 0;

##Total number of invoices
SELECT
    COUNT(DISTINCT invoice_no) AS total_invoices
FROM transactions
WHERE is_cancellation = 0;

##Number of identified customers
SELECT
    COUNT(DISTINCT customer_id) AS total_customers
FROM transactions
WHERE customer_id IS NOT NULL
  AND is_cancellation = 0;

## Average ordervalue
WITH invoice_totals AS (
    SELECT
        invoice_no,
        SUM(revenue) AS order_revenue
    FROM transactions
    WHERE is_cancellation = 0
    GROUP BY invoice_no
)
SELECT
    ROUND(AVG(order_revenue), 2) AS average_order_value
FROM invoice_totals;

##Monthly revenue
SELECT
    year_month,
    ROUND(SUM(revenue), 2) AS monthly_revenue
FROM transactions
WHERE is_cancellation = 0
GROUP BY year_month
ORDER BY year_month;

##Top products by revenue
SELECT
    description,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM transactions
WHERE is_cancellation = 0
GROUP BY description
ORDER BY total_revenue DESC
LIMIT 10;

##Top products by quantity sold
SELECT
    description,
    SUM(quantity) AS total_quantity
FROM transactions
WHERE is_cancellation = 0
GROUP BY description
ORDER BY total_quantity DESC
LIMIT 10;

##Revenue share by product
WITH product_revenue AS (
    SELECT
        description,
        SUM(revenue) AS total_revenue
    FROM transactions
    WHERE is_cancellation = 0
    GROUP BY description
)
SELECT
    description,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(
        100.0 * total_revenue / SUM(total_revenue) OVER (),
        2
    ) AS revenue_share_pct
FROM product_revenue
ORDER BY total_revenue DESC
LIMIT 10;

##Top customers by revenue
SELECT
    customer_id,
    ROUND(SUM(revenue), 2) AS customer_revenue
FROM transactions
WHERE customer_id IS NOT NULL
  AND is_cancellation = 0
GROUP BY customer_id
ORDER BY customer_revenue DESC
LIMIT 10;

##Orders per customer
SELECT
    customer_id,
    COUNT(DISTINCT invoice_no) AS number_of_orders
FROM transactions
WHERE customer_id IS NOT NULL
  AND is_cancellation = 0
GROUP BY customer_id
ORDER BY number_of_orders DESC
LIMIT 10;


##Repeat versus one-time customers
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS order_count
    FROM transactions
    WHERE customer_id IS NOT NULL
      AND is_cancellation = 0
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time customer'
        ELSE 'Repeat customer'
    END AS customer_type,
    COUNT(*) AS number_of_customers
FROM customer_orders
GROUP BY customer_type;

##Revenue by country
SELECT
    country,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM transactions
WHERE is_cancellation = 0
GROUP BY country
ORDER BY total_revenue DESC;

##Average order value by country
WITH country_orders AS (
    SELECT
        country,
        invoice_no,
        SUM(revenue) AS order_revenue
    FROM transactions
    WHERE is_cancellation = 0
    GROUP BY country, invoice_no
)
SELECT
    country,
    ROUND(AVG(order_revenue), 2) AS average_order_value
FROM country_orders
GROUP BY country
ORDER BY average_order_value DESC;

##Cancellation rate
SELECT
    ROUND(
        100.0 * COUNT(DISTINCT CASE
            WHEN is_cancellation = 1 THEN invoice_no
        END)
        / COUNT(DISTINCT invoice_no),
        2
    ) AS cancellation_rate_pct
FROM transactions;

##Value of cancelled transactions
SELECT
    ROUND(ABS(SUM(revenue)), 2) AS cancelled_value
FROM transactions
WHERE is_cancellation = 1;

##One advanced query

Add a month-over-month growth query using LAG.

WITH monthly_revenue AS (
    SELECT
        year_month,
        SUM(revenue) AS revenue
    FROM transactions
    WHERE is_cancellation = 0
    GROUP BY year_month
),
monthly_comparison AS (
    SELECT
        year_month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY year_month
        ) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    year_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / previous_month_revenue,
        2
    ) AS growth_pct
FROM monthly_comparison;


"Observation:
The United Kingdom generates the majority of total revenue.

Possible explanation:
The company is based in the UK and may have stronger local brand recognition.

Business action:
The retailer could study high-value international markets for expansion.

Limitation:
Revenue concentration does not automatically mean international markets are unprofitable."