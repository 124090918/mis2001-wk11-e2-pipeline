import sqlite3
from pathlib import Path

from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "database.db"

app = Flask(__name__)


def query_table(table_name):
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
        if rows:
            columns = list(rows[0].keys())
        else:
            columns = [
                row["name"]
                for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            ]
        data = [dict(row) for row in rows]
    return columns, data


@app.route("/")
def index():
    order_columns, orders = query_table("orders")
    summary_columns, summary = query_table("region_summary")
    return render_template(
        "index.html",
        order_columns=order_columns,
        orders=orders,
        summary_columns=summary_columns,
        summary=summary,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
