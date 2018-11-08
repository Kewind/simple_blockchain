from config import Config
import datetime
import hashlib
import json
from urllib.parse import urlparse

class Block:

    def __init__(self, index, proof, previous_hash, Transaction):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.proof = proof
        self.previous_hash = previous_hash
        self.Transaction = Transaction

    def __repr__(self):
        return "Block #{}, timestamp = {}, proof = {}, previous_hash = {}".format(self.index, self.timestamp,\
                                                                                self.proof, self.previous_hash)
class Transaction:

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.rceiver = receiver
        self.amount = amount

class Blockchain:

    def __init__(self):
        self.chain = []
        self.Transaction = []
        self.create_block(proof=1, previous_hash='0')
        self.target_leading_zeros = Config.INIT_TARGET_LEADING_ZEROS
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        new_block = Block(len(self.chain) + 1, proof, previous_hash, self.Transaction)
        self.Transaction = []
        self.chain.append(new_block)
        return new_block

    def get_previous_block(self):
        return self.chain[-1]

    def is_below_target(self, proof, prev_proof):
        hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
        return hash_operation[:len(self.target_leading_zeros)] == self.target_leading_zeros

    def proof_of_work(self, previous_proof):
        new_proof = 0
        valid_proof = False
        while not valid_proof:
            new_proof += 1
            valid_proof = self.is_below_target(new_proof, previous_proof)
        return new_proof

    @staticmethod
    def hash(block):
        encoded_block = json.dumps(str(block), sort_keys = True).encode()
        encoded_block = hashlib.sha256(encoded_block).hexdigest()
        return encoded_block

    def validate_chain(self, chain):
        for i in range(1, len(chain)):
            current_block = chain[i]
            prev_block = chain[i-1]
            if current_block.previous_hash != Blockchain.hash(prev_block):
                return False
            is_valid = self.is_below_target(current_block.proof, prev_block.proof)
            if not is_valid:
                return False
        return True

    def get_chain_str(self):
        chain_str = list(map(lambda x: str(x), self.chain))
        return chain_str

    def add_transaction(self, sender, receiver, amount):
        new_transaction = Transaction(sender, receiver, amount)
        self.Transaction.append(new_transaction)
        prev_block = self.get_previous_block()
        return prev_block.index + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get('http://' + node + Config.GET_CHAIN_URL)
            if response.status_code == 200:
                response = response.json()
                length = response['length']
                chain = response['chain']
                if length > max_length and self.validate_chain(chain):
                    longest_chain = chain
                    max_length = length
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def serialize(self):
        return json.dumps(self.__dict__, default=lambda x: x.__dict__ if hasattr(x, '__dict__') else str(x))

    @staticmethod
    def deserialize(properties):
        blockchain = Blockchain()
        blockchain.__dict__ = json.loads(properties)
        return blockchain
