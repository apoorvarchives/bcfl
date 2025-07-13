# dataset.py
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split

def load_datasets(config):
    transform = transforms.Compose([transforms.ToTensor()])
    full_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)

    # Split dataset equally among clients
    client_data_size = len(full_dataset) // config.num_clients
    client_datasets = random_split(full_dataset, [client_data_size] * config.num_clients)

    train_loaders = [
        DataLoader(client_dataset, batch_size=config.batch_size, shuffle=True)
        for client_dataset in client_datasets
    ]

    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

    return train_loaders, test_loader
