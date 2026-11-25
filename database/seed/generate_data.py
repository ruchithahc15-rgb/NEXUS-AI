
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy import text

from database.config import engine

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

random.seed(42)
Faker.seed(42)
fake = Faker("en_IN")

CUSTOMER_COUNT = 500
PRODUCT_COUNT = 50
TICKET_COUNT = 1000

MONTHLY_ORDERS = {
    "2025-11": 400,
    "2025-12": 400,
    "2026-01": 400,
    "2026-02": 400,
    "2026-03": 400,
    "2026-04": 400,
    "2026-05": 400,
    "2026-06": 400,
    "2026-07": 400,
    "2026-08": 400,
    "2026-09": 650,
    "2026-10": 350,
}

REGIONS = {
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Kochi"],
    "North": ["Delhi", "Jaipur", "Lucknow", "Chandigarh"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat"],
    "East": ["Kolkata", "Bhubaneswar", "Patna", "Ranchi"],
}

PRODUCT_TYPES = [
    ("Laptop", "Electronics", 55000, 95000),
    ("Smartphone", "Electronics", 15000, 75000),
    ("Headphones", "Accessories", 1000, 12000),
    ("Smartwatch", "Accessories", 2000, 18000),
    ("Tablet", "Electronics", 12000, 45000),
]


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def generate_month_dates(month, count):
    year, month_number = map(int, month.split("-"))
    start = datetime(year, month_number, 1)

    if month_number == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month_number + 1, 1)

    days = (end - start).days

    return [
        start + timedelta(
            days=random.randrange(days),
            hours=random.randrange(8, 21),
            minutes=random.randrange(60)
        )
        for _ in range(count)
    ]


# --------------------------------------------------
# 2. GENERATE CUSTOMERS
# --------------------------------------------------

