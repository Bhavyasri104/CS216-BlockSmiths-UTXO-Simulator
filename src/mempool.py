class Mempool:
    def __init__(self):
        self.transactions = []
        self.spent_utxos = set()

    def add_transaction(self, tx, utxo_manager, validator):
        for inp in tx["inputs"]:
            ref = (inp["prev_tx"], inp["index"])
            if ref in self.spent_utxos:
                return False, f"UTXO {ref[0]}:{ref[1]} already spent by {self.transactions[0]['tx_id']}"

        ok, msg = validator(tx, utxo_manager)
        if not ok:
            return False, msg

        for inp in tx["inputs"]:
            self.spent_utxos.add((inp["prev_tx"], inp["index"]))

        self.transactions.append(tx)
        return True, "Transaction added to mempool"

    def clear(self):
        self.transactions.clear()
        self.spent_utxos.clear()
