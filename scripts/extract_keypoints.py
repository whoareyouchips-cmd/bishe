# scripts/extract_keypoints.py
# 需求: pip install mediapipe opencv-python numpy tqdm

import os, sys, argparse
import cv2
import mediapipe as mp
import numpy as np
from tqdm import tqdm

mp_hands = mp.solutions.hands

def extract_from_video(video_path, max_frames=None):
    cap = cv2.VideoCapture(video_path)
    hands = mp_hands.Hands(static_image_mode=False,
                           max_num_hands=2,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5)
    frames_kps = []
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(img_rgb)
        # we capture up to two hands, flatten positions - if missing fill zeros
        if res.multi_hand_landmarks:
            # sort hands by x coordinate to keep order consistent (left/right)
            hands_sorted = sorted(res.multi_hand_landmarks, key=lambda lm: min([p.x for p in lm.landmark]))
            # keep first two
            kps = []
            for lm in hands_sorted[:2]:
                for p in lm.landmark:
                    kps.extend([p.x, p.y, p.z])  # normalized coords
            # pad if only one hand
            if len(hands_sorted) == 1:
                kps.extend([0.0]*21*3)
        else:
            kps = [0.0]*(21*3*2)  # two hands, each 21*(x,y,z)
        frames_kps.append(kps)
        if max_frames and len(frames_kps) >= max_frames:
            break
    cap.release()
    hands.close()
    return np.asarray(frames_kps, dtype=np.float32), fps

def main(args):
    os.makedirs(args.out_dir, exist_ok=True)
    # video_dir contains subfolders or files whose name encodes label
    # Expected convention: video files named <label>_<id>.mp4 OR organized in subfolders per label
    if os.path.isdir(args.input):
        # iterate files
        items = []
        for root, dirs, files in os.walk(args.input):
            for f in files:
                if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    label = os.path.basename(root) if root != args.input else os.path.splitext(f)[0].split('_')[0]
                    items.append((os.path.join(root,f), label))
    else:
        print("Input should be a directory containing videos.")
        return

    for vp, label in tqdm(items):
        try:
            kps, fps = extract_from_video(vp)
            if kps.shape[0] < 3:
                # too short ignore or pad; here we skip
                continue
            # normalize per-sample: subtract mean, divide std
            mean = kps.mean()
            std = kps.std() + 1e-6
            kps = (kps - mean) / std
            base = os.path.splitext(os.path.basename(vp))[0]
            outp = os.path.join(args.out_dir, f"{label}_{base}.npz")
            np.savez_compressed(outp, keypoints=kps, label=label, fps=fps)
        except Exception as e:
            print("Failed:", vp, e)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="input video dir")
    p.add_argument("--out_dir", default="data/processed", help="output dir for npz")
    args = p.parse_args()
    main(args)
