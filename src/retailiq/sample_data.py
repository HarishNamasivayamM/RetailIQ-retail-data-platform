"""Deterministic synthetic retail data for local demos and tests.

The generated data is explicitly synthetic. It is useful for demonstrating the
pipeline without distributing a large third-party dataset or any personal data.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterator

from retailiq.validation.schema import EXPECTED_COLUMNS

_MONEY = Decimal("0.01")

PRODUCTS = (
    ("P001", "Laptop Pro 14", "Electronics", "Computers", Decimal("1299.00"), Decimal("0.82")),
    ("P002", "Wireless Headphones", "Electronics", "Audio", Decimal("189.00"), Decimal("0.78")),
    ("P003", "4K Monitor", "Electronics", "Computers", Decimal("429.00"), Decimal("0.80")),
    ("P004", "Smartphone X", "Electronics", "Mobile", Decimal("899.00"), Decimal("0.84")),
    ("P005", "Smartwatch", "Electronics", "Wearables", Decimal("249.00"), Decimal("0.76")),
    (
        "P006",
        "Mechanical Keyboard",
        "Electronics",
        "Accessories",
        Decimal("119.00"),
        Decimal("0.65"),
    ),
    ("P007", "USB-C Dock", "Electronics", "Accessories", Decimal("149.00"), Decimal("0.66")),
    ("P008", "Portable SSD", "Electronics", "Storage", Decimal("139.00"), Decimal("0.70")),
    ("P009", "Coffee Maker", "Home", "Kitchen", Decimal("129.00"), Decimal("0.50")),
    ("P010", "Air Purifier", "Home", "Appliances", Decimal("249.00"), Decimal("0.56")),
    ("P011", "Desk Lamp", "Home", "Lighting", Decimal("59.00"), Decimal("0.42")),
    ("P012", "Bedding Set", "Home", "Bedroom", Decimal("89.00"), Decimal("0.48")),
    ("P013", "Nonstick Cookware", "Home", "Kitchen", Decimal("149.00"), Decimal("0.52")),
    ("P014", "Storage Organizer", "Home", "Organization", Decimal("34.00"), Decimal("0.38")),
    ("P015", "Robot Vacuum", "Home", "Appliances", Decimal("399.00"), Decimal("0.62")),
    ("P016", "Everyday Sneakers", "Apparel", "Footwear", Decimal("89.00"), Decimal("0.45")),
    ("P017", "Performance Jacket", "Apparel", "Outerwear", Decimal("139.00"), Decimal("0.49")),
    ("P018", "Denim Jeans", "Apparel", "Clothing", Decimal("79.00"), Decimal("0.44")),
    ("P019", "Cotton T-Shirt", "Apparel", "Clothing", Decimal("29.00"), Decimal("0.36")),
    ("P020", "Travel Backpack", "Apparel", "Accessories", Decimal("99.00"), Decimal("0.47")),
    ("P021", "Running Shorts", "Apparel", "Activewear", Decimal("39.00"), Decimal("0.40")),
    ("P022", "Organic Coffee", "Grocery", "Beverages", Decimal("16.00"), Decimal("0.70")),
    ("P023", "Snack Variety Box", "Grocery", "Snacks", Decimal("24.00"), Decimal("0.73")),
    ("P024", "Olive Oil", "Grocery", "Pantry", Decimal("19.00"), Decimal("0.69")),
    ("P025", "Sparkling Water", "Grocery", "Beverages", Decimal("8.00"), Decimal("0.62")),
    ("P026", "Protein Bars", "Grocery", "Snacks", Decimal("14.00"), Decimal("0.71")),
    ("P027", "Pasta Bundle", "Grocery", "Pantry", Decimal("12.00"), Decimal("0.66")),
)

STORES = (
    ("S001", "Chicago"),
    ("S002", "Dallas"),
    ("S003", "Denver"),
    ("S004", "Atlanta"),
    ("S005", "Seattle"),
    ("S006", "Boston"),
    ("S007", "Phoenix"),
    ("S008", "Minneapolis"),
)

PAYMENT_METHODS = ("Credit Card", "Debit Card", "Digital Wallet", "Bank Transfer")
CUSTOMER_SEGMENTS = ("Loyal", "Regular", "Occasional", "New")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_MONEY, rounding=ROUND_HALF_UP)


def generate_transactions(rows: int = 100_000, seed: int = 42) -> Iterator[dict[str, str]]:
    """Yield deterministic transaction-line records for a given row count and seed."""

    if rows < 1:
        raise ValueError("rows must be positive")
    rng = random.Random(seed)
    start_date = date(2024, 1, 1)
    days = 731  # Includes leap day and ends on 2025-12-31.

    customers = [f"C{i:05d}" for i in range(1, 2001)]
    customer_segments = {
        customer: rng.choices(CUSTOMER_SEGMENTS, weights=(18, 42, 28, 12), k=1)[0]
        for customer in customers
    }
    product_weights = [
        9 if product[2] == "Electronics" else 7 if product[2] == "Home" else 5
        for product in PRODUCTS
    ]

    for sequence in range(1, rows + 1):
        product_id, product_name, category, subcategory, base_price, cost_ratio = rng.choices(
            PRODUCTS, weights=product_weights, k=1
        )[0]
        customer_id = rng.choices(
            customers, weights=[3 if customer_segments[c] == "Loyal" else 1 for c in customers], k=1
        )[0]
        store_id, store_location = rng.choice(STORES)
        transaction_date = start_date + timedelta(days=rng.randrange(days))
        quantity = rng.choices((1, 2, 3, 4), weights=(58, 27, 10, 5), k=1)[0]
        price_multiplier = Decimal(str(round(rng.uniform(0.92, 1.08), 4)))
        unit_price = _money(base_price * price_multiplier)
        base_discount = {
            "Electronics": Decimal("0.08"),
            "Home": Decimal("0.06"),
            "Apparel": Decimal("0.14"),
            "Grocery": Decimal("0.03"),
        }[category]
        discount = min(
            Decimal("0.30"), _money(base_discount + Decimal(str(round(rng.uniform(0, 0.08), 4))))
        )
        sales_amount = _money(Decimal(quantity) * unit_price * (Decimal("1") - discount))
        cost = _money(Decimal(quantity) * unit_price * cost_ratio)
        profit = _money(sales_amount - cost)
        yield {
            "transaction_id": f"TXN-{sequence:07d}",
            "transaction_date": transaction_date.isoformat(),
            "customer_id": customer_id,
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "subcategory": subcategory,
            "quantity": str(quantity),
            "unit_price": f"{unit_price:.2f}",
            "discount": f"{discount:.2f}",
            "sales_amount": f"{sales_amount:.2f}",
            "cost": f"{cost:.2f}",
            "profit": f"{profit:.2f}",
            "store_id": store_id,
            "store_location": store_location,
            "payment_method": rng.choice(PAYMENT_METHODS),
            "customer_segment": customer_segments[customer_id],
        }


def write_transactions(path: Path, rows: int = 100_000, seed: int = 42) -> None:
    """Write generated transactions to a CSV file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EXPECTED_COLUMNS))
        writer.writeheader()
        writer.writerows(generate_transactions(rows=rows, seed=seed))
