
from sqlalchemy import text

from database.config import engine


# 1. Monthly Sales Analysis
def get_monthly_sales_data():
    query = text("""
        SELECT
            TO_CHAR(sale_date, 'YYYY-MM') AS month,
            COUNT(*) AS total_sales,
            SUM(revenue) AS total_revenue,
            ROUND(AVG(revenue), 2) AS average_order_value
        FROM sales
        GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
        ORDER BY month
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        records = result.mappings().all()

    return {
        "status": "success",
        "total_months": len(records),
        "data": [
            {
                "month": row["month"],
                "total_sales": row["total_sales"],
                "total_revenue": float(row["total_revenue"]),
                "average_order_value": float(row["average_order_value"])
            }
            for row in records
        ]
    }


# 2. Revenue Comparison
def get_revenue_comparison(from_month: str, to_month: str):
    query = text("""
        SELECT
            TO_CHAR(o.order_date, 'YYYY-MM') AS month,
            COUNT(*) AS total_orders,

            COUNT(*) FILTER (
                WHERE p.payment_status = 'success'
            ) AS successful_payments,

            COUNT(*) FILTER (
                WHERE p.payment_status = 'failed'
            ) AS failed_payments,

            COALESCE(SUM(s.revenue), 0) AS total_revenue,
            COALESCE(AVG(s.revenue), 0) AS average_order_value

        FROM orders o

        JOIN payments p
            ON o.order_id = p.order_id

        LEFT JOIN sales s
            ON o.order_id = s.order_id

        WHERE TO_CHAR(o.order_date, 'YYYY-MM')
            IN (:from_month, :to_month)

        GROUP BY TO_CHAR(o.order_date, 'YYYY-MM')
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "from_month": from_month,
                "to_month": to_month
            }
        )

        records = {
            row["month"]: dict(row)
            for row in result.mappings().all()
        }

    if from_month not in records or to_month not in records:
        raise LookupError(
            "No data found for one or both selected months"
        )

    previous = records[from_month]
    current = records[to_month]

    previous_revenue = float(previous["total_revenue"])
    current_revenue = float(current["total_revenue"])

    revenue_difference = current_revenue - previous_revenue

    revenue_change_percentage = (
        (revenue_difference / previous_revenue) * 100
        if previous_revenue else None
    )

    return {
        "status": "success",
        "comparison": {
            "from_month": from_month,
            "to_month": to_month,
            "previous_revenue": previous_revenue,
            "current_revenue": current_revenue,
            "revenue_difference": revenue_difference,
            "revenue_change_percentage": round(
                revenue_change_percentage, 2
            ) if revenue_change_percentage is not None else None,
            "previous_total_orders": previous["total_orders"],
            "current_total_orders": current["total_orders"],
            "previous_failed_payments": previous["failed_payments"],
            "current_failed_payments": current["failed_payments"],
            "previous_average_order_value": float(
                previous["average_order_value"]
            ),
            "current_average_order_value": float(
                current["average_order_value"]
            )
        }
    }


# 3. Payment Failure Analysis
def get_payment_failure_analysis(month: str):
    query = text("""
        SELECT
            p.payment_method,
            COUNT(*) AS total_attempts,

            COUNT(*) FILTER (
                WHERE p.payment_status = 'success'
            ) AS successful_payments,

            COUNT(*) FILTER (
                WHERE p.payment_status = 'failed'
            ) AS failed_payments,

            ROUND(
                COUNT(*) FILTER (
                    WHERE p.payment_status = 'failed'
                ) * 100.0 / NULLIF(COUNT(*), 0),
                2
            ) AS failure_rate

        FROM payments p

        JOIN orders o
            ON p.order_id = o.order_id

        WHERE TO_CHAR(o.order_date, 'YYYY-MM') = :month

        GROUP BY p.payment_method
        ORDER BY failed_payments DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(query, {"month": month})
        records = result.mappings().all()

    if not records:
        raise LookupError(
            "No payment data found for the selected month"
        )

    return {
        "status": "success",
        "month": month,
        "total_payment_methods": len(records),
        "data": [
            {
                "payment_method": row["payment_method"],
                "total_attempts": row["total_attempts"],
                "successful_payments": row["successful_payments"],
                "failed_payments": row["failed_payments"],
                "failure_rate": float(row["failure_rate"] or 0)
            }
            for row in records
        ]
    }


# 4. Product Revenue Analysis
def get_product_revenue_analysis(
    from_month: str,
    to_month: str
):
    query = text("""
        SELECT
            TO_CHAR(s.sale_date, 'YYYY-MM') AS month,
            p.category,
            COUNT(DISTINCT s.sale_id) AS total_sales,
            SUM(oi.subtotal) AS total_revenue

        FROM sales s

        JOIN order_items oi
            ON s.order_id = oi.order_id

        JOIN products p
            ON oi.product_id = p.product_id

        WHERE TO_CHAR(s.sale_date, 'YYYY-MM')
            IN (:from_month, :to_month)

        GROUP BY
            TO_CHAR(s.sale_date, 'YYYY-MM'),
            p.category

        ORDER BY month, p.category
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "from_month": from_month,
                "to_month": to_month
            }
        )

        records = result.mappings().all()

    if not records:
        raise LookupError("No product revenue data found")

    return {
        "status": "success",
        "comparison": {
            "from_month": from_month,
            "to_month": to_month
        },
        "data": [
            {
                "month": row["month"],
                "category": row["category"],
                "total_sales": row["total_sales"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in records
        ]
    }


# 5. Regional Revenue Analysis
def get_regional_revenue_analysis(
    from_month: str,
    to_month: str
):
    query = text("""
        SELECT
            TO_CHAR(s.sale_date, 'YYYY-MM') AS month,
            c.region,
            COUNT(DISTINCT s.sale_id) AS total_sales,
            SUM(s.revenue) AS total_revenue

        FROM sales s

        JOIN orders o
            ON s.order_id = o.order_id

        JOIN customers c
            ON o.customer_id = c.customer_id

        WHERE TO_CHAR(s.sale_date, 'YYYY-MM')
            IN (:from_month, :to_month)

        GROUP BY
            TO_CHAR(s.sale_date, 'YYYY-MM'),
            c.region

        ORDER BY month, c.region
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "from_month": from_month,
                "to_month": to_month
            }
        )

        records = result.mappings().all()

    if not records:
        raise LookupError("No regional revenue data found")

    return {
        "status": "success",
        "comparison": {
            "from_month": from_month,
            "to_month": to_month
        },
        "data": [
            {
                "month": row["month"],
                "region": row["region"],
                "total_sales": row["total_sales"],
                "total_revenue": float(row["total_revenue"])
            }
            for row in records
        ]
    }
