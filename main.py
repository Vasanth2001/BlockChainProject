import requests
import json
from pprint import pprint
import time
import random 
def get_node_address():
    print("Enter the address of the node you want to connect to (e.g., http://127.0.0.1:5000):")
    return input("Node address: ").strip()

def get_node_wallet_address(node_address):
    try:
        response = requests.post(f"{node_address}/wallet")
        if response.status_code == 200:
            wallet_details = response.json()
            public_key = wallet_details.get("public_key", "N/A")
            return public_key
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def get_all_nodes_wallets():
    try:
        with open("nodes.json", "r") as file:
            data = json.load(file)
            nodes = data.get("nodes", [])
        if not nodes:
            print("No nodes found in nodes.json")
            return {}
        node_wallets = {}
        for node_address in nodes:
            try:
                response = requests.post(f"{node_address}/wallet", timeout=5)  # Set a timeout for responsiveness
                if response.status_code == 200:
                    wallet_details = response.json()
                    public_key = wallet_details.get("public_key", "N/A")
                    node_wallets[node_address] = [public_key, "active"]
                else:
                    node_wallets[node_address] = ["N/A", "inactive"]
            except requests.exceptions.RequestException:
                node_wallets[node_address] = ["N/A", "inactive"]

        return node_wallets
    except FileNotFoundError:
        print("Error: nodes.json file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to parse nodes.json. Please ensure it is in valid JSON format.")
        return {}

def display_wallet_details():
    try:
        with open("nodes.json", "r") as file:
            data = json.load(file)
            nodes = data.get("nodes", [])

        if not nodes:
            print("No nodes found in nodes.json")
            return

        print("\nWallet Details of All Nodes:")
        print("###############################################")
        
        for node_address in nodes:
            try:
                print(f"Node Address : {node_address}")
                response = requests.post(f"{node_address}/wallet")
                if response.status_code == 200:
                    wallet_details = response.json()
                    public_key = wallet_details.get("public_key", "N/A")
                    balance = wallet_details.get("balance", "N/A")
                    print(f"Node: {node_address}")
                    print(f"  Public Key: {public_key}")
                    print(f"  Balance: {balance}")
                else:
                    print(f"Failed to fetch wallet details from {node_address}")
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {node_address}: {e}")
            print("###############################################")

    except FileNotFoundError:
        print("nodes.json file not found.")
    except json.JSONDecodeError:
        print("Failed to parse nodes.json. Please ensure it is in valid JSON format.")

def display_my_wallet_details(node_address):
    try:
        response = requests.post(f"{node_address}/wallet")
        if response.status_code == 200:
            wallets = response.json()
            print("Wallet Details from Node:")
            for wallet, balance in wallets.items():
                print(f"Wallet Address: {wallet}, Balance: {balance}")
        else:
            print(f"Failed to retrieve wallet details from {node_address}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving wallet details from {node_address}: {e}")



