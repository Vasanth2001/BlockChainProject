# Blockchain Implementation in Python

This project is a simple blockchain implementation in Python, featuring essential blockchain concepts like proof-of-work mining, transaction handling, block validation, and chain integrity checks.

## Features

- **Proof-of-Work (PoW):** Mining blocks with configurable difficulty.
- **CPU Utilization Tracking:** Tracks CPU usage during block mining and chain validation.
- **Dynamic Block Confirmation:** Blocks are confirmed and added to the chain based on a customizable confirmation requirement.
- **Transaction Simulation:** Supports custom transactions between users.
- **Chain Integrity Check:** Verifies the entire blockchain for data consistency and proof-of-work validity.

## Prerequisites

- Python 3.x
- `psutil` library for CPU usage tracking.

Install `psutil`:
```bash
pip install psutil
```

## Classes and Methods

### `Block`

This class represents a block in the blockchain.

- **Attributes**:
  - `index`: Block number.
  - `timestamp`: Timestamp when the block is created.
  - `transactions`: List of transactions in the block.
  - `previous_hash`: Hash of the previous block for chain linking.
  - `nonce`: A number used to find a valid block hash.
  - `hash`: Unique identifier calculated using SHA-256.

- **Methods**:
  - `calculate_hash()`: Computes the SHA-256 hash of the block.
  - `mine_block(difficulty)`: Mines the block using proof-of-work by finding a hash with a specific number of leading zeros.

### `BlockChain`

This class manages the blockchain, a list of linked blocks.

- **Attributes**:
  - `chain`: List of confirmed blocks in the blockchain.
  - `difficulty`: Number of leading zeros required in the hash for PoW.
  - `confirmation_requirement`: Number of mined blocks needed before appending to the chain.
  - `pending_blocks`: List of blocks awaiting confirmation.

- **Methods**:
  - `get_latest_block()`: Returns the last confirmed block in the chain.
  - `add_block(new_block)`: Mines and adds a new block to the chain.
  - `is_chain_valid()`: Validates the blockchain by checking hash consistency and proof-of-work requirements.
  - `display_chain()`: Displays all confirmed blocks in the chain.

### Utility Functions

- **`get_custom_transaction()`**: Collects transaction details from the user.
- **`mine_new_block(blockchain)`**: Mines a new block and adds it to the blockchain.
- **`display_blockchain_state(blockchain)`**: Displays the current blockchain.

### `main()` Function

The main menu offers four options:
1. **Add and Mine a New Block**: Adds transactions and mines a new block.
2. **View Blockchain**: Displays the blockchain.
3. **Verify Blockchain Integrity**: Validates the entire blockchain.
4. **Exit**: Exits the program.

## Usage

Run the program:

```bash
python blockchain.py
```

In the main menu, you can choose:
1. Add and mine a new block with custom transactions.
2. View the entire blockchain and each block's details.
3. Verify the blockchain's integrity.
4. Exit the program.

## Example Run

1. Select **Option 1** to enter a transaction and mine a block.
2. Choose **Option 2** to view the blockchain.
3. Use **Option 3** to check the validity of the blockchain.

## License

This code is provided under the MIT License.
