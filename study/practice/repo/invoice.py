from discount import apply_discount


def total(prices, code=None):
    subtotal = sum(prices)
    if code:
        subtotal = apply_discount(subtotal, code)
    return round(subtotal, 2)
