from utxo_manager import UTXOManager
from mempool import Mempool
from transaction import create_transaction
from validator import validate_transaction
from block import mine_block

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests")))
import test_scenarios


def print_genesis():
    print("=== Bitcoin Transaction Simulator ===")
    print("Initial UTXOs ( Genesis Block ) :")
    print("- Alice : 50.0 BTC")
    print("- Bob : 30.0 BTC")
    print("- Charlie : 20.0 BTC")
    print("- David : 10.0 BTC")
    print("- Eve : 5.0 BTC\n")


def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()

    genesis = [
        ("Alice", 50.0),
        ("Bob", 30.0),
        ("Charlie", 20.0),
        ("David", 10.0),
        ("Eve", 5.0)
    ]

    for i, (name, amt) in enumerate(genesis):
        utxo_manager.add_utxo("genesis", i, amt, name)

    print_genesis()

    while True:
        print("Main Menu :")
        print("1. Create new transaction")
        print("2. View UTXO set")
        print("3. View mempool")
        print("4. Mine block")
        print("5. Run test scenarios")
        print("6. Exit\n")

        choice = input("Enter choice : ")

        if choice == "1":
            sender = input("Enter sender : ")
            print(f"Available balance : {utxo_manager.get_balance(sender)} BTC")
            receiver = input("Enter recipient : ")
            amount = float(input("Enter amount : "))

            print("\nCreating transaction ...")
            tx, msg = create_transaction(sender, receiver, amount, utxo_manager)
            if not tx:
                print(msg)
                continue

            print(msg)
            print("Transaction ID :", tx["tx_id"])

            ok, msg2 = mempool.add_transaction(tx, utxo_manager, validate_transaction)
            if ok:
                print("Transaction added to mempool .")
                print(f"Mempool now has {len(mempool.transactions)} transactions .")
            else:
                print("Transaction rejected :", msg2)

        elif choice == "2":
            for k, v in utxo_manager.utxo_set.items():
                print(k, "->", v)

        elif choice == "3":
            for tx in mempool.transactions:
                print(tx["tx_id"])

        elif choice == "4":
            miner = input("Enter miner name : ")
            print("Mining block ...")
            mine_block(miner, mempool, utxo_manager)

        elif choice == "5":
            print("\nRunning test ...\n")
            test_scenarios.run_all_tests()

        elif choice == "6":
            break


if __name__ == "__main__":
    main()
