# --------------------------- miner.py ---------------------------
import time
import hashlib
from block import Block

class Miner:
    def __init__(self, miner_id, config):
        self.id = miner_id
        self.difficulty = config.difficulty
        self.received_updates = []
        self.h = config.h
        self.delta = config.delta
        self.nd = config.nd
        self.T_wait = config.T_wait

    def receive_update(self, client_id, model_update, comp_time, sample_count):
        self.received_updates.append((client_id, model_update, comp_time, sample_count))

    def cross_verify(self, all_miners):
        known_clients = set(update[0] for update in self.received_updates)
        for miner in all_miners:
            if miner.id != self.id:
                for update in miner.received_updates:
                    client_id = update[0]
                    if client_id not in known_clients:
                        self.received_updates.append(update)
                        known_clients.add(client_id)
        print(f"[Miner {self.id}] Verified {len(self.received_updates)} updates")

    def mine_block(self, prev_hash):
        required_size = int(self.h + self.delta * self.nd)
        print(f"[Miner {self.id}] Waiting to collect {required_size} updates or until timeout {self.T_wait}s")

        start_time = time.time()
        while len(self.received_updates) < required_size:
            if time.time() - start_time >= self.T_wait:
                print(f"[Miner {self.id}] Timeout reached with {len(self.received_updates)} updates. Proceeding to PoW...")
                break
            time.sleep(0.1)  # brief sleep to simulate waiting

        print(f"[Miner {self.id}] Starting PoW with {len(self.received_updates)} updates...")
        nonce = 0
        while True:
            timestamp = time.time()
            block = Block(self.id, self.received_updates, prev_hash, nonce, timestamp)
            block_hash = block.compute_hash()
            if block_hash.startswith(self.difficulty):
                block.hash = block_hash
                print(f"[Miner {self.id}] Found valid block with nonce {nonce} at {block.hash}")
                return block
            nonce += 1
