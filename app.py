from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("expenses.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/", methods=["GET", "POST"])
def home():
    connection = get_db_connection()
    error = ""

    if request.method == "POST":
        action = request.form["action"]

        if action == "add":
            transaction_type = request.form["type"]
            category = request.form["category"]
            amount = float(request.form["amount"])
            description = request.form["description"]
            date = request.form["date"]

            if transaction_type not in ["income", "expense"]:
                error = "Invalid transaction type"

            elif amount <= 0:
                error = "Amount must be greater than 0"

            else:
                connection.execute("""
                    INSERT INTO transactions
                    (type, category, amount, description, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (transaction_type, category, amount, description, date))

                connection.commit()

        elif action == "delete":
            transaction_id = request.form["id"]

            connection.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )

            connection.commit()

    filter_type = request.args.get("type", "all")

    if filter_type == "income":
        transactions = connection.execute("""
            SELECT * FROM transactions
            WHERE type = 'income'
            ORDER BY date DESC, id DESC
        """).fetchall()

    elif filter_type == "expense":
        transactions = connection.execute("""
            SELECT * FROM transactions
            WHERE type = 'expense'
            ORDER BY date DESC, id DESC
        """).fetchall()

    else:
        transactions = connection.execute("""
            SELECT * FROM transactions
            ORDER BY date DESC, id DESC
        """).fetchall()

    total_income = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'income'
    """).fetchone()[0]

    total_expenses = connection.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense'
    """).fetchone()[0]

    balance = total_income - total_expenses

    category_totals = connection.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    connection.close()

    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        filter_type=filter_type,
        category_totals=category_totals,
        error=error
    )

@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit(transaction_id):
    connection = get_db_connection()
    error = ""

    transaction = connection.execute(
        "SELECT * FROM transactions WHERE id = ?",
        (transaction_id,)
    ).fetchone()

    if transaction is None:
        connection.close()
        return "Transaction not found"

    if request.method == "POST":
        transaction_type = request.form["type"]
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date = request.form["date"]

        if transaction_type not in ["income", "expense"]:
            error = "Invalid transaction type"

        elif amount <= 0:
            error = "Amount must be greater than 0"

        else:
            connection.execute("""
                UPDATE transactions
                SET type = ?, category = ?, amount = ?, description = ?, date = ?
                WHERE id = ?
            """, (
                transaction_type,
                category,
                amount,
                description,
                date,
                transaction_id
            ))

            connection.commit()
            connection.close()

            return redirect("/")

    connection.close()

    return render_template(
        "edit.html",
        transaction=transaction,
        error=error
    )


if __name__ == "__main__":
    app.run()