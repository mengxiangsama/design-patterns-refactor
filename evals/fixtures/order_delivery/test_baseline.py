"""Reproduce the ORIGINAL failure windows, not acceptance tests for a fix."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from service import credit, initialize, place_order


class OriginalBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="delivery-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "state.sqlite"
        self.db = sqlite3.connect(self.path)
        self.addCleanup(self.db.close)
        initialize(self.db)

    def test_committed_order_without_published_event_survives_reopen(self):
        def publish(event):
            raise ConnectionError("broker unavailable")

        with self.assertRaises(ConnectionError):
            place_order(self.db, "order-1", publish)
        with sqlite3.connect(self.path) as reopened:
            self.assertEqual([("order-1",)], reopened.execute("SELECT id FROM orders").fetchall())
            tables = {row[0] for row in reopened.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual({"orders", "balances", "processed"}, tables)

    def test_retry_after_credit_commit_applies_credit_twice(self):
        def crash():
            raise RuntimeError("process stopped before completion")

        with self.assertRaises(RuntimeError):
            credit(self.db, "event-1", 10, crash)
        with sqlite3.connect(self.path) as reopened:
            credit(reopened, "event-1", 10)
            self.assertEqual(20, reopened.execute("SELECT amount FROM balances").fetchone()[0])


if __name__ == "__main__":
    unittest.main()
