import time
import hashlib
from colorama import init, Fore
import json
import os
import random

# Initialize colorama
init(autoreset=True)

class Transaction:
    def __init__(self, sender, recipient, amount, speed='normal'):
        self.sender = sender
        self.recipient = recipient
        self.amount = float(amount)
        self.speed = speed  # Speed of transaction (normal, fast, etc.)

    @staticmethod
    def from_dict(data):
        """Créer une instance de Transaction à partir d'un dictionnaire."""
        return Transaction(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
            speed=data.get('speed', 'normal')
        )

    def __repr__(self):
        return f"{self.sender} -> {self.recipient}: {self.amount} KSC (Speed: {self.speed})"

    def calculate_gas_fee(self, base_gas_fee):
        """Calcul des frais de gaz en fonction du montant et de la vitesse."""
        amount_gas_fee = self.amount * 0.001  # 0.1% du montant
        speed_gas_fee = 0.002 if self.speed == 'fast' else 0
        return base_gas_fee + amount_gas_fee + speed_gas_fee

    def to_dict(self):
        """Convertir l'objet Transaction en dictionnaire."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "speed": self.speed
        }


class Block:
    def __init__(self, index, transactions, previous_hash, reward, timestamp=None, nonce=0):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.reward = reward

    def compute_hash(self):
        """Calculer le hash du bloc."""
        block_data = json.dumps(self.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_data).hexdigest()

    @staticmethod
    def from_dict(data):
        """Créer une instance de Block à partir d'un dictionnaire."""
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        return Block(
            index=data['index'],
            transactions=transactions,
            previous_hash=data['previous_hash'],
            reward=data['reward'],
            timestamp=data['timestamp'],
            nonce=data['nonce']
        )

    def to_dict(self):
        """Convertir l'objet Block en dictionnaire."""
        return {
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "reward": self.reward,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }

    def __repr__(self):
        return (f"Block #{self.index} [\n  Hash: {self.compute_hash()}\n  "
                f"Previous: {self.previous_hash}\n  Transactions: {self.transactions}\n  "
                f"Reward: {self.reward} KSC\n  Nonce: {self.nonce}\n  "
                f"Timestamp: {self.timestamp}\n]")


