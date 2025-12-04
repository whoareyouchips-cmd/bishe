# scripts/train.py
# 需求: pip install torch torchvision numpy tqdm

import argparse
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from scripts.dataset import KeypointSequenceDataset
import glob
from tqdm import tqdm

class LSTMClassifier(nn.Module):
    def __init__(self, input_dim=126, hidden=256, num_layers=2, num_classes=100):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden, num_layers=num_layers, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden*2, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )
    def forward(self, x, mask=None):
        # x: [B, T, F]
        out, _ = self.lstm(x)  # [B, T, H*2]
        # pool by masked mean
        if mask is not None:
            mask = mask.unsqueeze(-1)  # [B, T, 1]
            out = (out * mask).sum(1) / (mask.sum(1)+1e-6)
        else:
            out = out.mean(1)
        logits = self.fc(out)
        return logits

def train_epoch(model, opt, criterion, loader, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    for x,y,mask in tqdm(loader):
        x,y,mask = x.to(device), y.to(device), mask.to(device)
        logits = model(x, mask)
        loss = criterion(logits, y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        total_loss += loss.item()*x.size(0)
        preds = logits.argmax(dim=1)
        correct += (preds==y).sum().item()
        total += x.size(0)
    return total_loss/total, correct/total

def val_epoch(model, criterion, loader, device):
    model.eval()
    total_loss = 0
    correct=0; total=0
    with torch.no_grad():
        for x,y,mask in loader:
            x,y,mask = x.to(device), y.to(device), mask.to(device)
            logits = model(x, mask)
            loss = criterion(logits, y)
            total_loss += loss.item()*x.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds==y).sum().item()
            total += x.size(0)
    return total_loss/total, correct/total

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_ds = KeypointSequenceDataset(args.data_dir, max_len=args.max_len)
    # share label_map with val if provided
    val_files = glob.glob(os.path.join(args.val_dir, "*.npz")) if args.val_dir else []
    val_ds = KeypointSequenceDataset(args.val_dir, label_map=train_ds.label_map, max_len=args.max_len) if args.val_dir else None

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=2) if val_ds else None

    input_dim = np.load(train_ds.files[0])['keypoints'].shape[1]
    num_classes = len(train_ds.label_map)
    model = LSTMClassifier(input_dim=input_dim, num_classes=num_classes).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0
    os.makedirs(args.ckpt_dir, exist_ok=True)
    for epoch in range(1, args.epochs+1):
        tr_loss, tr_acc = train_epoch(model, opt, criterion, train_loader, device)
        print(f"Epoch {epoch} Train loss:{tr_loss:.4f} acc:{tr_acc:.4f}")
        if val_loader:
            va_loss, va_acc = val_epoch(model, criterion, val_loader, device)
            print(f"Epoch {epoch} Val loss:{va_loss:.4f} acc:{va_acc:.4f}")
            if va_acc > best_acc:
                best_acc = va_acc
                torch.save({'model':model.state_dict(),
                            'label_map':train_ds.label_map}, os.path.join(args.ckpt_dir, 'best.pth'))
    # final save
    torch.save({'model':model.state_dict(),
                'label_map':train_ds.label_map}, os.path.join(args.ckpt_dir, 'last.pth'))

if __name__ == "__main__":
    import numpy as np
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", default="data/processed")
    p.add_argument("--val_dir", default="")
    p.add_argument("--ckpt_dir", default="models/checkpoints")
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--max_len", type=int, default=80)
    p.add_argument("--lr", type=float, default=1e-3)
    args = p.parse_args()
    main(args)
