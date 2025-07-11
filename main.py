from dataset import load_dataset, split_dataset
from client import Client
from miner import Miner
from network import broadcast_update, broadcast_block
import random
import time
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

training_cfg = config['training']
miner_cfg = config['miner']
system_cfg = config['system']

NUM_CLIENTS = system_cfg['num_clients']
NUM_MINERS = system_cfg['num_miners']
EPOCHS = system_cfg['epochs']

dataset = load_dataset()
partitions = split_dataset(dataset, NUM_CLIENTS)
clients = [Client(i, partitions[i]) for i in range(NUM_CLIENTS)]
miners = [Miner(i,
                difficulty=miner_cfg['difficulty'],
                h=miner_cfg['h'],
                delta=miner_cfg['delta'],
                nd=miner_cfg['nd'],
                T_wait=miner_cfg['T_wait']) for i in range(NUM_MINERS)]

for epoch in range(EPOCHS):
    print(f"\n====================== EPOCH {epoch+1} ======================")
    for client in clients:
        update = client.train(
            local_epochs=training_cfg['local_epochs'],
            batch_size=training_cfg['batch_size'],
            lr=training_cfg['lr'],
            momentum=training_cfg['momentum']
        )
        assigned_miner = random.choice([m for m in miners if m.miner_id != client.client_id % NUM_MINERS])
        print(f"Client {client.client_id} sends update to Miner {assigned_miner.miner_id}")
        assigned_miner.receive_update(update)
        broadcast_update(miners, update)

    time.sleep(1)

    mined = False
    for miner in miners:
        if miner.is_ready_to_mine() and not mined:
            block = miner.mine_block()
            success = broadcast_block(miners, block)
            if not success:
                print("Fork detected! Restarting epoch...")
            mined = True
            break
