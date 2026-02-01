def validate_transaction(tx, utxo_manager, mempool):
    seen_inputs = set()
    input_sum = 0.0
    output_sum = 0.0

    # 1. Validate inputs
    for inp in tx["inputs"]:
        key = (inp["prev_tx"], inp["index"])

        # Same UTXO twice in same transaction
        if key in seen_inputs:
            return False, "Double spending in same transaction"

        # UTXO must exist
        if not utxo_manager.exists(inp["prev_tx"], inp["index"]):
            return False, f"UTXO {inp['prev_tx']}:{inp['index']} does not exist"

        # UTXO already used in mempool
        if key in mempool.spent_utxos:
            return False, f"UTXO {inp['prev_tx']}:{inp['index']} already spent in mempool"

        utxo = utxo_manager.utxo_set[key]

        # Ownership check
        if utxo["owner"] != inp["owner"]:
            return False, "UTXO owner mismatch"

        seen_inputs.add(key)
        input_sum += utxo["amount"]

    # 2. Validate outputs
    for out in tx["outputs"]:
        if out["amount"] < 0:
            return False, "Negative output amount"
        output_sum += out["amount"]

    # 3. Balance check
    if input_sum < output_sum:
        return False, "Insufficient funds"

    fee = input_sum - output_sum
    return True, f"Transaction valid. Fee = {fee}"