from client import Client
from miner import Miner
from server import Server
from config import Config
from dataset import load_datasets
from model import evaluate
import random
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt

# Worker function to mine block in parallel
def mine_worker(miner, prev_hash, queue):
    block = miner.mine_block(prev_hash)
    queue.put(block)

if __name__ == '__main__':
    config = Config()
    train_loaders, test_loader = load_datasets(config)

    clients = [Client(i, train_loaders[i], config) for i in range(config.num_clients)]
    miners = [Miner(i, config) for i in range(config.num_miners)]
    server = Server(config)

    test_accuracies = []

    for epoch in range(config.epochs):
        print(f"\n====================== EPOCH {epoch + 1} ======================")

        # STEP 1-2: Clients train locally and upload to random miners
        miner_assignments = {m.id: [] for m in miners}
        for client in clients:
            selected_miner = random.choice(miners)
            update, comp_time, sample_count = client.train()
            print(f"[Client {client.id}] ➜ Miner {selected_miner.id} | samples: {sample_count} | time: {comp_time}s")
            miner_assignments[selected_miner.id].append((client.id, update, comp_time, sample_count))
            selected_miner.receive_update(client.id, update, comp_time, sample_count)

        # STEP 3: Miners cross-verify
        for miner in miners:
            miner.cross_verify(miners)

        # STEP 4-5: Parallel PoW mining using multiprocessing
        queue = Queue()
        processes = []

        for miner in miners:
            p = Process(target=mine_worker, args=(miner, server.chain[-1].hash, queue))
            p.start()
            processes.append(p)

        blocks = [queue.get() for _ in miners]
        for p in processes:
            p.join()

        # Select block with earliest timestamp
        blocks.sort(key=lambda b: b.timestamp)
        successful_block = blocks[0]
        print(f"[Server] Miner {successful_block.miner_id} wins the fork and broadcasts block.")

        # STEP 6: Devices download the block
        for client in clients:
            client.update_global_model(successful_block)

        server.add_block(successful_block)

        # Evaluate and print accuracy
        global_model_state = successful_block.model_updates[0][1].copy()
        for key in global_model_state:
            global_model_state[key] = sum(update[1][key] * update[3] for update in successful_block.model_updates) / sum(update[3] for update in successful_block.model_updates)

        acc = evaluate(global_model_state, test_loader, config)
        print(f"[Eval] Global Model Accuracy after Epoch {epoch + 1}: {acc:.2f}%")
        test_accuracies.append(acc)

    # Save chain to file
    server.save_chain_to_file("chain.json")
    print("\n[✓] BlockFL Training Complete and chain saved to chain.json")

    # Plot accuracy
    plt.plot(range(1, config.epochs + 1), test_accuracies, marker='o')
    plt.xlabel("Epoch")
    plt.ylabel("Test Accuracy (%)")
    plt.title("Global Model Accuracy per Epoch")
    plt.grid(True)
    plt.savefig("accuracy_plot.png")
    plt.show()