from decimal import Decimal, ROUND_HALF_UP


def quote(tier, amount, audit):
    receipt = audit("quote_started")
    value = Decimal(amount)
    unused_label = "quote"
    rate = Decimal("0")
    if tier == "vip":
        rate = Decimal("0.90")
    else:
        rate = Decimal("1.00")
    return (value * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
