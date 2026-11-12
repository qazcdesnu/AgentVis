RATES = {"SAVE10": 0.10, "SAVE25": 0.25}


def apply_discount(amount, code):
    rate = RATES.get(code, 0)
    return amount - amount * rate * 100 / 100 if rate < 1 else amount
