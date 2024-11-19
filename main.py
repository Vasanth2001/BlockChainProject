import requests

def get_node_address():
    print("Enter the address of the node you want to connect to (e.g., http://127.0.0.1:5000):")
    return input("Node address: ").strip()

def get_custom_transaction():
    sender = input("Enter the sender's name: ")
    receiver = input("Enter the receiver's name: ")
    amount = input(f"Enter the amount {sender} wants to send to {receiver}: ")
    return f"{sender} pays {receiver} {amount} BTC"

def mine_new_block(node_address):
    transaction = get_custom_transaction()
    response = requests.post(
        f"{node_address}/mine",
        json={"transactions": [transaction]}
    )
    print('#####################################################')
    if response.status_code == 201:
        response_data = response.json()
        block_data = response_data.get("block", {})
        time_taken = response_data.get("time_taken", "N/A")
        cpu_utilization = response_data.get("cpu_utilization", "N/A")
        print(f"Block mined successfully!")
        print(f"Index: {block_data.get('index')}")
        print(f"Hash: {block_data.get('hash')}")
        print(f"Time Taken: {time_taken}")
        print(f"CPU Utilization: {cpu_utilization}")
    else:
        error_message = response.json().get("error", "Unknown error occurred")
        print("Failed to mine block. Error:", error_message)
    print('#####################################################')


def resolve_chain(node_address):
    try:
        response = requests.get(f"{node_address}/nodes/resolve")
        if response.status_code == 200:
            result = response.json()
            print(result.get('message', 'No message provided'))
            if "new_chain" in result:
                for block in result["new_chain"]:
                    print("**************************************")
                    print(f"Index: {block.get('index', 'N/A')}, "
                          f"Timestamp: {block.get('timestamp', 'N/A')}, "
                          f"Transactions: {block.get('transactions', 'N/A')}, "
                          f"Previous Hash: {block.get('previous_hash', 'N/A')}, "
                          f"Hash: {block.get('hash', 'N/A')}, "
                          f"Nonce: {block.get('nonce', 'N/A')}")
                    print("**************************************")
            else:
                print("No changes made. The chain is authoritative.")
            time_taken = result.get("time_taken")
            cpu_utilization = result.get("cpu_utilization")
            if time_taken or cpu_utilization:
                if time_taken:
                    print(f"Time Taken: {time_taken}")
                if cpu_utilization:
                    print(f"CPU Utilization: {cpu_utilization}")
        else:
            # If the request fails, provide the status code and response
            print(f"Failed to resolve conflicts. HTTP Status: {response.status_code}")
            try:
                print(response.json())
            except ValueError:
                print("Response content could not be parsed as JSON.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

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
    response = requests.get(f"{node_address}/verify")
    print("--------------------------------------")
    
    if response.status_code == 200:
        data = response.json()
        print("Blockchain Integrity Verification Successful!")
        print(f"Time Taken: {data.get('time_taken')}")
        print(f"CPU Utilization: {data.get('cpu_utilization')}")
        print("Validation Result: The blockchain is valid.")
    else:
        data = response.json()
        print(f"Blockchain Integrity Verification Failed: {data.get('message')}")
        print(f"Error: {data.get('error')}")
    
    print("--------------------------------------")


def main():
    node_address = get_node_address()
    while True:
        print("1. Add transactions and mine a new block")
        print("2. View blockchain")
        print("3. Verify blockchain integrity")
        print("4. Resolve chain conflicts")
        print("5. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            mine_new_block(node_address)
        elif choice == '2':
            display_blockchain_state(node_address)
        elif choice == '3':
            verify_blockchain_integrity(node_address)
        elif choice == '4':
            resolve_chain(node_address)
        elif choice == '5':
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
