def broadcast_update(miners, update):
    print(f"Broadcasting update from Client {update['client_id']} to all miners...")
    for miner in miners:
        miner.receive_update(update)

def broadcast_block(miners, block):
    print(f"Broadcasting mined Block {block.index} to all miners...")
    for miner in miners:
        if block.hash != block.compute_hash():
            print(f"Miner {miner.miner_id} rejected block due to hash mismatch.")
            return False
        if miner.blockchain:
            if block.prev_hash != miner.blockchain[-1].hash:
                print(f"Miner {miner.miner_id} detected a fork.")
                return False
        miner.blockchain.append(block)
    return True