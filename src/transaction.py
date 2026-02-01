import time
import random
from validator import validate_transaction

def generate_tx_id():
    return f"tx_{int(time.time())}_{random.randint(1000,9999)}"

def create_transaction(sender, receiver, amount, utxo_manager, mempool, fee=None):
    if fee is None:
        fee = 0.0

    if amount < 0:
        return None, "Amount cannot be negative"
    
    if amount == 0:
        if fee > 0:
            return None, "Cannot have fee for zero amount transaction"
        inputs = []
        outputs = [{"amount": 0, "address": receiver}]
        transaction = {
            "tx_id": generate_tx_id(),
            "inputs": inputs,
            "outputs": outputs
        }
        return transaction, "Zero amount transaction created"

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

        if total_input >= amount + fee:
            break

    outputs = [
        {"amount": amount, "address": receiver}
    ]

    change = total_input - amount - fee
    if change > 0:
        outputs.append({"amount": change, "address": sender})

    transaction = {
        "tx_id": generate_tx_id(),
        "inputs": inputs,
        "outputs": outputs
    }

    return transaction, "Transaction created"

def execute_transaction(transaction, utxo_manager):
    # Remove inputs
    for inp in transaction["inputs"]:
        utxo_manager.remove_utxo(inp["prev_tx"], inp["index"])
    
    # Add outputs
    for i, out in enumerate(transaction["outputs"]):
        utxo_manager.add_utxo(transaction["tx_id"], i, out["amount"], out["address"])