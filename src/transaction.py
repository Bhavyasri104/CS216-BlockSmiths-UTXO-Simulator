DEFAULT_FEE = 0.001
_tx_counter = 1

def generate_tx_id(sender, receiver):
    global _tx_counter
    txid = f"tx_{sender.lower()}_{receiver.lower()}_{_tx_counter:03d}"
    _tx_counter += 1
    return txid


def create_transaction(sender, receiver, amount, utxo_manager):
    if amount <= 0:
        return None, "Invalid amount"

    utxos = utxo_manager.get_utxos_for_owner(sender)
    inputs = []
    total_input = 0.0

    for tx_id, index, utxo_amount in utxos:
        inputs.append({
            "prev_tx": tx_id,
            "index": index,
            "owner": sender
        })
        total_input += utxo_amount
        if total_input >= amount:
            break

    if total_input < amount:
        return None, "Insufficient funds"

    if total_input == amount:
        fee = 0.0
    else:
        fee = DEFAULT_FEE
        if total_input < amount + fee:
            return None, "Insufficient funds"

    outputs = [{"amount": amount, "address": receiver}]

    change = round(total_input - amount - fee, 8)
    if change > 0:
        outputs.append({"amount": change, "address": sender})

    tx = {
        "tx_id": generate_tx_id(sender, receiver),
        "inputs": inputs,
        "outputs": outputs
    }

    return tx, f"Transaction valid ! Fee : {fee} BTC"