def check_wallet_balance(node_address):
    try:
        response = requests.get(f"{node_address}/wallet")
        if response.status_code == 200:
            data = response.json()
            public_key = data.get("public_key", "N/A")
            balance = data.get("balance", 0)
            print("#####################################################")
            print("Wallet Details:")
            print(f"Public Key:\n{public_key}")
            print(f"Balance: {balance} BTC")
            print("#####################################################")
        else:
            print("Failed to fetch wallet details.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def mine_new_block(node_address, sender_wallet_address):
    nodes_wallets = get_all_nodes_wallets()
    active_nodes = {i + 1: (node, details[0]) for i, (node, details) in enumerate(nodes_wallets.items()) if details[1] == "active" and node != node_address}
    if not active_nodes:
        print("No active nodes available. Cannot proceed with the transaction.")
        return
    print("\nSelect a receiver from the active nodes below:")
    pprint({key: {"Node Address": value[0], "Public Key": value[1]} for key, value in active_nodes.items()})
    try:
        choice = int(input("Enter the number corresponding to the receiver: ").strip())
        if choice not in active_nodes:
            print("Invalid choice! Please select a valid option.")
            return
        receiver = active_nodes[choice][1]
    except ValueError:
        print("Error: Please enter a valid number!")
        return
    try:
        amount = float(input("Enter the amount to send: ").strip())
        if amount <= 0:
            print("Error: Transaction amount must be greater than zero!")
            return
    except ValueError:
        print("Error: Amount must be a valid number!")
        return
    transaction = {
        "sender": sender_wallet_address,
        "receiver": receiver,
        "amount": amount,
        "signature": None
    }
    try:
        response = requests.post(f"{node_address}/transaction", json=transaction)
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||")
        if response.status_code == 201:
            response_data = response.json()
            block_data = response_data.get("block", {})
            time_taken = response_data.get("time_taken", "N/A")
            cpu_utilization = response_data.get("cpu_utilization", "N/A")
            
            print("Transaction submitted and block mined successfully!")
            print(f"Index: {block_data.get('index')}")
            print(f"Hash: {block_data.get('hash')}")
            print(f"Time Taken: {time_taken}")
            print(f"CPU Utilization: {cpu_utilization}")
        else:
            error_message = response.json().get("error", "Unknown error occurred")
            print("Failed to process transaction and mine block. Error:", error_message)
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


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


def simulate_pinning_attack(node_address, sender_wallet_address):
    try:
        nodes_wallets = get_all_nodes_wallets()
        active_wallets = [
            wallet_details[0]
            for node, wallet_details in nodes_wallets.items()
            if wallet_details[1] == "active" and wallet_details[0] != sender_wallet_address
        ]
        if len(active_wallets) < 2:
            print("Insufficient active wallets for the attack simulation.")
            return
        receiver_public_key_1 = random.choice(active_wallets)
        active_wallets.remove(receiver_public_key_1)
        receiver_public_key_2 = random.choice(active_wallets)
        legitimate_transaction = {
            "sender": sender_wallet_address,
            "receiver": receiver_public_key_1,
            "amount": 10,
            "signature": None 
        }

        response_legit = requests.post(f"{node_address}/transaction_simulation", json=legitimate_transaction)
        if response_legit.status_code == 201:
            print("Legitimate transaction sent successfully.")
        else:
            print(f"Failed to send legitimate transaction: {response_legit.text}")
            return
        spam_transaction = {
            "sender": sender_wallet_address,
            "receiver": receiver_public_key_2,
            "amount": 10,
            "signature": None
        }
        min_delay = 5
        max_delay = 10
        delay = random.randint(min_delay, max_delay)
        time.sleep(delay)
        response_spam = requests.post(f"{node_address}/transaction", json=spam_transaction)
        if response_spam.status_code == 201:
            print("Conflicting transaction sent successfully.")
        else:
            print(f"Failed to send conflicting transaction: {response_spam.text}")

        print("Transaction pinning attack simulation complete.")

    except requests.exceptions.RequestException as e:
        print(f"Error during attack simulation: {e}")

def main():
    node_address = get_node_address()
    node_wallet_address = get_node_wallet_address(node_address)
    if not node_wallet_address:
        print("Error: Unable to retrieve wallet address.")
        return
    while True:
        print("1. Add transactions and mine a new block")
        print("2. View blockchain")
        print("3. Verify blockchain integrity")
        print("4. Resolve chain conflicts")
        print("5. Display your wallet details")
        print("6. View other nodes' wallets")
        print("7. Simulate a Transaction Pinning Attack")
        print("8. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            mine_new_block(node_address, node_wallet_address)
        elif choice == '2':
            display_blockchain_state(node_address)
        elif choice == '3':
            verify_blockchain_integrity(node_address)
        elif choice == '4':
            resolve_chain(node_address)
        elif choice == '5':
            display_my_wallet_details(node_address)
        elif choice == '6':
            display_wallet_details()
        elif choice == '7':
            simulate_pinning_attack(node_address, node_wallet_address)
        elif choice == '8':
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
