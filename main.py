from helpers.blockchain import *
import random


def generate_fake_data():
    blockchain = Blockchain()
    blockchain.load_state()
    
    # Faire des transactions
    for _ in range(random.randint(1, 100)):
        transaction_amount = random.uniform(0.01, 0.05)
        transaction_amount_str = str(transaction_amount)
        blockchain.add_transaction(Transaction("kerogscoinminer", "Kerogs", transaction_amount_str, "medium"))
        
        # 30% chance to mine
        if random.random() < 0.3:
            blockchain.mine_pending_transactions("kerogscoinminer")
        
    blockchain.ksc_to_eur(1)
    blockchain.save_state()


# Testing the updated Blockchain
if __name__ == "__main__":
    generate_fake_data()