def generate_data():
    print("Generating NEXUS AI enterprise data...")

    customers = []

    for i in range(CUSTOMER_COUNT):
        region = random.choice(list(REGIONS.keys()))

        customers.append({
            "full_name": fake.name(),
            "email": f"customer{i + 1}@example.com",
            "city": random.choice(REGIONS[region]),
            "region": region,
            "registration_date": fake.date_between(
                start_date=date(2024, 1, 1),
                end_date=date(2025, 10, 31)
            ),
        })

    # --------------------------------------------------
    # 3. GENERATE PRODUCTS
    # --------------------------------------------------

    products = []

    for i in range(PRODUCT_COUNT):
        name, category, low, high = random.choice(PRODUCT_TYPES)

        products.append({
            "product_name": f"{name} Model {i + 1}",
            "category": category,
            "price": money(random.randint(low, high)),
            "stock_quantity": random.randint(5, 500),
        })

    # --------------------------------------------------
    # 4. GENERATE ORDERS AND RELATED RECORDS
    # --------------------------------------------------

    order_dates = []

    for month, count in MONTHLY_ORDERS.items():
        order_dates.extend(generate_month_dates(month, count))

    random.shuffle(order_dates)

    orders = []
    order_items = []
    sales = []
    payments = []

    failed_order_ids = []
    order_customer_ids = {}

    accessory_ids = [
        i + 1 for i, product in enumerate(products)
        if product["category"] == "Accessories"
    ]

    order_id = 1

    for order_date in order_dates:

        customer_id = random.randint(1, CUSTOMER_COUNT)
        customer_region = customers[customer_id - 1]["region"]

        is_october = (
            order_date.year == 2026 and order_date.month == 10
        )

        # Higher payment failure rate in October.
        failure_rate = 0.25 if is_october else 0.05
        payment_failed = random.random() < failure_rate

        # October purchases are deliberately lower-value.
        if is_october:
            item_count = 1
            selected_products = [random.choice(accessory_ids)]
        else:
            item_count = random.randint(1, 3)
            selected_products = [
                random.randint(1, PRODUCT_COUNT)
                for _ in range(item_count)
            ]

        total = Decimal("0.00")

        for product_id in selected_products:
            product = products[product_id - 1]

            quantity = 1 if is_october else random.randint(1, 3)

            unit_price = product["price"]
            subtotal = money(unit_price * quantity)
            total += subtotal

            order_items.append({
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        total = money(total)

        status = "pending" if payment_failed else random.choices(
            ["completed", "processing"],
            weights=[85, 15]
        )[0]

        orders.append({
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "total_amount": total,
        })

        order_customer_ids[order_id] = customer_id

        payments.append({
            "order_id": order_id,
            "payment_method": random.choice([
                "UPI",
                "Credit Card",
                "Debit Card",
                "Net Banking"
            ]),
            "amount": total,
            "payment_status": "failed" if payment_failed else "success",
            "transaction_date": order_date,
        })

        if payment_failed:
            failed_order_ids.append(order_id)
        else:
            sales.append({
                "order_id": order_id,
                "sale_date": order_date,
                "revenue": total,
                "region": customer_region,
            })

        order_id += 1

    # --------------------------------------------------
    # 5. GENERATE SUPPORT TICKETS
    # --------------------------------------------------

    tickets = []

    # Guarantee 150 unresolved payment complaints
    # linked to orders with failed payments.

    if len(failed_order_ids) < 150:
        raise ValueError(
            "Not enough failed payments to create required tickets."
        )

    for failed_order_id in random.sample(failed_order_ids, 150):
        customer_id = order_customer_ids[failed_order_id]
        order_date = orders[failed_order_id - 1]["order_date"]

        created_at = order_date + timedelta(
            days=random.randint(0, 5)
        )

        tickets.append({
            "customer_id": customer_id,
            "order_id": failed_order_id,
            "issue_type": "Payment Failure",
            "priority": random.choice(["High", "Critical"]),
            "status": "open",
            "created_at": created_at,
            "resolved_at": None,
        })

    # Generate the remaining 850 tickets.

    other_issue_types = [
        "Late Delivery",
        "Product Defect",
        "Refund Request",
        "Order Cancellation",
    ]

    for _ in range(TICKET_COUNT - 150):

        order_id = random.randint(1, len(orders))
        customer_id = order_customer_ids[order_id]
        order_date = orders[order_id - 1]["order_date"]

        created_at = order_date + timedelta(
            days=random.randint(0, 5)
        )

        unresolved = random.random() < 0.30

        tickets.append({
            "customer_id": customer_id,
            "order_id": order_id,
            "issue_type": random.choice(other_issue_types),
            "priority": random.choice([
                "Low", "Medium", "High", "Critical"
            ]),
            "status": "open" if unresolved else "resolved",
            "created_at": created_at,
            "resolved_at": None if unresolved else
                created_at + timedelta(days=random.randint(1, 10)),
        })

    # --------------------------------------------------
    # 6. INSERT DATA INTO POSTGRESQL
    # --------------------------------------------------

    print("Inserting records into PostgreSQL...")

    with engine.begin() as conn:

        # WARNING: Clears existing records in these tables.
        conn.execute(text("""
            TRUNCATE TABLE
                support_tickets,
                payments,
                sales,
                order_items,
                orders,
                products,
                customers
            RESTART IDENTITY CASCADE
        """))

        conn.execute(text("""
            INSERT INTO customers
            (full_name, email, city, region, registration_date)
            VALUES
            (:full_name, :email, :city, :region, :registration_date)
        """), customers)

        conn.execute(text("""
            INSERT INTO products
            (product_name, category, price, stock_quantity)
            VALUES
            (:product_name, :category, :price, :stock_quantity)
        """), products)

        conn.execute(text("""
            INSERT INTO orders
            (customer_id, order_date, status, total_amount)
            VALUES
            (:customer_id, :order_date, :status, :total_amount)
        """), orders)

        conn.execute(text("""
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price, subtotal)
            VALUES
            (:order_id, :product_id, :quantity, :unit_price, :subtotal)
        """), order_items)

        conn.execute(text("""
            INSERT INTO sales
            (order_id, sale_date, revenue, region)
            VALUES
            (:order_id, :sale_date, :revenue, :region)
        """), sales)

        conn.execute(text("""
            INSERT INTO payments
            (order_id, payment_method, amount,
             payment_status, transaction_date)
            VALUES
            (:order_id, :payment_method, :amount,
             :payment_status, :transaction_date)
        """), payments)

        conn.execute(text("""
            INSERT INTO support_tickets
            (customer_id, order_id, issue_type, priority,
             status, created_at, resolved_at)
            VALUES
            (:customer_id, :order_id, :issue_type, :priority,
             :status, :created_at, :resolved_at)
        """), tickets)

    # --------------------------------------------------
    # 7. SUMMARY
    # --------------------------------------------------

    print("\n========== DATA GENERATION COMPLETED ==========")
    print(f"Customers:      {len(customers)}")
    print(f"Products:       {len(products)}")
    print(f"Orders:         {len(orders)}")
    print(f"Order Items:    {len(order_items)}")
    print(f"Sales:          {len(sales)}")
    print(f"Payments:       {len(payments)}")
    print(f"Failed Payments:{len(failed_order_ids)}")
    print(f"Support Tickets:{len(tickets)}")
    print("Guaranteed unresolved payment tickets: 150")
    print("===============================================")


if __name__ == "__main__":
    generate_data()
