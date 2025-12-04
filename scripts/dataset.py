# scripts/dataset.py
import os
import numpy as np
from torch.utils.data import Dataset
import torch

class KeypointSequenceDataset(Dataset):
    def __init__(self, npz_dir, label_map=None, max_len=100, mode='train'):
        """
        npz_dir: directory of .npz files
        label_map: dict label->int, if None build from data
        max_len: pad/truncate length in frames
        """
        files = [os.path.join(npz_dir,f) for f in os.listdir(npz_dir) if f.endswith('.npz')]
        self.files = files
        self.max_len = max_len
        self.mode = mode
        self.label_map = label_map or self._build_label_map()
        self.inv_map = {v:k for k,v in self.label_map.items()}

    def _build_label_map(self):
        labels = set()
        for f in self.files:
            data = np.load(f, allow_pickle=True)
            labels.add(str(data['label']))
        labels = sorted(list(labels))
        return {lab:i for i,lab in enumerate(labels)}

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        npz = np.load(self.files[idx], allow_pickle=True)
        kps = npz['keypoints']  # shape [T, feat]
        label = str(npz['label'])
        y = self.label_map[label]
        # pad/truncate
        if kps.shape[0] >= self.max_len:
            kps = kps[:self.max_len]
            mask = np.ones(self.max_len, dtype=np.float32)
        else:
            pad = np.zeros((self.max_len - kps.shape[0], kps.shape[1]), dtype=np.float32)
            kps = np.concatenate([kps, pad], axis=0)
            mask = np.concatenate([np.ones(kps.shape[0]-pad.shape[0], dtype=np.float32),
                                   np.zeros(pad.shape[0], dtype=np.float32)])
        return torch.from_numpy(kps).float(), torch.tensor(y).long(), torch.from_numpy(mask).float()
