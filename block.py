# import hashlib
# import json
# import time

# class Block:
#     def __init__(self, miner_id, model_updates, previous_hash, nonce=0, timestamp=None):
#         self.miner_id = miner_id
#         self.model_updates = model_updates  # list of (client_id, update_dict, comp_time, sample_count)
#         self.previous_hash = previous_hash
#         self.nonce = nonce
#         self.timestamp = timestamp
#         self.hash = None

#     def to_dict(self):
#         return {
#             "miner_id": self.miner_id,
#             "timestamp": self.timestamp,
#             "nonce": self.nonce,
#             "hash": self.hash,
#             "previous_hash": self.previous_hash,
#             "num_updates": len(self.model_updates),
#             "clients": [uid for uid, *_ in self.model_updates]
#         }

#     def compute_hash(self):
#         data = json.dumps({
#             'miner_id': self.miner_id,
#             'previous_hash': self.previous_hash,
#             'nonce': self.nonce,
#             'timestamp': self.timestamp
#         }, sort_keys=True).encode()
#         return hashlib.sha256(data).hexdigest()

# def genesis_block():
#     return Block(miner_id=-1, model_updates=[], previous_hash="0", nonce=0, timestamp=time.time())














import hashlib
import json
import time

class Block:
    def __init__(self, miner_id, model_updates, previous_hash, nonce=0, timestamp=None):
        self.miner_id = miner_id
        # list of tuples: (client_id, update_dict, comp_time, sample_count)
        self.model_updates = model_updates
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = timestamp
        self.hash = None  # will be set after successful PoW

    def to_dict(self):
        return {
            "miner_id": self.miner_id,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash,
            "previous_hash": self.previous_hash,
            "num_updates": len(self.model_updates),
            "clients": [uid for uid, *_ in self.model_updates]
        }

    def compute_hash(self):
        data = json.dumps({
            'miner_id': self.miner_id,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'timestamp': self.timestamp
        }, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()

    def work(self):
        """
        Return work contributed by this block.
        With fixed difficulty, each block counts as 1 unit of work.
        """
        return 1


def genesis_block():
    return Block(miner_id=-1, model_updates=[], previous_hash="0", nonce=0, timestamp=time.time())
