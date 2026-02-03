def mine_block(miner_address, mempool, utxo_manager):
    txs = mempool.transactions
    count = len(txs)

    print(f"Selected {count} transactions from mempool .")

    total_fees = 0.0

    for tx in txs:
        input_sum = 0.0
        for inp in tx["inputs"]:
            utxo = utxo_manager.utxo_set[(inp["prev_tx"], inp["index"])]
            input_sum += utxo["amount"]
            utxo_manager.remove_utxo(inp["prev_tx"], inp["index"])

        output_sum = 0.0
        for i, out in enumerate(tx["outputs"]):
            utxo_manager.add_utxo(
                tx["tx_id"], i, out["amount"], out["address"]
            )
            output_sum += out["amount"]

        total_fees += input_sum - output_sum

    total_fees = round(total_fees, 8)

    print(f"Total fees : {total_fees} BTC")
    if total_fees > 0:
        utxo_manager.add_utxo("coinbase", 0, total_fees, miner_address)
        print(f"Miner {miner_address} receives {total_fees} BTC")

    mempool.clear()
    print("Block mined successfully !")
    print(f"Removed {count} transactions from mempool .")
