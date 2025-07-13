import copy
import time
from model import initialize_model, aggregate_updates

class Client:
    def __init__(self, client_id, train_loader, config):
        self.id = client_id
        self.train_loader = train_loader
        self.config = config
        self.local_model = initialize_model()

    def train(self):
        optimizer = self.config.optimizer(self.local_model.parameters(), lr=self.config.lr, momentum=self.config.momentum)
        self.local_model.train()

        start = time.time()
        for _ in range(self.config.local_epochs):
            for data, target in self.train_loader:
                optimizer.zero_grad()
                output = self.local_model(data)
                loss = self.config.loss_fn(output, target)
                loss.backward()
                optimizer.step()
        end = time.time()

        print(f"[Client {self.id}] Trained locally in {round(end - start, 2)}s")
        return self.local_model.state_dict(), round(end - start, 2), len(self.train_loader.dataset)

    def update_global_model(self, block):
        print(f"[Client {self.id}] Updating global model using block from Miner {block.miner_id}")
        self.local_model.load_state_dict(aggregate_updates(block.model_updates))

