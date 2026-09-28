"""Synthetic local SQLite service; no network or real customer/payment data."""


def initialize(db):
    db.executescript("""
        CREATE TABLE orders (id TEXT PRIMARY KEY);
        CREATE TABLE balances (id INTEGER PRIMARY KEY, amount INTEGER NOT NULL);
        INSERT INTO balances VALUES (1, 0);
        CREATE TABLE processed (event_id TEXT PRIMARY KEY);
    """)


def place_order(db, order_id, publish):
    with db:
        db.execute("INSERT INTO orders VALUES (?)", (order_id,))
    publish({"event_id": order_id, "type": "order.created"})


def credit(db, event_id, amount, after_commit=lambda: None):
    if db.execute("SELECT 1 FROM processed WHERE event_id = ?", (event_id,)).fetchone():
        return
    with db:
        db.execute("UPDATE balances SET amount = amount + ? WHERE id = 1", (amount,))
    after_commit()
    with db:
        db.execute("INSERT INTO processed VALUES (?)", (event_id,))
