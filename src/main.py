from utxo_manager import UTXOManager
from transaction import create_transaction
from mempool import Mempool
from validator import validate_transaction
from block import mine_block

def initialize_genesis_utxos(utxo_manager):
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_manager.add_utxo("genesis", 3, 10.0, "David")
    utxo_manager.add_utxo("genesis", 4, 5.0, "Eve")

def print_utxo_set(utxo_manager):
    print("\n--- Current UTXO Set ---")
    for (tx_id, index), utxo in utxo_manager.utxo_set.items():
        print(f"{tx_id}:{index} -> {utxo['amount']} BTC -> {utxo['owner']}")
    print("-----------------------")

def print_transaction(tx):
    print("\n--- Transaction Created ---")
    print("Transaction ID:", tx["tx_id"])
    print("Inputs:")
    for inp in tx["inputs"]:
        print(f"  {inp['prev_tx']}:{inp['index']} owned by {inp['owner']}")
    print("Outputs:")
    for out in tx["outputs"]:
        print(f"  {out['amount']} BTC -> {out['address']}")
    print("---------------------------")

def print_initial_utxos():
    print("\nInitial UTXOs (Genesis Block):")
    print("- Alice : 50.0 BTC")
    print("- Bob : 30.0 BTC")
    print("- Charlie : 20.0 BTC")
    print("- David : 10.0 BTC")
    print("- Eve : 5.0 BTC")

def print_mempool(mempool):
    print("\n--- Mempool ---")
    if not mempool.transactions:
        print("Mempool is empty.")
    else:
        for i, tx in enumerate(mempool.transactions, 1):
            print(f"{i}. TXID: {tx['tx_id']} | Inputs: {[f'{inp['prev_tx']}:{inp['index']}' for inp in tx['inputs']]} | Outputs: {[f'{out['amount']} BTC -> {out['address']}' for out in tx['outputs']]}")
    print("----------------")

def test_double_spend_same_tx(utxo_manager, mempool):
    print("\nTest 3: Double-Spend in Same Transaction")
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
    if not valid:
        print("REJECTED as expected:", msg)
    else:
        print("❌ ERROR: Double-spend in same transaction not detected!")

def test_zero_fee_transaction(utxo_manager, mempool, sender="Bob", receiver="Alice", amount=30.0):
    print("\nTest 7: Zero Fee Transaction")
    fee = 0.0
    tx, msg = create_transaction(sender, receiver, amount, utxo_manager, mempool, fee)
    if tx is None:
        print(f"❌ ERROR: Transaction creation failed for {sender} → {receiver} with {amount} BTC:", msg)
        return
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    if valid:
        ok, add_msg = mempool.add_transaction(tx, utxo_manager)
        if ok:
            print(f"ACCEPTED as expected for {sender} → {receiver} with {amount} BTC: {message}")
            print_transaction(tx)
        else:
            print("❌ ERROR: Transaction not added to mempool:", add_msg)
    else:
        print(f"❌ ERROR: Test failed for {sender} → {receiver} with {amount} BTC -", message)

