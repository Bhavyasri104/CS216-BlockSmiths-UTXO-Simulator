def validate_transaction(tx, utxo_manager):
    seen = set()
    total_in = 0.0
    total_out = 0.0

    for inp in tx["inputs"]:
        ref = (inp["prev_tx"], inp["index"])

        if ref in seen:
            return False, "Double-spend in same transaction"

        if not utxo_manager.exists(*ref):
            return False, "UTXO does not exist"

        utxo = utxo_manager.utxo_set[ref]
        total_in += utxo["amount"]
        seen.add(ref)

    for out in tx["outputs"]:
        if out["amount"] < 0:
            return False, "Negative output amount"
        total_out += out["amount"]

    if total_out > total_in:
        return False, "Outputs exceed inputs"

    return True, "Valid"
