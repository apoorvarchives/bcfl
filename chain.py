import hashlib
import json
import time
from typing import Dict, List

class Block:
    def __init__(self, index, previous_hash, timestamp, data, miner_id, nonce=0, difficulty=4):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data          # store model updates or payload
        self.miner_id = miner_id
        self.nonce = nonce
        self.difficulty = difficulty  # allow variable difficulty if needed
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "miner_id": self.miner_id,
            "nonce": self.nonce,
            "difficulty": self.difficulty
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine(self, difficulty: int):
        """Perform Proof-of-Work until hash has required prefix."""
        self.difficulty = difficulty
        prefix = "0" * difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash

    def work(self):
        """Return work contributed by this block. With fixed difficulty, each block = 1 work."""
        return 1


class Blockchain:
    def __init__(self, genesis_block: Block, difficulty=4):
        self.difficulty = difficulty
        # tip_hash -> branch (list of blocks)
        self.branches: Dict[str, List[Block]] = {genesis_block.hash: [genesis_block]}
        # canonical chain (best branch)
        self.chain: List[Block] = [genesis_block]
        # orphan blocks that didn’t fit yet
        self.orphans: Dict[str, Block] = {}

    def add_block(self, block: Block):
        """
        Add a block. If it extends an existing tip, create or extend a branch.
        Otherwise, store as orphan.
        """
        parent_hash = block.previous_hash
        extended = False

        # Try to attach to one of the known branches
        for tip_hash, branch in list(self.branches.items()):
            if branch[-1].hash == parent_hash:
                # create a new branch based on this one
                new_branch = list(branch)
                new_branch.append(block)

                # remove old tip and add new tip
                if tip_hash in self.branches:
                    del self.branches[tip_hash]
                self.branches[block.hash] = new_branch

                print(f"[CHAIN] Added block {block.hash[:8]} (Miner {block.miner_id}) height={len(new_branch)}")
                extended = True
                break

        if not extended:
            # parent not found -> orphan
            if block.previous_hash:
                print(f"[CHAIN] Orphan block {block.hash[:8]} (parent {block.previous_hash[:8]} not found yet)")
            else:
                print(f"[CHAIN] Orphan block {block.hash[:8]} (no parent hash provided)")
            self.orphans[block.hash] = block
            return False

        # after adding, try to resolve conflicts
        self.resolve_conflicts()
        return True

    def resolve_conflicts(self):
        """
        Resolve forks by selecting the branch with the most cumulative work.
        """
        best_branch = self.chain
        best_work = self.calculate_cumulative_work(best_branch)

        for branch in self.branches.values():
            branch_work = self.calculate_cumulative_work(branch)
            if branch_work > best_work:
                best_branch = branch
                best_work = branch_work

        if best_branch != self.chain:
            self.chain = best_branch
            print(f"[CHAIN] Fork resolved. Canonical length={len(self.chain)}")

    def calculate_cumulative_work(self, branch: List[Block]) -> int:
        """
        Calculate total work for a branch. If difficulty varies, sum actual work.
        """
        return sum(b.work() for b in branch)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_height(self) -> int:
        return len(self.chain)

































# import hashlib
# import json
# from typing import Dict, List

# class Block:
#     def __init__(self, index, previous_hash, timestamp, data, miner_id, nonce=0, difficulty=4):
#         self.index = index
#         self.previous_hash = previous_hash
#         self.timestamp = timestamp
#         self.data = data          # store model updates or payload
#         self.miner_id = miner_id
#         self.nonce = nonce
#         self.difficulty = difficulty
#         self.hash = self.compute_hash()

#     def compute_hash(self):
#         block_string = json.dumps({
#             "index": self.index,
#             "previous_hash": self.previous_hash,
#             "timestamp": self.timestamp,
#             "data": self.data,
#             "miner_id": self.miner_id,
#             "nonce": self.nonce,
#             "difficulty": self.difficulty
#         }, sort_keys=True).encode()
#         return hashlib.sha256(block_string).hexdigest()

#     def mine(self, difficulty: int):
#         self.difficulty = difficulty
#         prefix = "0" * difficulty
#         while not self.hash.startswith(prefix):
#             self.nonce += 1
#             self.hash = self.compute_hash()
#         return self.hash

#     def work(self):
#         return 1  # each block counts as 1 unit of work


# class Blockchain:
#     def __init__(self, genesis_block: Block, difficulty=4):
#         self.difficulty = difficulty
#         self.branches: Dict[str, List[Block]] = {genesis_block.hash: [genesis_block]}
#         self.chain: List[Block] = [genesis_block]
#         self.orphans: Dict[str, Block] = {}

#     def add_block(self, block: Block):
#         parent_hash = block.previous_hash
#         extended = False

#         # Try to attach to one of the known branches
#         for tip_hash, branch in list(self.branches.items()):
#             if branch[-1].hash == parent_hash:
#                 new_branch = list(branch)
#                 new_branch.append(block)

#                 # update branches
#                 if tip_hash in self.branches:
#                     del self.branches[tip_hash]
#                 self.branches[block.hash] = new_branch

#                 print(f"   ✅ Miner {block.miner_id}: Block {block.hash[:8]} added | Height: {len(new_branch)}")
#                 extended = True
#                 break

#         if not extended:
#             # parent not found -> orphan
#             status = f"(parent {parent_hash[:8]} not found yet)" if parent_hash else "(no parent hash)"
#             print(f"   ❌ Miner {block.miner_id}: Block {block.hash[:8]} orphaned {status}")
#             self.orphans[block.hash] = block
#             return False

#         self.resolve_conflicts()
#         return True

#     def resolve_conflicts(self):
#         best_branch = self.chain
#         best_work = self.calculate_cumulative_work(best_branch)

#         for branch in self.branches.values():
#             branch_work = self.calculate_cumulative_work(branch)
#             if branch_work > best_work:
#                 best_branch = branch
#                 best_work = branch_work

#         if best_branch != self.chain:
#             self.chain = best_branch
#             print(f"🌿 [CHAIN] Fork resolved. Canonical length={len(self.chain)}")

#     def calculate_cumulative_work(self, branch: List[Block]) -> int:
#         return sum(b.work() for b in branch)

#     def get_last_block(self) -> Block:
#         return self.chain[-1]

#     def get_height(self) -> int:
#         return len(self.chain)
