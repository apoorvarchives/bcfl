# main.py
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

        last_block = server.get_chain()[-1]  # get tip of canonical chain
        prev_hash = last_block.hash

        for miner in miners:
            p = Process(target=mine_worker, args=(miner, prev_hash, queue))
            p.start()
            processes.append(p)

        blocks = [queue.get() for _ in miners]
        for p in processes:
            p.join()

        # STEP 5b: Add *all* blocks to the chain to let fork resolution decide
        for b in blocks:
            server.add_block(b)

        # After fork resolution, canonical chain tip is:
        canonical_tip = server.get_chain()[-1]
        print(f"[Server] Canonical chain tip after fork resolution: {canonical_tip.hash[:8]} (Miner {canonical_tip.miner_id})")

        # STEP 6: Devices download the block (canonical tip)
        for client in clients:
            client.update_global_model(canonical_tip)

        # Evaluate and print accuracy
        global_model_state = canonical_tip.model_updates[0][1].copy()
        for key in global_model_state:
            global_model_state[key] = sum(update[1][key] * update[3] for update in canonical_tip.model_updates) / sum(update[3] for update in canonical_tip.model_updates)

        acc = evaluate(global_model_state, test_loader, config)
        print(f"[Eval] Global Model Accuracy after Epoch {epoch + 1}: {acc:.2f}%")
        test_accuracies.append(acc)

    # Save canonical chain
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
























# from client import Client
# from miner import Miner
# from server import Server
# from config import Config
# from dataset import load_datasets
# from model import evaluate
# import random
# from multiprocessing import Process, Queue
# import matplotlib.pyplot as plt

# # Worker function to mine block in parallel
# def mine_worker(miner, prev_hash, queue):
#     block = miner.mine_block(prev_hash)
#     queue.put(block)

# if __name__ == '__main__':
#     config = Config()
#     train_loaders, test_loader = load_datasets(config)

#     clients = [Client(i, train_loaders[i], config) for i in range(config.num_clients)]
#     miners = [Miner(i, config) for i in range(config.num_miners)]
#     server = Server(config)

#     test_accuracies = []

#     for epoch in range(config.epochs):
#         print(f"\n====================== EPOCH {epoch + 1} ======================")

#         # STEP 1-2: Clients train locally and upload to random miners
#         for client in clients:
#             selected_miner = random.choice(miners)
#             update, comp_time, sample_count = client.train()
#             print(f"[Client {client.id}] ➜ Miner {selected_miner.id} | samples: {sample_count} | time: {comp_time:.2f}s")
#             selected_miner.receive_update(client.id, update, comp_time, sample_count)

#         # STEP 3: Miners cross-verify
#         for miner in miners:
#             miner.cross_verify(miners)

#         # STEP 4-5: Parallel PoW mining using multiprocessing
#         queue = Queue()
#         processes = []

#         last_block = server.get_chain()[-1]
#         prev_hash = last_block.hash

#         print("\n⛏️  Mining Results:")
#         for miner in miners:
#             p = Process(target=mine_worker, args=(miner, prev_hash, queue))
#             p.start()
#             processes.append(p)

#         blocks = [queue.get() for _ in miners]
#         for p in processes:
#             p.join()

#         # Add all mined blocks for fork resolution
#         for b in blocks:
#             server.add_block(b)

#         # STEP 6: Devices download the block (canonical tip)
#         tip = server.get_chain()[-1]
#         for client in clients:
#             client.update_global_model(tip)

#         # Evaluate and print accuracy
#         global_model_state = tip.model_updates[0][1].copy()
#         for key in global_model_state:
#             global_model_state[key] = sum(update[1][key] * update[3] for update in tip.model_updates) / sum(update[3] for update in tip.model_updates)

#         acc = evaluate(global_model_state, test_loader, config)

#         print(f"\n🌳 Canonical Chain Tip: {tip.hash[:8]} | Height: {len(server.get_chain())}")
#         print(f"📈 Global Model Accuracy: {acc:.2f}%")

#         test_accuracies.append(acc)

#     # Save chain to file
#     server.save_chain_to_file("chain.json")
#     print("\n[✓] BlockFL Training Complete and chain saved to chain.json")

#     # Plot accuracy
#     plt.plot(range(1, config.epochs + 1), test_accuracies, marker='o')
#     plt.xlabel("Epoch")
#     plt.ylabel("Test Accuracy (%)")
#     plt.title("Global Model Accuracy per Epoch")
#     plt.grid(True)
#     plt.savefig("accuracy_plot.png")
#     plt.show()
