import requests

def get_node_address():
    """Prompt the user to specify the node address."""
    print("Enter the address of the node you want to connect to (e.g., http://127.0.0.1:5000):")
    return input("Node address: ").strip()

def get_custom_transaction():
    sender = input("Enter the sender's name: ")
    receiver = input("Enter the receiver's name: ")
    amount = input(f"Enter the amount {sender} wants to send to {receiver}: ")
    return f"{sender} pays {receiver} {amount} BTC"

def mine_new_block(node_address):
    transaction = get_custom_transaction()

    # Send the transaction to the node for mining
    response = requests.post(
        f"{node_address}/mine",
        json={"transactions": [transaction]}
    )

    if response.status_code == 201:
        block_data = response.json().get("block", {})
        print(f"Block mined successfully! Index: {block_data.get('index')}, Hash: {block_data.get('hash')}")
    else:
        print("Failed to mine block. Error:", response.json().get("error"))

def display_blockchain_state(node_address):
    response = requests.get(f"{node_address}/chain")
    if response.status_code == 200:
        chain_data = response.json().get("chain", [])
        print("\nCurrent state of the blockchain:")
        for block in chain_data:
            print("**************************************")
            print(f"Index: {block['index']}")
            print(f"Timestamp: {block['timestamp']}")
            print(f"Transactions: {block['transactions']}")
            print(f"Previous Hash: {block['previous_hash']}")
            print(f"Hash: {block['hash']}")
            print(f"Nonce: {block['nonce']}")
            print("**************************************")
    else:
        print("Failed to fetch blockchain state.")

def verify_blockchain_integrity(node_address):
    response = requests.get(f"{node_address}/chain")
    if response.status_code == 200:
        print("The blockchain is valid.")
    else:
        print("The blockchain is invalid.")

def main():
    node_address = get_node_address()

    while True:
        print("1. Add transactions and mine a new block\n")
        print("2. View blockchain\n")
        print("3. Verify blockchain integrity\n")
        print("4. Exit\n")
        choice = input("Choose an option: ")

        if choice == '1':
            mine_new_block(node_address)
        elif choice == '2':
            display_blockchain_state(node_address)
        elif choice == '3':
            verify_blockchain_integrity(node_address)
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()