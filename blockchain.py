import hashlib
import time
import datetime
import psutil
class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index  # Block number
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
		self.chain = [Block(0, ["Genesis Block"], "0")]
		self.difficulty = difficulty
		self.confirmation_requirement = confirmation_requirement
		self.pending_blocks = []
	def get_latest_block(self):
		return self.chain[-1]
	def add_block(self, new_block):
		new_block.previous_hash = self.get_latest_block().hash
		new_block.mine_block(self.difficulty)
		self.pending_blocks.append(new_block)
		while len(self.pending_blocks) > self.confirmation_requirement:
			confirmed_block = self.pending_blocks.pop(0)
			print(f"Block confirmed and added to the chain. Index: {confirmed_block.index}, Hash: {confirmed_block.hash}")
			self.chain.append(confirmed_block)
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
		end_time = time.time()
		cpu_usage_end = psutil.cpu_percent(interval=None)
		time_taken = end_time - start_time
		cpu_utilization = (cpu_usage_start + cpu_usage_end) / psutil.cpu_count()
		print(f"Chain validation completed. Time taken: {time_taken:.2f} seconds, CPU Utilization: {cpu_utilization}%")
		return True
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
def get_custom_transaction():
    sender = input("Enter the sender's name: ")
    receiver = input("Enter the receiver's name: ")
    amount = input(f"Enter the amount {sender} wants to send to {receiver}: ")
    return f"{sender} pays {receiver} {amount} BTC"
def mine_new_block(blockchain):
    transactions = get_custom_transaction()
    new_block = Block(len(blockchain.chain), transactions, blockchain.get_latest_block().hash)
    blockchain.add_block(new_block)
    print("Block mined and added to the blockchain!")
def display_blockchain_state(blockchain):
    print("\nCurrent state of the blockchain:")
    blockchain.display_chain()
def main():
    blockchain_instance = BlockChain()
    while True:
        print("1. Add transactions and mine a new block\n")
        print("2. View blockchain\n")
        print("3. Verify blockchain integrity\n")
        print("4. Exit\n")     
        choice = input("Choose an option: ")       
        if choice == '1':
            mine_new_block(blockchain_instance)
        elif choice == '2':
            display_blockchain_state(blockchain_instance)
        elif choice == '3':
            if blockchain_instance.is_chain_valid():
                print("The blockchain is valid.")
            else:
                print("The blockchain is invalid.")
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again.")
if __name__ == "__main__":
    main()