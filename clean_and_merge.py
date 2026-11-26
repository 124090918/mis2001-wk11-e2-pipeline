import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ORDER_FILE = DATA_DIR / "order.txt"
CUSTOMER_FILE = DATA_DIR / "customer.txt"
DATABASE_FILE = BASE_DIR / "database.db"

EXCHANGE_RATES = {
    "USD": 6.9,
    "EUR": 7.5,
    "CNY": 1.0,
    "JPY": 0.05,
}


def convert_to_cny(row):
    currency = row["currency"]
    if currency not in EXCHANGE_RATES:
        raise ValueError(
            f"Unknown currency '{currency}' for order {row['order_id']}; "
            f"supported currencies: {', '.join(EXCHANGE_RATES)}"
        )
    return float(row["amount"]) * EXCHANGE_RATES[currency]


def main():
    orders = pd.read_csv(ORDER_FILE)
    customers = pd.read_csv(CUSTOMER_FILE)

    orders = orders.drop_duplicates()
    customers = customers.drop_duplicates()

    orders["amount_cny"] = orders.apply(convert_to_cny, axis=1)

    merged = orders.merge(customers, on="customer_id", how="inner")

    summary = (
        merged.groupby("region", as_index=False)["amount_cny"]
        .mean()
        .rename(columns={"amount_cny": "average_amount_cny"})
    )

    with sqlite3.connect(DATABASE_FILE) as conn:
        merged.to_sql("orders", conn, if_exists="replace", index=False)
        summary.to_sql("region_summary", conn, if_exists="replace", index=False)

    print("Merged orders:")
    print(merged.to_string(index=False))
    print()
    print("Regional summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
