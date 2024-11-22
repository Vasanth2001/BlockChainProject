from flask import Flask, jsonify, request
from blockchain import BlockChain, Block, Wallet, Transaction
import sys
import requests
import psutil
import time
import threading
from urllib.parse import urlparse

app = Flask(__name__)
blockchain = None
wallet = None

@app.route('/wallet', methods=['POST'])
def get_wallet_details():
    try:
        wallet_address = wallet.get_address()
        balance = blockchain.get_wallet_balance(wallet_address)
        response = {
            "public_key": wallet_address,
            "balance": balance
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/wallet_details', methods=['POST'])
def receive_wallet_details():
    try:
        data = request.get_json()
        public_key = data['public_key']
        balance = data['balance']
        sender_address = data['node_address']
        blockchain.wallets[public_key] = balance
        my_wallet_details = {
            "public_key": wallet.get_address(),
            "balance": blockchain.get_wallet_balance(wallet.get_address()),
            "node_address": f"http://localhost:{port}"
        }
        response = requests.post(f"{sender_address}/wallet_details/update", json=my_wallet_details)
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Wallet details updated and sent back."}), 200
        else:
            return jsonify({"status": "partial_success", "message": "Wallet details updated but failed to send back."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/wallet_details/update', methods=['POST'])
def update_wallet_details():
    try:
        # Get wallet details from incoming JSON
        data = request.get_json()
        public_key = data['public_key']
        balance = data['balance']
        
        # Add the wallet details to your local blockchain wallet dictionary
        blockchain.wallets[public_key] = balance
        return jsonify({"status": "success", "message": "Wallet details received and updated."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mempool', methods=['GET'])
def get_mempool():
    return jsonify({"mempool": blockchain.mempool}), 200

@app.route('/update_mempool', methods=['POST'])
def update_mempool():
    try:
        data = request.json
        new_mempool = data.get('mempool')
        if new_mempool is None:
            return jsonify({"error": "Mempool data is required"}), 400

        blockchain.mempool = new_mempool 
        return jsonify({"message": "Mempool updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_mempool', methods=['POST'])
def append_mempool():
    try:
        data = request.json
        transactions = data.get("transactions")[0]
        if transactions is None:
            return jsonify({"error": "Transactions are required"}), 400
        blockchain.mempool.append(transactions) 
        return jsonify({"message": "Transaction added to mempool successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/transaction', methods=['POST'])
def create_transaction():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount') 
    if not all([sender, receiver, amount is not None]):
        return jsonify({"error": "Sender, receiver, amount are required"}), 400
    transaction = Transaction(wallet, sender, receiver, amount)
    if transaction.validate_transaction(blockchain):
        transaction_data = transaction.to_dict()
        payload = {
            "transactions": [transaction.to_dict()]
        }
        for node in blockchain.nodes:
            try:
                response = requests.post(f"{node}/add_mempool", json=payload, timeout=5)
                if response.status_code == 201:
                    print(f"Transaction added to {node} mempool")
                else:
                    print(f"Failed to broadcast transaction to {node}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error broadcasting transaction to {node}: {e}")
        return jsonify({
            "message": "Transaction validated and added to the mempool"
        }), 201
    else:
        return jsonify({"error": "Invalid transaction"}), 400


@app.route('/transaction_simulation', methods=['POST'])
def create_transaction_simulation():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = data.get('amount')
    if not all([sender, receiver, amount is not None]):
        return jsonify({"error": "Sender, receiver, and amount are required"}), 400
    transaction = Transaction(wallet, sender, receiver, amount)
    transaction_data = transaction.to_dict()
    for node in blockchain.nodes:
        try:
            response = requests.post(f"{node}/add_mempool", json=transaction_data, timeout=5)
            if response.status_code == 201:
                print(f"Transaction broadcasted to {node}")
            else:
                print(f"Failed to broadcast transaction to {node}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error broadcasting transaction to {node}: {e}")


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [vars(block) for block in blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data}), 200


@app.route('/verify', methods=['GET'])
def verify_integrity():
    start_time = time.time()
    cpu_usage_start = psutil.cpu_percent(interval=None)

    try:
        for i in range(1, len(blockchain.chain)):
            current_block = blockchain.chain[i]
            previous_block = blockchain.chain[i - 1]
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
        return jsonify({
            "error": "Conflict resolution failed",
            "message": str(e)
        }), 500

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 500


def broadcast_wallet_details():
    while True:
        try:
            wallet_address = wallet.get_address()
            balance = blockchain.get_wallet_balance(wallet_address)
            payload = {
                "public_key": wallet_address,
                "balance": balance,
                "node_address": f"http://localhost:{port}"
            }

            for node in blockchain.nodes:
                try:
                    response = requests.post(f"{node}/wallet_details", json=payload, timeout=5)
                    if response.status_code == 200:
                        print(f"Wallet details sent to {node}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to send wallet details to {node}: {e}")

            time.sleep(300)
        except Exception as e:
            print(f"Error in wallet broadcast thread: {str(e)}")


def prioritize_mempool(mempool):
    print("Mempool before prioritization:", mempool)
    return sorted(
        mempool, 
        key=lambda tx: (-tx.get('fee', 0), tx.get('timestamp', 0))
    )


def mine_block():
    start_time = time.time()
    max_transactions = 2
    if len(blockchain.mempool) < max_transactions:
        print("Not enough transactions to mine a block")
        return
    prioritized_mempool = prioritize_mempool(blockchain.mempool)
    transactions = prioritized_mempool[:max_transactions] 
    new_block = Block(len(blockchain.chain), transactions, blockchain.get_latest_block().hash)
    new_block.mine_block(blockchain.difficulty)
    blockchain.add_block(new_block)
    blockchain.mempool = blockchain.mempool[len(transactions):]
    for node in blockchain.nodes:
        try:
            response = requests.post(f"{node}/add_block", json=vars(new_block), timeout=5)
            if response.status_code == 200:
                print(f"Block successfully sent to node {node}")
            else:
                print(f"Failed to send block to node {node}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")
    for node in blockchain.nodes:
        try:
            response = requests.post(f"{node}/update_mempool", json={"mempool": blockchain.mempool}, timeout=5)
            if response.status_code == 200:
                print(f"Mempool successfully synchronized with node {node}")
            else:
                print(f"Failed to synchronize mempool with node {node}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to node {node}: {e}")
    end_time = time.time()
    time_taken = end_time - start_time
    print(f"Block mined and broadcasted in {time_taken:.2f} seconds")


def mine_blocks_periodically():
    while True:
        print("Trying to mine......")
        mine_block()
        time.sleep(5)

if __name__ == "__main__":
    port = 5000  
    wallet_balance = 100 
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number provided. Using default (5000)")
    if len(sys.argv) > 2:
        try:
            wallet_balance = float(sys.argv[2])
            if wallet_balance < 0:
                raise ValueError("Wallet balance cannot be negative.")
        except ValueError:
            print("Invalid wallet balance provided. Using default (100)")
    blockchain = BlockChain()
    wallet = Wallet(wallet_balance)
    blockchain.wallets[wallet.get_address()] = wallet_balance
    threading.Thread(target=mine_blocks_periodically, daemon=True).start()
    threading.Thread(target=broadcast_wallet_details, daemon=True).start()
    app.run(port=port)
