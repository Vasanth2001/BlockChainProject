# Blockchain with P2P Network

This project is a simplified blockchain implementation featuring Proof of Work (PoW) consensus and basic peer-to-peer (P2P) networking. The blockchain can mine new blocks, add them to the chain, validate integrity, and resolve conflicts across nodes. 

The project uses Flask for the server-side APIs, allowing multiple nodes to communicate and maintain a synchronized blockchain. 

---

## Features

1. **Proof of Work**: Blocks are mined by solving a computationally difficult problem based on a configurable difficulty level.
2. **Genesis Block**: The chain is initialized with a Genesis block.
3. **Block Validation**: Ensures data integrity and validates that the chain satisfies the PoW.
4. **Distributed Network**:
   - Nodes can broadcast new blocks to peers.
   - Nodes can resolve conflicts to agree on the longest valid chain.
5. **RESTful API**: API endpoints to mine, add blocks, fetch the blockchain, and resolve conflicts.
6. **CLI Interface**: A user-friendly CLI to interact with the blockchain, submit transactions, view the chain, and verify its integrity.

---

## Technologies Used

- **Python**: Core logic and implementation.
- **Flask**: RESTful API for blockchain interactions.
- **Requests**: HTTP communication between nodes.
- **Psutil**: Performance monitoring during mining.
- **JSON**: Serialization and deserialization of blockchain data.

---

## Project Structure

```plaintext
├── blockchain.py   # Core blockchain logic
├── app.py          # Flask app exposing blockchain APIs
├── main.py         # CLI interface for interacting with the blockchain
├── nodes.json      # File to store connected nodes
```

---

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/blockchain-p2p.git
   cd blockchain-p2p
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.6+ installed. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run a Node**:
   Start a node using `app.py`. Optionally, specify the port:
   ```bash
   python app.py 5000
   ```
   If no port is provided, the default is `5000`.

4. **Start the CLI Interface**:
   Use the CLI to interact with the blockchain:
   ```bash
   python main.py
   ```

---

## API Endpoints

### **1. Fetch Blockchain**
- **URL**: `/chain`
- **Method**: GET
- **Response**: JSON representation of the blockchain.

### **2. Mine a New Block**
- **URL**: `/mine`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "transactions": ["Alice pays Bob 10 BTC"]
  }
  ```
- **Response**: Details of the mined block.

### **3. Add a Block**
- **URL**: `/add_block`
- **Method**: POST
- **Request Body**: Block data.
- **Response**: Status of block addition.

### **4. Resolve Conflicts**
- **URL**: `/nodes/resolve`
- **Method**: GET
- **Response**: Updated blockchain if conflicts are resolved.

---

## Usage

### From the CLI

1. **Add Transactions and Mine a Block**:
   Enter details of the sender, receiver, and amount. The block is mined and added to the chain.

2. **View Blockchain**:
   View the full blockchain with all blocks and their details.

3. **Verify Blockchain**:
   Ensure the blockchain is valid and intact.

4. **Exit**:
   Quit the CLI.

---

## Node Synchronization

- Add peers by modifying the `nodes.json` file:
  ```json
  {
    "nodes": ["http://127.0.0.1:5001", "http://127.0.0.1:5002"]
  }
  ```
- Nodes communicate with peers to broadcast new blocks and resolve chain conflicts.

---

## Example Workflow

1. Start two nodes on different ports:
   ```bash
   python app.py 5000
   python app.py 5001
   ```

2. Add transactions and mine blocks via the CLI:
   ```bash
   python main.py
   ```

3. Use `/nodes/resolve` to synchronize chains across nodes.

---

## Future Enhancements

- Add support for digital signatures and cryptographic verification.
- Implement a more advanced consensus mechanism.
- Extend the P2P network to discover peers dynamically.

---

## License

This project is licensed under the MIT License. Feel free to use and modify it for your purposes.
