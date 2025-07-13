# config.py
import yaml
import torch.nn as nn
import torch.optim as optim

class Config:
    def __init__(self, path='config.yaml'):
        with open(path, 'r') as file:
            cfg = yaml.safe_load(file)

        self.num_clients = cfg['system']['num_clients']
        self.num_miners = cfg['system']['num_miners']
        self.epochs = cfg['system']['epochs']

        self.local_epochs = cfg['training']['local_epochs']
        self.batch_size = cfg['training']['batch_size']
        self.lr = cfg['training']['lr']
        self.momentum = cfg['training']['momentum']
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD

        self.difficulty = cfg['miner']['difficulty']
        self.h = cfg['miner']['h']
        self.delta = cfg['miner']['delta']
        self.nd = cfg['miner']['nd']
        self.T_wait = cfg['miner']['T_wait']
