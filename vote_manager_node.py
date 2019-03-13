# Authors: Sam Champer, Andi Nosler
# Partially uses some code from Daniel van Flymen (https://github.com/dvf/blockchain)
# along with additional code by the authors to implement the specific needs of a blockchain enabled election. 

from uuid import uuid4
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from blockchain import Blockchain
import requests
from time import sleep


# Instantiate the blockchain node in flask:
app = Flask(__name__)

# Generate a globally unique address for this node:
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain for this node:
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    """
    The app route to add a new coin/vote to the block.
    """
    # Run the proof of work algorithm to get the next proof:
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Receive a reward for finding the proof:
    # The sender is "0" to signify that this is a newly mined coin, not a transfer.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    # Forge the new block by adding it to the chain:
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Appp route for conducting a transfer of a coin (e.g. for voting for a recipient).
    """
    values = request.get_json(force=True)
    # Check that the required fields are in the POST:
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction on the blockchain:
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    """
    App route to call for a display of the entire chain.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Register a list of new nodes that share the blockchain.
    """
    values = request.get_json(force=True)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Call function to resolve conflicts between this node and other nodes.
    """
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


def initialize(source):
    """
    Link to a specified manager or miner node and import a blockchain from that node.
    """
    if source[-1] != '/':
        source += '/'
    blockchain.register_node(source)
    for i in range(5):
        try:
            response = requests.get(source + "get_nodes")
            if response.status_code:
                break
        except:
            print("   Connection to {} source failed, retrying. Attempt {} of 5".format(
                "default" if source == "http://127.0.0.1:4999/" else "specified", i + 1))
            sleep(2)
            i += 1
            if i == 4:
                print("\n  ***Connection failed. Please Register source and resolve chain manually.***")
                return
    if response.status_code == 200:
        # Nodes only respond 200 if they are peer nodes. This stuff won't touch the initialization server,
        # which simply shuts down after it passes on the blockchain.
        # For node in response:
        #      blockchain.register_node(node)
        #      Ask responding node to register this one in return.
        pass

    initialize_from_source = blockchain.resolve_conflicts()
    if initialize_from_source:
        print("\n  ***Local blockchain has been initialized to match the specified source!***\n")
    else:
        print("\n  ***Failed to import blockchain from the specified source. "
              "Try a different source or maybe just panic?***")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-src', '--source', default="http://127.0.0.1:4999/", type=str,
                        help='port to listen on')
    args = parser.parse_args()
    port = args.port
    source = args.source
    initialize(source)
    # Initialize the app on the desired port:
    app.run(host='0.0.0.0', port=port)