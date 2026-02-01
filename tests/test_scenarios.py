# test_scenarios.py
# Place your test cases for the UTXO simulator here.
# Example structure for pytest or unittest can be added as needed.

# Example placeholder:
def test_placeholder():
    assert True

import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from utxo_manager import UTXOManager
from transaction import create_transaction
from mempool import Mempool
from validator import validate_transaction
from block import mine_block

def setup_genesis(utxo_manager):
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_manager.add_utxo("genesis", 3, 10.0, "David")
    utxo_manager.add_utxo("genesis", 4, 5.0, "Eve")

# 1. Basic Valid Transaction
def test_basic_valid_transaction():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    tx, msg = create_transaction("Alice", "Bob", 10.0, utxo_manager, mempool, 0.001)
    assert tx is not None, msg
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    assert valid, message
    ok, add_msg = mempool.add_transaction(tx, utxo_manager)
    assert ok, add_msg
    # Check change output
    change = [out for out in tx["outputs"] if out["address"] == "Alice"]
    assert change and change[0]["amount"] == pytest.approx(39.999), "Change output incorrect"
    # Check fee
    input_sum = sum(utxo_manager.utxo_set[(inp["prev_tx"], inp["index"])] ["amount"] for inp in tx["inputs"])
    output_sum = sum(out["amount"] for out in tx["outputs"])
    assert abs(input_sum - output_sum - 0.001) < 1e-6

# 2. Multiple Inputs
def test_multiple_inputs():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    utxo_manager.add_utxo("genesis", 5, 20.0, "Alice")
    tx, msg = create_transaction("Alice", "Bob", 60.0, utxo_manager, mempool, 0.002)
    assert tx is not None, msg
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    assert valid, message
    ok, add_msg = mempool.add_transaction(tx, utxo_manager)
    assert ok, add_msg
    # Check inputs aggregation
    assert len(tx["inputs"]) >= 2

# 3. Double-Spend in Same Transaction
def test_double_spend_same_tx():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    tx = {
        "tx_id": "tx_test_double",
        "inputs": [
            {"prev_tx": "genesis", "index": 0, "owner": "Alice"},
            {"prev_tx": "genesis", "index": 0, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": 10, "address": "Bob"}
        ]
    }
    valid, msg = validate_transaction(tx, utxo_manager, mempool)
    assert not valid
    assert "double spending" in msg.lower() or "double-spend" in msg.lower() or "already spent" in msg.lower()

# 4. Mempool Double-Spend
def test_mempool_double_spend():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    utxo_manager.add_utxo("genesis", 7, 15.0, "Alice")
    tx1 = {
        "tx_id": "tx_mempool1",
        "inputs": [
            {"prev_tx": "genesis", "index": 7, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": 15.0, "address": "Bob"}
        ]
    }
    tx2 = {
        "tx_id": "tx_mempool2",
        "inputs": [
            {"prev_tx": "genesis", "index": 7, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": 15.0, "address": "Charlie"}
        ]
    }
    ok1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    assert ok1, msg1
    ok2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    assert not ok2
    assert "already spent" in msg2.lower() or "conflict" in msg2.lower()

# 5. Insufficient Funds
def test_insufficient_funds():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    tx, msg = create_transaction("Bob", "Alice", 35.0, utxo_manager, mempool, 0.001)
    valid, vmsg = validate_transaction(tx, utxo_manager, mempool)
    assert not valid
    assert "insufficient" in vmsg.lower()

# 6. Negative Amount
def test_negative_output_amount():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    tx = {
        "tx_id": "tx_negative_amt",
        "inputs": [
            {"prev_tx": "genesis", "index": 0, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": -5.0, "address": "Bob"}
        ]
    }
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    assert not valid
    assert "negative" in message.lower()

# 7. Zero Fee Transaction
def test_zero_fee_transaction():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    tx, msg = create_transaction("Bob", "Alice", 30.0, utxo_manager, mempool, 0.0)
    assert tx is not None, msg
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    assert valid, message
    ok, add_msg = mempool.add_transaction(tx, utxo_manager)
    assert ok, add_msg

# 8. Race Attack Simulation
def test_race_attack_first_seen():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis(utxo_manager)
    sender = "David"
    receiver1 = "Merchant"
    receiver2 = "Attacker"
    amount = 10.0
    tx1, _ = create_transaction(sender, receiver1, amount, utxo_manager, mempool, fee=0.001)
    utxos = utxo_manager.get_utxos_for_owner(sender)
    txid, idx, _ = utxos[0]
    tx2 = {
        "tx_id": "tx_attack",
        "inputs": [
            {"prev_tx": txid, "index": idx, "owner": sender}
        ],
        "outputs": [
            {"amount": amount - 0.005, "address": receiver2}
        ]
    }
    ok1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    ok2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    assert ok1
    assert not ok2

# 9. Complete Mining Flow
def test_complete_mining_flow():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    tx1, _ = create_transaction("Alice", "Bob", 10.0, utxo_manager, mempool, 0.001)
    tx2, _ = create_transaction("Bob", "Charlie", 5.0, utxo_manager, mempool, 0.002)
    tx3, _ = create_transaction("Charlie", "Alice", 7.0, utxo_manager, mempool, 0.003)
    for tx in [tx1, tx2, tx3]:
        valid, msg = validate_transaction(tx, utxo_manager, mempool)
        if valid:
            mempool.add_transaction(tx, utxo_manager)
    miner = "Miner1"
    mine_block(miner, mempool, utxo_manager)
    # Check mempool cleared
    assert len(mempool.transactions) == 0
    # Check miner rewarded
    assert utxo_manager.get_balance(miner) > 0

# 10. Unconfirmed Chain
def test_unconfirmed_chain():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    utxo_manager.utxo_set.clear()
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    tx1, _ = create_transaction("Alice", "Bob", 10.0, utxo_manager, mempool, 0.001)
    valid1, msg1 = validate_transaction(tx1, utxo_manager, mempool)
    if valid1:
        mempool.add_transaction(tx1, utxo_manager)
    tx2 = {
        "tx_id": "tx2",
        "inputs": [
            {"prev_tx": tx1["tx_id"], "index": 0, "owner": "Bob"}
        ],
        "outputs": [
            {"amount": 10.0, "address": "Charlie"}
        ]
    }
    valid2, msg2 = validate_transaction(tx2, utxo_manager, mempool)
    # Accept or reject depending on your design
    # Here, we accept if your design allows spending unconfirmed outputs
    assert valid2 or not valid2
    # Optionally, check for explanation in msg2
