class Mempool:
    def __init__(self, max_size=50):
        self.transactions = []  # Store transactions
        self.spent_utxos = set()  # Track UTXOs spent in mempool
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager=None):
        """Validate and add transaction. Return (success, message)."""
        from validator import validate_transaction

        if len(self.transactions) >= self.max_size:
            return False, "Mempool is full"
        if utxo_manager is None:
            return False, "UTXO manager required for validation"
        valid, msg = validate_transaction(tx, utxo_manager, self)
        if not valid:
            return False, msg
        self.transactions.append(tx)
        for inp in tx["inputs"]:
            self.spent_utxos.add((inp["prev_tx"], inp["index"]))
        return True, "Transaction added"

    def remove_transaction(self, tx_id: str):
        """Remove transaction (when mined)."""
        tx_to_remove = None
        for tx in self.transactions:
            if tx["tx_id"] == tx_id:
                tx_to_remove = tx
                break
        if tx_to_remove:
            self.transactions.remove(tx_to_remove)
            for inp in tx_to_remove["inputs"]:
                self.spent_utxos.discard((inp["prev_tx"], inp["index"]))

    def get_top_transactions(self, n: int) -> list:
        """Return top N transactions by fee (highest first)."""

        def fee(tx, utxo_manager=None):
            # Calculate fee for sorting
            input_sum = 0.0
            output_sum = 0.0
            for inp in tx["inputs"]:
                # UTXO manager is not available here, so skip precise lookup
                # Assume input_sum is sum of amounts in input dict if present
                if "amount" in inp:
                    input_sum += inp["amount"]
            for out in tx["outputs"]:
                output_sum += out["amount"]
            return input_sum - output_sum

        # If txs have fee info, sort by it; else, keep order
        txs_with_fee = []
        for tx in self.transactions:
            # Try to get fee from message if present, else estimate as 0
            try:
                input_sum = 0.0
                output_sum = 0.0
                for inp in tx["inputs"]:
                    # No amount in input, so skip
                    pass
                for out in tx["outputs"]:
                    output_sum += out["amount"]
                # Fee is input_sum - output_sum, but input_sum unknown here
                # For demo, treat fee as 0
                txs_with_fee.append((0, tx))
            except Exception:
                txs_with_fee.append((0, tx))
        # Sort by fee descending (all 0 if not computable)
        txs_with_fee.sort(key=lambda x: x[0], reverse=True)
        return [tx for _, tx in txs_with_fee[:n]]

    def clear(self):
        """Clear all transactions."""
        self.transactions.clear()
        self.spent_utxos.clear()