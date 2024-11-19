import hashlib
import time
import datetime
from urllib.parse import urlparse
import requests
import psutil
import json
class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_contents = (
            str(self.index) +
            str(self.timestamp) +
            str(self.transactions) +
            str(self.previous_hash) +
            str(self.nonce)
        )
        return hashlib.sha256(block_contents.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()  

class BlockChain:
    def __init__(self, difficulty = 4, confirmation_requirement = 0):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.confirmation_requirement = confirmation_requirement
        self.pending_blocks = []
        self.nodes = set()
        self.load_nodes_from_file()
    def create_genesis_block(self):
        genesis_block = Block(0, "Genesis Block", "0")
        genesis_block.timestamp = 0 
        genesis_block.hash = genesis_block.calculate_hash()  
        return genesis_block
    def load_nodes_from_file(self, file_path="nodes.json"):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.nodes = set(data.get("nodes", []))
                print(f"Nodes loaded: {self.nodes}")
        except FileNotFoundError:
            print(f"{file_path} not found. No nodes loaded.")
        except json.JSONDecodeError as e:
            print(f"Error decoding {file_path}: {e}")
    def get_latest_block(self):
        print(f"Getting latest block. Chain: {self.chain}")
        return self.chain[-1]
    def add_block(self, new_block):
        self.pending_blocks.append(new_block)
        confirmed_blocks = []
        while len(self.pending_blocks) > self.confirmation_requirement:
            confirmed_block = self.pending_blocks.pop(0)
            self.chain.append(confirmed_block)
            confirmed_blocks.append(confirmed_block)
            print(f"Block confirmed and added to the chain. Index: {confirmed_block.index}, Hash: {confirmed_block.hash}")
        if confirmed_blocks:
            return {
            "status": "confirmed",
            "confirmed_blocks": [vars(block) for block in confirmed_blocks],
            "pending_blocks": len(self.pending_blocks)
            }
        return {
            "status": "pending",
            "remaining_confirmations": self.confirmation_requirement - len(self.pending_blocks),
            "pending_blocks": len(self.pending_blocks)
            }
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Ensure the genesis block matches the current chain's genesis block
                if chain and chain[0] != vars(self.chain[0]):
                    continue

                # Replace with the longest valid chain
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = [self.deserialize_block(b) for b in new_chain]
            return True

        return False

    def validate_chain(self, chain):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        return True
    def deserialize_block(self, block_data):
        block = Block(
            index=block_data['index'],
            transactions=block_data['transactions'],
            previous_hash=block_data['previous_hash']
        )

        # Override the automatically generated attributes
        block.timestamp = block_data.get('timestamp', block.timestamp)  # Use provided timestamp or keep the generated one
        block.hash = block_data['hash']
        block.nonce = block_data['nonce']

        return block
