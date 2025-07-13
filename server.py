import json
from block import genesis_block

class Server:
    def __init__(self, config):
        self.chain = [genesis_block()]
        self.config = config

    def add_block(self, block):
        self.chain.append(block)
        print(f"[Server] Block added to chain from Miner {block.miner_id}. Total blocks: {len(self.chain)}")

    def save_chain_to_file(self, filename):
        json_chain = [block.to_dict() for block in self.chain]
        with open(filename, 'w') as f:
            json.dump(json_chain, f, indent=4)
        print(f"[Server] Blockchain saved to {filename}")
