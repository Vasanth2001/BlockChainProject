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
        start_time = time.time()
        cpu_usage_start = psutil.cpu_percent(interval=None)
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()  
        end_time = time.time()
        cpu_usage_end = psutil.cpu_percent(interval=None)
        time_taken = end_time - start_time
        cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()
        print(f"Proof of Work completed. Time taken: {time_taken:.2f} seconds, CPU Utilization: {cpu_utilization}%")

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
    def is_chain_valid(self):
        start_time = time.time()
        cpu_usage_start = psutil.cpu_percent(interval=None)
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid block hash at index {current_block.index}")
                return False
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash link at index {current_block.index}")
                return False
            if not current_block.hash.startswith('0' * self.difficulty):
                print(f"Block {current_block.index} does not satisfy proof-of-work")
                return False
            total_difficulty += 1
        end_time = time.time()
        cpu_usage_end = psutil.cpu_percent(interval=None)
        time_taken = end_time - start_time
        cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()
        print(f"Chain validation completed. Time taken: {time_taken:.2f} seconds, CPU Utilization: {cpu_utilization}%")
        return total_difficulty >= len(self.chain)
    def display_chain(self):
        for block in self.chain:
            print("**************************************")
            print(f"Index: {block.index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Transactions: {block.transactions}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print(f"Nonce: {block.nonce}")
            print("**************************************")
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = [self.deserialize_block(b) for b in new_chain]
            return True
        return False
    def validate_chain(self, chain):
        for i in range(1, len(chain)):
            block = chain[i]
            previous_block = chain[i - 1]
            if block['previous_hash'] != previous_block['hash']:
                return False
            if not block['hash'].startswith('0' * self.difficulty):
                return False
        return True
    @staticmethod
    def deserialize_block(block_data):
        try:
            return Block(
                index=block_data['index'],
                transactions=block_data['transactions'],
                previous_hash=block_data['previous_hash']
            )
        except KeyError as e:
            print(f"Error deserializing block: missing key {e}")
            return None
