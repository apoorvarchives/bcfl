import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, random_split

def load_dataset():
    transform = transforms.Compose([transforms.ToTensor()])
    dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    return dataset

def split_dataset(dataset, num_clients):
    return random_split(dataset, [len(dataset) // num_clients] * num_clients)