def test_multiple_inputs(utxo_manager, mempool):
    print("\nTest 2: Multiple inputs")

    tx = {
        "tx_id": "tx_multi",
        "inputs": [
            {"prev_tx": "genesis", "index": 0, "owner": "Alice"},
            {"prev_tx": "genesis", "index": 5, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": 60, "address": "Bob"},
            {"amount": 15, "address": "Alice"}
        ]
    }

    valid, msg = validate_transaction(tx, utxo_manager, mempool)

    if valid:
        print("ACCEPTED as expected:", msg)
    else:
        print("❌ ERROR: Test failed -", msg)

def test_multiple_inputs_transaction(utxo_manager, mempool):
    print("\nTest 2: Multiple Inputs Transaction")
    # Give Alice an extra UTXO for this test
    utxo_manager.add_utxo("genesis", 6, 20.0, "Alice")
    sender = "Alice"
    receiver = "Bob"
    amount = 60.0
    fee = 0.002
    # Alice has (genesis, 0): 50.0 and (genesis, 6): 20.0
    # She spends both to send 60 BTC to Bob, gets change
    tx, msg = create_transaction(sender, receiver, amount, utxo_manager, mempool, fee)
    if tx is None:
        print("❌ ERROR: Transaction creation failed:", msg)
        return
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    if not valid:
        print("❌ ERROR: Transaction validation failed:", message)
        return
    ok, add_msg = mempool.add_transaction(tx, utxo_manager)
    if ok:
        print("Transaction valid!", message)
        print(f"Transaction ID: {tx['tx_id']}")
        print("Transaction added to mempool.")
        print_transaction(tx)
        # Check outputs
        for out in tx["outputs"]:
            if out["address"] == sender:
                print(f"Change output: {out['amount']} BTC back to {sender}")
            elif out["address"] == receiver:
                print(f"Payment output: {out['amount']} BTC to {receiver}")
        print(f"Fee: {fee} BTC")
    else:
        print("❌ ERROR: Transaction not added to mempool:", add_msg)

def test_unconfirmed_chain(utxo_manager, mempool):
    print("\nTest 10: Unconfirmed Chain")
    # Reset UTXOs for a clean test
    utxo_manager.utxo_set.clear()
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    # TX1: Alice → Bob
    tx1, _ = create_transaction("Alice", "Bob", 10.0, utxo_manager, mempool, 0.001)
    valid1, msg1 = validate_transaction(tx1, utxo_manager, mempool)
    if valid1:
        mempool.add_transaction(tx1, utxo_manager)
        print(f"TX1 accepted: Alice → Bob (creates new UTXO for Bob)")
    else:
        print(f"❌ ERROR: TX1 rejected: {msg1}")
        return
    # TX2: Bob tries to spend the new UTXO before TX1 is mined
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
    if valid2:
        print("TX2 accepted: Bob can spend unconfirmed UTXO (your design allows unconfirmed chain).")
    else:
        print(f"TX2 rejected: {msg2} (your design does not allow unconfirmed chain)")

def test_simple_double_spend(utxo_manager, mempool):
    print("\nTest: Simple double-spend detection")
    # Spend the same UTXO in two different transactions
    tx1 = {
        "tx_id": "tx_ds1",
        "inputs": [
            {"prev_tx": "genesis", "index": 1, "owner": "Bob"}
        ],
        "outputs": [
            {"amount": 20, "address": "Alice"},
            {"amount": 10, "address": "Bob"}
        ]
    }
    tx2 = {
        "tx_id": "tx_ds2",
        "inputs": [
            {"prev_tx": "genesis", "index": 1, "owner": "Bob"}
        ],
        "outputs": [
            {"amount": 30, "address": "Charlie"}
        ]
    }
    valid1, msg1 = validate_transaction(tx1, utxo_manager, mempool)
    if valid1:
        mempool.add_transaction(tx1, utxo_manager)
        print("First spend accepted.")
    else:
        print("❌ ERROR: First spend rejected:", msg1)
    valid2, msg2 = validate_transaction(tx2, utxo_manager, mempool)
    if not valid2:
        print("Second spend correctly rejected:", msg2)
    else:
        print("❌ ERROR: Double-spend not detected!")

def test_mempool_conflict(utxo_manager, mempool):
    print("\nTest: Mempool conflict prevention")
    # Add a transaction to mempool, then try to add a conflicting one
    tx1 = {
        "tx_id": "tx_conflict1",
        "inputs": [
            {"prev_tx": "genesis", "index": 2, "owner": "Charlie"}
        ],
        "outputs": [
            {"amount": 20, "address": "Alice"}
        ]
    }
    tx2 = {
        "tx_id": "tx_conflict2",
        "inputs": [
            {"prev_tx": "genesis", "index": 2, "owner": "Charlie"}
        ],
        "outputs": [
            {"amount": 20, "address": "Bob"}
        ]
    }
    ok1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    if ok1:
        print("First tx added to mempool.")
    else:
        print("❌ ERROR: First tx rejected:", msg1)
    ok2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    if not ok2:
        print("Second conflicting tx correctly rejected:", msg2)
    else:
        print("❌ ERROR: Conflict not detected!")

def test_race_attack_first_seen(utxo_manager, mempool, sender="David", receiver1="Merchant", receiver2="Attacker", amount=10.0):
    print("\nTest 8: Race Attack (first-seen rule)")
    # Low-fee merchant TX arrives first
    tx1, _ = create_transaction(sender, receiver1, amount, utxo_manager, mempool, fee=0.001)
    # High-fee attack TX arrives second (same input, higher fee)
    # Manually construct to ensure same input, higher fee
    utxos = utxo_manager.get_utxos_for_owner(sender)
    if not utxos:
        print("❌ ERROR: No UTXO available for race attack test.")
        return
    txid, idx, _ = utxos[0]
    tx2 = {
        "tx_id": "tx_attack",
        "inputs": [
            {"prev_tx": txid, "index": idx, "owner": sender}
        ],
        "outputs": [
            {"amount": amount - 0.005, "address": receiver2}  # Higher fee
        ]
    }
    ok1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    ok2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    if ok1 and not ok2:
        print(f"First-seen (merchant, low-fee) tx accepted: {sender} → {receiver1}, second (attacker, high-fee) rejected as expected.")
    elif ok2:
        print("❌ ERROR: High-fee attack tx was incorrectly accepted!")
    else:
        print("❌ ERROR: Race attack not handled correctly!")

def test_basic_valid_transaction(utxo_manager, mempool, sender="Alice", receiver="Bob", amount=10.0, fee=0.001):
    print("\nTest 1: Basic Valid Transaction")
    tx, msg = create_transaction(sender, receiver, amount, utxo_manager, mempool, fee)
    if tx is None:
        print(f"❌ ERROR: Transaction creation failed for {sender} → {receiver} with {amount} BTC:", msg)
        return
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    if not valid:
        print(f"❌ ERROR: Transaction validation failed for {sender} → {receiver} with {amount} BTC:", message)
        return
    ok, add_msg = mempool.add_transaction(tx, utxo_manager)
    if ok:
        print("Transaction valid!", message)
        print(f"Transaction ID: {tx['tx_id']}")
        print("Transaction added to mempool.")
        print_transaction(tx)
        for out in tx["outputs"]:
            if out["address"] == sender:
                print(f"Change output: {out['amount']} BTC back to {sender}")
            elif out["address"] == receiver:
                print(f"Payment output: {out['amount']} BTC to {receiver}")
        print(f"Fee: {fee} BTC")
    else:
        print("❌ ERROR: Transaction not added to mempool:", add_msg)

def test_mempool_double_spend(utxo_manager, mempool):
    print("\nTest 4: Mempool Double-Spend")
    # Reset Alice's UTXO for this test
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
    if ok1:
        print("TX1 accepted: Alice → Bob (spends UTXO)")
    else:
        print("❌ ERROR: TX1 rejected:", msg1)
    ok2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    if not ok2:
        print("TX2 correctly rejected: Alice → Charlie (same UTXO)")
        print("Reason:", msg2)
    else:
        print("❌ ERROR: TX2 (double-spend) was incorrectly accepted!")

def test_insufficient_funds(utxo_manager, mempool, sender="Bob", receiver="Alice", amount=35.0, fee=0.001):
    print("\nTest 5: Insufficient Funds")
    tx, msg = create_transaction(sender, receiver, amount, utxo_manager, mempool, fee)
    if tx is None:
        print(f"REJECTED as expected for {sender} → {receiver} with {amount} BTC:", msg)
        return
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    if not valid and "Insufficient funds" in message:
        print(f"REJECTED as expected for {sender} → {receiver} with {amount} BTC:", message)
    else:
        print("❌ ERROR: Insufficient funds not detected!")

def test_negative_output_amount(utxo_manager, mempool, sender="Alice", receiver="Bob", amount=-5.0, fee=0.001):
    print("\nTest 6: Negative Output Amount")
    # Manually construct a transaction with negative output
    tx = {
        "tx_id": "tx_negative_amt",
        "inputs": [
            {"prev_tx": "genesis", "index": 0, "owner": sender}
        ],
        "outputs": [
            {"amount": amount, "address": receiver}
        ]
    }
    valid, message = validate_transaction(tx, utxo_manager, mempool)
    if not valid and "Negative output amount" in message:
        print(f"REJECTED as expected for {sender} → {receiver} with {amount} BTC:", message)
    else:
        print("❌ ERROR: Negative output not detected!")

def test_complete_mining_flow(utxo_manager, mempool):
    print("\nTest 9: Complete Mining Flow")
    # Reset UTXOs for a clean test
    utxo_manager.utxo_set.clear()
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    # Add multiple transactions
    tx1, _ = create_transaction("Alice", "Bob", 10.0, utxo_manager, mempool, 0.001)
    tx2, _ = create_transaction("Bob", "Charlie", 5.0, utxo_manager, mempool, 0.002)
    tx3, _ = create_transaction("Charlie", "Alice", 7.0, utxo_manager, mempool, 0.003)
    for tx in [tx1, tx2, tx3]:
        valid, msg = validate_transaction(tx, utxo_manager, mempool)
        if valid:
            mempool.add_transaction(tx, utxo_manager)
            print(f"Added TX: {tx['tx_id']}")
        else:
            print(f"❌ ERROR: Could not add TX: {msg}")
    print(f"Mempool size before mining: {len(mempool.transactions)}")
    print("Mining block...")
    miner = "Miner1"
    mine_block(miner, mempool, utxo_manager)
    print(f"Mempool size after mining: {len(mempool.transactions)}")
    print_utxo_set(utxo_manager)
    print(f"Miner {miner} balance: {utxo_manager.get_balance(miner)} BTC")

def run_test_scenarios(utxo_manager, mempool):
    print("\nSelect test scenario:")
    print("1. Basic valid transaction")
    print("2. Multiple inputs transaction")
    print("3. Double-spend in same transaction")
    print("4. Mempool double-spend")
    print("5. Insufficient funds")
    print("6. Negative output amount")
    print("7. Zero fee transaction")
    print("8. Race attack (first-seen rule)")
    print("9. Complete mining flow")
    print("10. Unconfirmed chain")
    print("11. Simple double-spend detection")
    print("12. Mempool conflict prevention")
    print("13. All tests")
    choice = input("Enter scenario number: ")
    mempool.clear()
    if choice == "10":
        test_unconfirmed_chain(utxo_manager, mempool)
    else:
        if choice == "1":
            sender = input("Sender: ") or "Alice"
            receiver = input("Receiver: ") or "Bob"
            amount = float(input("Amount: ") or 10.0)
            fee = float(input("Fee: ") or 0.001)
            test_basic_valid_transaction(utxo_manager, mempool, sender, receiver, amount, fee)
        elif choice == "2":
            test_multiple_inputs_transaction(utxo_manager, mempool)
        elif choice == "3":
            test_double_spend_same_tx(utxo_manager, mempool)
        elif choice == "4":
            test_mempool_double_spend(utxo_manager, mempool)
        elif choice == "5":
            sender = input("Sender: ") or "Bob"
            receiver = input("Receiver: ") or "Alice"
            amount = float(input("Amount: ") or 35.0)
            fee = float(input("Fee: ") or 0.001)
            test_insufficient_funds(utxo_manager, mempool, sender, receiver, amount, fee)
        elif choice == "6":
            sender = input("Sender: ") or "Alice"
            receiver = input("Receiver: ") or "Bob"
            amount = float(input("Amount (should be negative): ") or -5.0)
            fee = float(input("Fee: ") or 0.001)
            test_negative_output_amount(utxo_manager, mempool, sender, receiver, amount, fee)
        elif choice == "7":
            sender = input("Sender: ") or "Bob"
            receiver = input("Receiver: ") or "Alice"
            amount = float(input("Amount: ") or 30.0)
            test_zero_fee_transaction(utxo_manager, mempool, sender, receiver, amount)
        elif choice == "8":
            sender = input("Sender: ") or "David"
            receiver1 = input("First receiver: ") or "Merchant"
            receiver2 = input("Second receiver: ") or "Attacker"
            amount = float(input("Amount: ") or 10.0)
            test_race_attack_first_seen(utxo_manager, mempool, sender, receiver1, receiver2, amount)
        elif choice == "9":
            test_complete_mining_flow(utxo_manager, mempool)
        elif choice == "11":
            test_simple_double_spend(utxo_manager, mempool)
        elif choice == "12":
            test_mempool_conflict(utxo_manager, mempool)
        elif choice == "13":
            test_basic_valid_transaction(utxo_manager, mempool)
            mempool.clear()
            test_multiple_inputs_transaction(utxo_manager, mempool)
            mempool.clear()
            test_double_spend_same_tx(utxo_manager, mempool)
            mempool.clear()
            test_mempool_double_spend(utxo_manager, mempool)
            mempool.clear()
            test_insufficient_funds(utxo_manager, mempool)
            mempool.clear()
            test_negative_output_amount(utxo_manager, mempool)
            mempool.clear()
            test_zero_fee_transaction(utxo_manager, mempool)
            mempool.clear()
            test_race_attack_first_seen(utxo_manager, mempool)
            mempool.clear()
            test_complete_mining_flow(utxo_manager, mempool)
            mempool.clear()
            test_unconfirmed_chain(utxo_manager, mempool)
            mempool.clear()
            test_simple_double_spend(utxo_manager, mempool)
            mempool.clear()
            test_mempool_conflict(utxo_manager, mempool)
            mempool.clear()
        else:
            print("Invalid scenario.")

def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    initialize_genesis_utxos(utxo_manager)
    print("\n=== Bitcoin Transaction Simulator ===")
    print_initial_utxos()
    while True:
        print("\nMain Menu:")
        print("1. Create new transaction")
        print("2. View UTXO set")
        print("3. View mempool")
        print("4. Mine block")
        print("5. Run test scenarios")
        print("6. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            sender = input("Enter sender: ")
            balance = utxo_manager.get_balance(sender)
            print(f"Available balance: {balance} BTC")
            receiver = input("Enter recipient: ")
            try:
                amount = float(input("Enter amount: "))
                if amount < 0:
                    print("Error: Amount must be non-negative")
                    continue
            except ValueError:
                print("Error: Invalid amount")
                continue
            default_fee = 0.0 if balance == amount else 0.0001
            fee = default_fee
            print(f"\nCreating transaction with fee {fee} ...")
            # --- Multi-UTXO selection logic ---
            utxos = utxo_manager.get_utxos_for_owner(sender)
            # Exclude UTXOs already spent in mempool
            spent = set()
            for tx in mempool.transactions:
                for inp in tx["inputs"]:
                    spent.add((inp["prev_tx"], inp["index"]))
            available_utxos = [(txid, idx, amt) for (txid, idx, amt) in utxos if (txid, idx) not in spent]
            available_utxos.sort(key=lambda x: x[2], reverse=True)  # Prefer largest first
            selected = []
            total = 0.0
            for utxo in available_utxos:
                selected.append(utxo)
                total += utxo[2]
                if total >= amount + fee:
                    break
            # Check if the sum of all UTXOs (regardless of mempool) is insufficient
            total_all_utxos = sum(amt for (txid, idx, amt) in utxos)
            if total_all_utxos < amount + fee:
                print(f"Error: Insufficient funds. Total available: {total_all_utxos} BTC, required: {amount + fee} BTC.")
                continue
            if total < amount + fee:
                # Find which UTXOs are blocked by mempool
                blocked_utxos = [(txid, idx, amt) for (txid, idx, amt) in utxos if (txid, idx) in spent]
                if blocked_utxos:
                    print("Transaction rejected: The following UTXOs are already spent in mempool and cannot be used:")
                    for txid, idx, amt in blocked_utxos:
                        print(f"  UTXO {txid}:{idx} ({amt} BTC)")
                else:
                    print(f"Error: Insufficient available funds to cover {amount + fee} BTC.")
                continue
            # Build transaction inputs
            inputs = [{"prev_tx": txid, "index": idx, "owner": sender} for (txid, idx, amt) in selected]
            outputs = [{"amount": amount, "address": receiver}]
            change = total - amount - fee
            if change > 0:
                outputs.append({"amount": change, "address": sender})
            import time, random
            tx_id = f"tx_{int(time.time())}_{random.randint(1000,9999)}"
            tx = {"tx_id": tx_id, "inputs": inputs, "outputs": outputs}
            valid, message = validate_transaction(tx, utxo_manager, mempool)
            if not valid:
                print("Transaction rejected:", message)
            else:
                ok, add_msg = mempool.add_transaction(tx, utxo_manager)
                if ok:
                    print(f"Transaction valid! {message}")
                    print(f"Transaction ID: {tx['tx_id']}")
                    print("Transaction added to mempool.")
                    print(f"Mempool now has {len(mempool.transactions)} transactions.")
                    print_transaction(tx)
                else:
                    print("Error adding to mempool:", add_msg)
        elif choice == "2":
            print_utxo_set(utxo_manager)
        elif choice == "3":
            print_mempool(mempool)
        elif choice == "4":
            miner = input("Enter miner name: ")
            mine_block(miner, mempool, utxo_manager)
        elif choice == "5":
            run_test_scenarios(utxo_manager, mempool)
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()

