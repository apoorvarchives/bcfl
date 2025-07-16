
# server.py
from chain import Blockchain
from block import genesis_block
import json

class Server:
    def __init__(self, config):
        # Create a genesis block and initialize the fork-aware blockchain
        g = genesis_block()
        # difficulty is handled by miners; chain logic uses work=1 per block
        self.blockchain = Blockchain(g, difficulty=config.difficulty)
        self.config = config

    def add_block(self, block):
        """
        Add a mined block to the fork-aware blockchain.
        Handles forks and orphan blocks internally.
        """
        added = self.blockchain.add_block(block)
        if added:
            print(f"[Server] Block {block.hash[:8]} added by Miner {block.miner_id}. Height={self.blockchain.get_height()}")
        else:
            print(f"[Server] Block {block.hash[:8]} is orphaned (parent missing).")

    def get_chain(self):
        """Return the canonical chain (longest chain)."""
        return self.blockchain.chain

    def save_chain_to_file(self, filename):
        """Save canonical chain to a JSON file."""
        json_chain = []
        for b in self.blockchain.chain:
            json_chain.append({
                "miner_id": b.miner_id,
                "timestamp": b.timestamp,
                "nonce": b.nonce,
                "hash": b.hash,
                "previous_hash": b.previous_hash
            })
        with open(filename, 'w') as f:
            json.dump(json_chain, f, indent=4)
        print(f"[Server] Blockchain saved to {filename}")
