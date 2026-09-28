from decimal import Decimal, InvalidOperation
import unittest

from quote import quote


class QuoteContractTest(unittest.TestCase):
    def test_tiers_rounding_and_fallback(self):
        for tier, amount, expected in (("vip", "10.05", "9.05"),
                                       ("regular", "10.05", "10.05"),
                                       ("new-tier", "10.05", "10.05"),
                                       ("vip", "0", "0.00")):
            calls = []
            self.assertEqual(Decimal(expected), quote(tier, amount, calls.append))
            self.assertEqual(["quote_started"], calls)

    def test_audit_happens_before_conversion_error(self):
        calls = []
        with self.assertRaises(InvalidOperation):
            quote("vip", "not-a-number", calls.append)
        self.assertEqual(["quote_started"], calls)

    def test_audit_exception_propagates(self):
        def audit(event):
            raise RuntimeError("audit unavailable")

        with self.assertRaisesRegex(RuntimeError, "audit unavailable"):
            quote("vip", "not-a-number", audit)


if __name__ == "__main__":
    unittest.main()
