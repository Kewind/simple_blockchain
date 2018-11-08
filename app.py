from flask import Flask, jsonify, request
from blockchain import Blockchain, Block
from config import Config
import requests
from uuid import uuid4
from urllib.parse import urlparse

def runServer(server_port, server_url='0.0.0.0'):
    node_address = str(uuid4()).replace('-', '')
    app = Flask(__name__)
    blockchain = Blockchain()

    @app.route(Config.MINE_BLOCK_URL, methods=['GET'])
    def mine_block():
        prev_block = blockchain.get_previous_block()
        prev_proof = prev_block.proof
        proof = blockchain.proof_of_work(prev_proof)
        prev_hash = blockchain.hash(prev_block)
        blockchain.add_transaction(sender=node_address, receiver='TestReceiver', amount=1000)
        block = blockchain.create_block(proof, prev_hash)
        response = {'message': 'Congrats! You have successfully added a block.',
                    'block': str(block)}
        return jsonify(response), 200

    @app.route(Config.GET_CHAIN_URL, methods=['GET'])
    def get_chain():
        response = {'chain': blockchain.get_chain_str()}
        print(response)
        return jsonify(response), 200

    @app.route(Config.IS_VALID_URL, methods=['GET'])
    def is_valid():
        is_valid = blockchain.validate_chain()
        response = {'is_valid': is_valid}
        return jsonify(response), 200

    @app.route(Config.ADD_TRANSACTION_URL, methods=['POST'])
    def add_transaction():
        json = request.get_json()
        index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
        response = {'message': 'Added transaction to block {}'.format(index)}
        return response, 201

    @app.route(Config.CONNECT_NODE_URL, methods=['POST'])
    def connect_node():
        json = request.get_json()
        nodes = json['nodes']
        if nodes is not None:
            for node in nodes:
                blockchain.add_node(node)
                response = {'message': 'Nodes connected!',
                            'node_count': len(blockchain.nodes)}
                return jsonify(response), 201
        return "No nodes", 400

    @app.route(Config.REPLACE_CHAIN_URL, methods=['GET'])
    def replace_chain():
        is_replaced = blockchain.replace_chain()
        if is_replaced:
            response = {'message': 'The chain was REPLACED.',
                        'chain': blockchain.chain}
        else:
            response = {'message': 'The chain was NOT REPLACED.',
                        'chain': blockchain.chain}
        return jsonify(reponse), 200

    app.run(host=server_url, port=server_port)