class Blockchain:
    def __init__(self, difficulty=4, reward=0.0001, max_supply=21000000, gas_fee=0.1, initial_balance=100, ksc_to_eur_rate=0.12):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.reward = reward
        self.max_supply = max_supply
        self.total_supply = 0
        self.gas_fee = gas_fee
        self.accounts = {"kerogscoinminer": initial_balance}
        self.ksc_to_eur_rate = ksc_to_eur_rate
        self.state_file = "blockchain_state.json"
        self.create_genesis_block()

    def create_genesis_block(self):
        """Créer le genesis block uniquement si la blockchain est vide."""
        if not self.chain:  # Vérifie si la chaîne est vide
            genesis_block = Block(0, [], "0" * 64, 0)
            self.chain.append(genesis_block)
            print(f"{Fore.GREEN}[+] Genesis block created.")
        else:
            print(f"{Fore.YELLOW}[!] Genesis block skipped: blockchain already exists.")
            
    def adjust_ksc_to_eur_rate(self):
        """
        Ajuste le taux de conversion KSC -> EUR en fonction de fluctuations réalistes et probabilistes.
        - Variation normale : -2% à +2%.
        - Variation rare : -6% à +6%.
        - Variation très rare : -10% à +10%.
        - Variation extrêmement rare : -20% à +20%.
        """
        base_adjustment = random.uniform(-0.02, 0.02)  # Variation normale (-2% à +2%)
        rare_adjustment = random.uniform(-0.06, 0.06) if random.random() < 0.1 else 0  # 10% de chance (-6% à +6%)
        very_rare_adjustment = random.uniform(-0.1, 0.1) if random.random() < 0.01 else 0  # 1% de chance (-10% à +10%)
        extremely_rare_adjustment = random.uniform(-0.2, 0.2) if random.random() < 0.001 else 0  # 0.1% de chance (-20% à +20%)

        total_adjustment = base_adjustment + rare_adjustment + very_rare_adjustment + extremely_rare_adjustment

        # Ajuster en fonction du nombre de transactions en attente (indicateur de demande/envoi)
        demand_factor = len(self.pending_transactions) / 100.0  # Exemple : +1% par 100 transactions en attente
        total_adjustment += demand_factor

        # Mise à jour du taux
        self.ksc_to_eur_rate += self.ksc_to_eur_rate * total_adjustment

        # S'assurer que le taux reste positif
        self.ksc_to_eur_rate = max(0.01, self.ksc_to_eur_rate)  # Taux minimal de 0.01 EUR/KSC

        print(f"[!] Adjusted KSC to EUR rate: {self.ksc_to_eur_rate:.4f} (Change: {total_adjustment * 100:.2f}%)")

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        sender_balance = self.get_balance(transaction.sender)
        gas_fee = transaction.calculate_gas_fee(self.gas_fee)
        total_required = transaction.amount + gas_fee

        if sender_balance < total_required:
            print(f"{Fore.RED}[-] Transaction rejected: insufficient funds for {transaction.sender} ({sender_balance} KSC)")
            return False

        self.accounts[transaction.sender] -= total_required
        self.pending_transactions.append(transaction)
        print(f"{Fore.GREEN}[+] Transaction added: {transaction}")
        return True

    def get_balance(self, address):
        return self.accounts.get(address, 0)

    def mine_pending_transactions(self, miner_address):
        if self.total_supply + self.reward > self.max_supply:
            print(f"{Fore.RED}[-] Mining reward exceeds maximum supply of KSC!")
            return False

        self.pending_transactions.append(Transaction("System", miner_address, self.reward))
        
        self.adjust_ksc_to_eur_rate()

        new_block = Block(
            index=self.get_next_block_index(),  # Utilise l'index suivant
            transactions=self.pending_transactions,
            previous_hash=self.get_last_block().compute_hash(),
            reward=self.reward
        )

        while not new_block.compute_hash().startswith("0" * self.difficulty):
            new_block.nonce += 1

        self.chain.append(new_block)
        self.total_supply += self.reward
        self.pending_transactions = []
        print(f"{Fore.GREEN}[+] Block mined successfully: {new_block}")
        return True

    def save_state(self):
        """Sauvegarder l'état de la blockchain."""
        state = {
            "ksc_to_eur_rate": self.ksc_to_eur_rate,
            "accounts": self.accounts,
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions]
        }
        with open(self.state_file, "w") as file:
            json.dump(state, file, indent=4)
        print("[!] State saved.")

    def load_state(self):
        """Charger l'état de la blockchain depuis un fichier JSON."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as file:
                state = json.load(file)
                self.ksc_to_eur_rate = state.get("ksc_to_eur_rate", self.ksc_to_eur_rate)
                self.accounts = state.get("accounts", self.accounts)
                self.chain = [Block.from_dict(block) for block in state.get("chain", [])]
                self.pending_transactions = [Transaction.from_dict(tx) for tx in state.get("pending_transactions", [])]
                print(f"{Fore.GREEN}[+] Blockchain state loaded. Total blocks: {len(self.chain)}")
        else:
            print(f"{Fore.YELLOW}[!] No previous state found. Starting fresh.")
            self.create_genesis_block()
            
    def get_next_block_index(self):
        """Retourne l'index du prochain bloc."""
        return len(self.chain)
    
    def ksc_to_eur(self, ksc_value, rate_per_k=None):
        """
        Convertit une valeur KSC en EUR en utilisant le taux de conversion actuel 
        (ksc_to_eur_rate) ou un taux donné (1 K€ = rate_per_k KSC).
        
        :param ksc_value: Valeur en KSC à convertir.
        :param rate_per_k: (Optionnel) Nombre de KSC nécessaires pour 1 K€. 
                           Si None, utilise self.ksc_to_eur_rate.
        :return: La valeur en EUR.
        """
        if rate_per_k is not None:
            ksc_to_eur_rate = 1000 / rate_per_k  # Conversion personnalisée
        else:
            ksc_to_eur_rate = self.ksc_to_eur_rate  # Taux dynamique de la blockchain
        
        eur_value = ksc_value * ksc_to_eur_rate
        print(f"[+] {ksc_value} KSC équivaut à {eur_value:.2f} EUR au taux de conversion {ksc_to_eur_rate:.4f} EUR par KSC.")
        return eur_value