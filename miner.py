from block import Block
import time
import numpy as np

class Miner:
    def __init__(self, miner_id, difficulty='000', h=5, delta=0.2, nd=10, T_wait=10):
        self.miner_id = miner_id
        self.candidate_block = []
        self.blockchain = []
        self.difficulty = difficulty
        self.h = h
        self.delta = delta
        self.nd = nd
        self.T_wait = T_wait
        self.first_update_time = None

    def verify_update(self, update):
        print(f"Miner {self.miner_id} verifying update from Client {update['client_id']}")
        return True

    def receive_update(self, update):
        if not self.first_update_time:
            self.first_update_time = time.time()
        if self.verify_update(update):
            print(f"Miner {self.miner_id} added update from Client {update['client_id']} to candidate block.")
            self.candidate_block.append(update)
            print(f"Current Candidate Block at Miner {self.miner_id}:")
            for u in self.candidate_block:
                print(f"  Client {u['client_id']}, T_local: {u['T_local']:.2f}s")

    def is_ready_to_mine(self):
        if len(self.candidate_block) >= self.h + int(self.delta * self.nd):
            print(f"Miner {self.miner_id} candidate block size threshold reached.")
            return True
        if self.first_update_time and (time.time() - self.first_update_time > self.T_wait):
            print(f"Miner {self.miner_id} candidate block timeout reached.")
            return True
        return False

    def aggregate_model(self):
        print(f"Miner {self.miner_id} aggregating global model from block updates...")
        num_updates = len(self.candidate_block)
        if num_updates == 0:
            return []

        agg_weights = None
        for update in self.candidate_block:
            weights = update['weights']
            weights_tensor = [np.array(w) for w in weights]
            if agg_weights is None:
                agg_weights = weights_tensor
            else:
                for i in range(len(agg_weights)):
                    agg_weights[i] += weights_tensor[i]

        agg_weights = [w / num_updates for w in agg_weights]
        print(f"Global model weights sample: {agg_weights[0][:2]}")
        return agg_weights

    def mine_block(self):
        index = len(self.blockchain)
        prev_hash = self.blockchain[-1].hash if self.blockchain else '0'*64
        block = Block(index, prev_hash, self.candidate_block)

        print(f"Miner {self.miner_id} started mining Block {index}...")
        while not block.hash.startswith(self.difficulty):
            block.nonce += 1
            block.hash = block.compute_hash()

        print(f"Miner {self.miner_id} mined Block {index} with hash {block.hash}")
        self.blockchain.append(block)
        self.aggregate_model()
        self.candidate_block = []
        self.first_update_time = None
        return block