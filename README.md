# Blockchain Node Interaction System

This project provides a Python-based command-line interface (CLI) to interact with a blockchain network. The system allows users to connect to multiple nodes, view wallet details, mine new blocks, verify blockchain integrity, and resolve chain conflicts. It simulates transactions between nodes and provides a simple way to visualize and manage a decentralized blockchain.

## Features

- **Node Interaction**: Connect to different blockchain nodes and interact with their wallets.
- **Transaction Mining**: Add transactions and mine new blocks between nodes.
- **Blockchain State Viewing**: View the current state of the blockchain, including transaction details, hashes, and previous blocks.
- **Blockchain Integrity Verification**: Verify the integrity of the blockchain to ensure that it hasn't been tampered with.
- **Chain Resolution**: Resolve conflicts between nodes by selecting the longest valid chain.
- **Wallet Management**: Display wallet details (public key and balance) for individual nodes or all nodes in the network.

## Installation

### Requirements

- Python 3.x
- `requests` library (for making HTTP requests)

### Setup

1. Clone the repository:


2. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Make sure you have a `nodes.json` file in the project directory that contains the addresses of the blockchain nodes you want to connect to. Example format for `nodes.json`:

    ```
    {
        "nodes": [
            "http://127.0.0.1:5000",
            "http://127.0.0.1:5001"
            "http://127.0.0.1:5002"

        ]
    }
    ```

## Usage

### Running the Blockchain Node Server (`app.py`)

To run the blockchain node server on a specific port, use the following command:

```bash
python3 app.py <PORT> <WALLET BALANCE>
```

### Run the script:

    ```bash
    python main.py
    ```
The program will prompt you to enter the address of the node you want to connect to. For example:

    ```
    Enter the address of the node you want to connect to (e.g., http://127.0.0.1:5000):
    ```

After connecting to the node, you'll see a menu with the following options:

    1. Add transactions and mine a new block
    2. View blockchain
    3. Verify blockchain integrity
    4. Resolve chain conflicts
    5. Display your wallet details
    6. View other nodes' wallets
    7. Exit

Choose the corresponding number to perform an action.

### Example Workflow

- **Transaction Mining**: You can send transactions between nodes by selecting an active node to send funds to.
- **Blockchain State**: View the entire blockchain or just check the latest state of the chain.
- **Chain Resolution**: If there's a conflict between nodes, the system can help resolve it by selecting the longest valid chain.
- **Integrity Verification**: Verify that the blockchain is consistent across all nodes.

## Contributing

If you'd like to contribute to this project, feel free to fork the repository, create a new branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
