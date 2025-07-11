import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from model import CNNModel
import time

class Client:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.model = CNNModel()
        self.dataset = dataset

    def train(self, local_epochs=1, batch_size=20, lr=0.01, momentum=0.9):
        self.model.train()
        loader = DataLoader(self.dataset, batch_size=batch_size, shuffle=True)
        optimizer = optim.SGD(self.model.parameters(), lr=lr, momentum=momentum)
        loss_fn = torch.nn.CrossEntropyLoss()

        start = time.time()
        for _ in range(local_epochs):
            for x, y in loader:
                optimizer.zero_grad()
                output = self.model(x)
                loss = loss_fn(output, y)
                loss.backward()
                optimizer.step()
        end = time.time()

        weights = [p.data.tolist() for p in self.model.parameters()]
        print(f"Client {self.client_id} Weights Sample: {str(weights[0][:2])}")

        update = {
            'client_id': self.client_id,
            'weights': weights,
            'gradients': [],
            'T_local': end - start
        }
        return update
