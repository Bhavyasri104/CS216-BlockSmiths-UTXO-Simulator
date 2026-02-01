def mine_block(miner_address, mempool, utxo_manager, num_txs=5):
    if not mempool.transactions:
        print("No transactions to mine.")
        return

    # Select up to num_txs non-conflicting transactions (first-seen rule)
    used_utxos = set()
    selected_txs = []
    for tx in mempool.transactions:
        conflict = False
        for inp in tx["inputs"]:
            utxo_key = (inp["prev_tx"], inp["index"])
            if utxo_key in used_utxos:
                conflict = True
                break
        if not conflict:
            selected_txs.append(tx)
            for inp in tx["inputs"]:
                used_utxos.add((inp["prev_tx"], inp["index"]))
        if len(selected_txs) >= num_txs:
            break

    total_fee = 0.0

    print("\nMining block...")
    print(f"Selected {len(selected_txs)} transactions from mempool")

    for tx in selected_txs:
        input_sum = 0.0
        output_sum = 0.0

        # Remove spent UTXOs
        for inp in tx["inputs"]:
            utxo = utxo_manager.utxo_set[(inp["prev_tx"], inp["index"])]
            input_sum += utxo["amount"]
            utxo_manager.remove_utxo(inp["prev_tx"], inp["index"])

        # Add new UTXOs
        for index, out in enumerate(tx["outputs"]):
            utxo_manager.add_utxo(
                tx["tx_id"],
                index,
                out["amount"],
                out["address"]
            )
            output_sum += out["amount"]

        total_fee += input_sum - output_sum
        mempool.remove_transaction(tx["tx_id"])

    # Miner reward = total fees
    if total_fee > 0:
        utxo_manager.add_utxo(
            "coinbase",
            0,
            total_fee,
            miner_address
        )

    print(f"Total fees collected: {total_fee} BTC")
    print(f"Miner {miner_address} rewarded")
    print("Block mined successfully!")