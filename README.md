# CS216 – UTXO Simulator

## Team Name
**BlockSmiths**

## Team Members
1. **Paruchuri Bhavya Sri** – Roll No: 240001049  
2. **Apoorva Dinesh Chipte** – Roll No: 240021003  
3. **Usepetla Nancy Sahithi** – Roll No: 240001075  
4. **Malothu Haritha** – Roll No: 240001042  

---

## Project Overview
This project is a simplified **Bitcoin UTXO (Unspent Transaction Output) Simulator** implemented in Python.  
It models how transactions are created, validated, stored in a mempool, and eventually confirmed through block mining.

The simulator demonstrates core blockchain concepts such as:
- UTXO-based accounting
- Transaction validation
- Prevention of double-spending
- Mempool handling
- Block mining and miner rewards

---

## Initial Genesis UTXOs
The system starts with the following predefined balances:

| User     | Balance (BTC) |
|----------|---------------|
| Alice    | 50.0          |
| Bob      | 30.0          |
| Charlie  | 20.0          |
| David    | 10.0          |
| Eve      | 5.0           |

---

## Project Structure
```text
CS216-BlockSmiths-UTXO-Simulator/
│
├── src/
│   ├── main.py            # Main menu-driven interface
│   ├── utxo_manager.py    # UTXO handling (add, remove, balance)
│   ├── transaction.py     # Transaction creation logic
│   ├── validator.py       # Transaction validation rules
│   ├── mempool.py         # Mempool management
│   └── block.py           # Block mining and fee rewards
│
├── tests/
│   └── test_scenarios.py  # Mandatory test scenarios
│
├── .gitignore
└── README.md
```
## Step 1: Clone the Repository
```bash
git clone https://github.com/Bhavyasri104/CS216-BlockSmiths-UTXO-Simulator.git
cd CS216-BlockSmiths-UTXO-Simulator
```
## Step 2: Run the Simulator
```bash
python src/main.py
```
## Program Menu Interface
```text
=== Bitcoin Transaction Simulator ===
Initial UTXOs (Genesis Block):
- Alice   : 50.0 BTC
- Bob     : 30.0 BTC
- Charlie : 20.0 BTC
- David   : 10.0 BTC
- Eve     : 5.0 BTC

Main Menu:
1. Create new transaction
2. View UTXO set
3. View mempool
4. Mine block
5. Run test scenarios
6. Exit
```
## Design Explanation
This section briefly describes the role of each major component in the simulator and how they interact.

### 1. UTXO Manager
- Maintains all unspent outputs
- Supports adding, removing, and querying balances
- Prevents reuse of already spent outputs
### 2. Transaction Validation
- Each transaction is checked for:
- Positive transaction amount
- Sufficient sender balance
- No double-spending within the same transaction
- No double-spending across the mempool
- Valid input–output balance
### 3. Mempool
- Stores validated but unconfirmed transactions
- Rejects conflicting transactions using the same UTXO
- Follows a first-seen rule for conflicts

### 4. Mining Logic
- Selects valid, non-conflicting transactions from the mempool
- Updates the UTXO set after confirmation
- Removes confirmed transactions from the mempool
- Rewards the miner using collected transaction fees

### 5. Testing
- Mandatory test scenarios verify:
- Valid transactions
- Double-spend rejection
- Insufficient funds handling
- Zero and negative amount rejection
- Mempool conflict handling
- Mining flow correctness
- Unconfirmed chain behavior
### Test Execution
```bash
pytest tests/
```
## Dependencies
- Python 3.8 or higher
- No external libraries required (only standard Python libraries)

## Notes
- The project follows good Git practices using feature branches
- Commits are descriptive and modular
- The main branch contains only merged, stable code
- Generated files (__pycache__, .pyc) are ignored using .gitignore
## Scope and Limitations
- The simulator does not implement cryptographic hashing or proof-of-work.
- The focus is on transaction correctness and UTXO management rather than network consensus.

