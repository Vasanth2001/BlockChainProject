from flask import Flask, jsonify, request
from blockchain import BlockChain, Block
import sys
import requests

app = Flask(__name__)

# Instantiate the blockchain
blockchain = BlockChain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [vars(block) for block in blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data}), 200

@app.route('/mine', methods=['POST'])
def mine_block():
    transactions = request.json.get("transactions")
    if not transactions:
        return jsonify({"error": "Transactions are required"}), 400

    new_block = Block(len(blockchain.chain), transactions, blockchain.get_latest_block().hash)
    new_block.previous_hash = blockchain.get_latest_block().hash
    new_block.mine_block(blockchain.difficulty)
    blockchain.add_block(new_block)

    # Broadcast the new block to other nodes
    for node in blockchain.nodes:  # Assuming blockchain.nodes contains the list of peers
        try:
            response = requests.post(f"{node}/add_block", json=vars(new_block), timeout=5)
            if response.status_code == 200:
                print(f"Block successfully sent to node {node}")
            else:
                print(f"Failed to send block to node {node}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")

    print(f"Nodes List: {blockchain.nodes}")
    return jsonify({"message": "New block mined and broadcasted", "block": vars(new_block)}), 201




@app.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.json
    if not block_data:
        return jsonify({"error": "Invalid block data"}), 400
    new_block = Block(
        block_data['index'],
        block_data['transactions'],
        block_data['previous_hash']
    )
    new_block.hash = block_data['hash']
    new_block.nonce = block_data['nonce']
    new_block.timestamp = block_data['timestamp']
    last_block = blockchain.get_latest_block()
    if (
        last_block.hash == new_block.previous_hash
        and new_block.hash.startswith('0' * blockchain.difficulty)
        and new_block.hash == new_block.calculate_hash()
    ):
        result = blockchain.add_block(new_block)
        return jsonify(result), 200
    else:
        try:
            resolve_url = f"http://localhost:{request.host.split(':')[1]}/nodes/resolve"
            response = requests.get(resolve_url, timeout=5)
            if response.status_code == 200:
                return jsonify({
                    "error": "Invalid block",
                    "message": "Attempted to resolve conflicts",
                    "resolve_response": response.json()
                }), 400
            else:
                return jsonify({
                    "error": "Invalid block",
                    "message": "Conflict resolution failed"
                }), 400
        except requests.exceptions.RequestException as e:
            return jsonify({
                "error": "Invalid block",
                "message": f"Conflict resolution failed: {str(e)}"
            }), 400
        return jsonify({"error": "Invalid block"}), 400



@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        return jsonify({"message": "Chain was replaced", "new_chain": [vars(block) for block in blockchain.chain]}), 200
    return jsonify({"message": "Chain is authoritative"}), 200

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Extract port number from command line if provided
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number provided. Using default (5000)")
            port = 5000
    else:
        # Use default port if no argument provided
        port = 5000

    app.run(port=port)
