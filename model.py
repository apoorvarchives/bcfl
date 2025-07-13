import torch.nn as nn
import torch.nn.functional as F
import torch
import copy

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        return self.fc2(x)

def initialize_model():
    return SimpleCNN()

def aggregate_updates(model_updates):
    num_samples = sum(s for _, _, _, s in model_updates)
    agg = copy.deepcopy(model_updates[0][1])
    for key in agg.keys():
        agg[key] = sum(update[1][key] * update[3] for update in model_updates) / num_samples
    return agg

def evaluate(state_dict, test_loader, config):
    model = initialize_model()
    model.load_state_dict(state_dict)
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    return 100.0 * correct / total
