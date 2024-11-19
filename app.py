from flask import Flask, jsonify, request
from blockchain import BlockChain, Block
import sys
import requests
import psutil
import time

app = Flask(__name__)

# Instantiate the blockchain
blockchain = BlockChain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [vars(block) for block in blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data}), 200

import psutil
import time
import requests
from flask import jsonify, request

@app.route('/mine', methods=['POST'])
def mine_block():
    start_time = time.time()  # Start time for mining process
    cpu_usage_start = psutil.cpu_percent(interval=None)  # Initial CPU usage
    transactions = request.json.get("transactions")
    if not transactions:
        return jsonify({"error": "Transactions are required"}), 400
    new_block = Block(len(blockchain.chain), transactions, blockchain.get_latest_block().hash)
    new_block.previous_hash = blockchain.get_latest_block().hash
    new_block.mine_block(blockchain.difficulty)
    blockchain.add_block(new_block)
    for node in blockchain.nodes:
        try:
            response = requests.post(f"{node}/add_block", json=vars(new_block), timeout=5)
            if response.status_code == 200:
                print(f"Block successfully sent to node {node}")
            else:
                print(f"Failed to send block to node {node}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")
    end_time = time.time() 
    cpu_usage_end = psutil.cpu_percent(interval=None)
    time_taken = end_time - start_time
    cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()
    print(f"Mining completed in {time_taken:.2f} seconds")
    print(f"CPU Utilization: {cpu_utilization:.2f}%")
    print(f"Nodes List: {blockchain.nodes}")
    return jsonify({
        "message": "New block mined and broadcasted",
        "block": vars(new_block),
        "time_taken": f"{time_taken:.2f} seconds",
        "cpu_utilization": f"{cpu_utilization:.2f}%",
    }), 201



@app.route('/verify', methods=['GET'])
def verify_integrity():
    start_time = time.time()
    cpu_usage_start = psutil.cpu_percent(interval=None)

    try:
        for i in range(1, len(blockchain.chain)):
            current_block = blockchain.chain[i]
            previous_block = blockchain.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return jsonify({
                    "valid": False,
                    "error": f"Invalid block hash at index {current_block.index}",
                    "details": "The computed hash does not match the stored hash."
                }), 400
            if current_block.previous_hash != previous_block.hash:
                return jsonify({
                    "valid": False,
                    "error": f"Invalid previous hash link at index {current_block.index}",
                    "details": "The previous hash stored in the block does not match the hash of the previous block."
                }), 400
            if not current_block.hash.startswith('0' * blockchain.difficulty):
                return jsonify({
                    "valid": False,
                    "error": f"Block {current_block.index} does not satisfy proof-of-work",
                    "details": "The block hash does not have the required number of leading zeros."
                }), 400
        end_time = time.time()
        cpu_usage_end = psutil.cpu_percent(interval=None)
        time_taken = end_time - start_time
        cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()
        return jsonify({
            "valid": True,
            "message": "Chain validation completed successfully",
            "time_taken": f"{time_taken:.2f} seconds",
            "cpu_utilization": f"{cpu_utilization:.2f}%"
        }), 200

    except Exception as e:
        return jsonify({
            "valid": False,
            "error": "Unexpected error occurred during verification",
            "details": str(e)
        }), 500




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
    start_time = time.time()  # Start time for conflict resolution
    cpu_usage_start = psutil.cpu_percent(interval=None)  # Initial CPU usage

    try:
        # Perform the conflict resolution
        replaced = blockchain.resolve_conflicts()

        end_time = time.time()  # End time for conflict resolution
        cpu_usage_end = psutil.cpu_percent(interval=None)  # Final CPU usage

        # Calculate the time taken and average CPU usage
        time_taken = end_time - start_time
        cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()  # Average CPU utilization

        if replaced:
            return jsonify({
                "message": "Chain was replaced",
                "new_chain": [vars(block) for block in blockchain.chain],
                "time_taken": f"{time_taken:.2f} seconds",
                "cpu_utilization": f"{cpu_utilization:.2f}%"
            }), 200

        return jsonify({
            "message": "Chain is authoritative",
            "time_taken": f"{time_taken:.2f} seconds",
            "cpu_utilization": f"{cpu_utilization:.2f}%"
        }), 200

    except requests.exceptions.RequestException as e:
        # Handle request-related errors gracefully
        return jsonify({
            "error": "Conflict resolution failed",
            "message": str(e)
        }), 500

    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500


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
