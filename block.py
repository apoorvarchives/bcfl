import hashlib
import json
import time

class Block:
    def __init__(self, index, prev_hash, updates, timestamp=None):
        self.index = index
        self.prev_hash = prev_hash
        self.updates = updates  # list of dicts: {client_id, weights, gradients, T_local}
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_str = json.dumps({
            "index": self.index,
            "prev_hash": self.prev_hash,
            "updates": [u['client_id'] for u in self.updates],
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()