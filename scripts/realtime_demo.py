# scripts/realtime_demo.py
# 需求: pip install mediapipe opencv-python torch numpy pymysql
import os
from pathlib import Path

# 获取当前文件（realtime_demo.py）所在目录
BASE_DIR = Path(__file__).resolve().parent.parent

model_path = BASE_DIR / "models" / "checkpoints" / "last.pth"
print("加载模型路径：", model_path)

import cv2
import mediapipe as mp
import numpy as np
import torch
from collections import deque

# 写日志用
from scripts.log_service import add_log

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


# ============================
#     模型实时识别类
# ============================
class RealtimeSign:
    def __init__(self, model_path, device='cuda', window_size=40, predict_every=5):
        # 加载模型 checkpoint
        ck = torch.load(model_path, map_location=device)

        # 加载标签映射
        label_map = ck.get("label_map", None)
        self.inv_map = {v: k for k, v in label_map.items()} if label_map else None

        # 导入训练阶段的模型结构
        from scripts.train import LSTMClassifier

        input_dim = 21 * 3 * 2  # 双手关键点
        num_classes = len(label_map) if label_map else 100

        # 构建模型
        self.model = LSTMClassifier(input_dim=input_dim, num_classes=num_classes)
        self.model.load_state_dict(ck["model"])
        self.model.eval().to(device)

        self.device = device
        self.window_size = window_size
        self.buf = deque(maxlen=window_size)
        self.predict_every = predict_every
        self.counter = 0
        self.votes = deque(maxlen=10)

    def push_frame_kps(self, kps):
        self.buf.append(kps)
        self.counter += 1

        if self.counter % self.predict_every == 0 and len(self.buf) == self.window_size:
            self.predict()
            self.counter = 0

    def predict(self):
        x = np.array(self.buf, dtype=np.float32)[None, ...]
        x = torch.from_numpy(x).float().to(self.device)

        with torch.no_grad():
            try:
                logits = self.model(x)
                pred = int(logits.argmax(dim=1).item())
            except Exception as e:
                print("Prediction ERROR:", e)
                return

        label = self.inv_map.get(pred, str(pred))
        self.votes.append(label)

    def get_smooth_label(self):
        if not self.votes:
            return ""
        from collections import Counter
        c = Counter(self.votes)
        return c.most_common(1)[0][0]


# ============================
#         主函数
# ============================
def main():
    model_path = "../models/checkpoints/last.pth"


    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Using device:", device)

    rt = RealtimeSign(model_path, device=device)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera!")
        return

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    CURRENT_USER_ID = 2  # 写入数据库的用户 ID，可改

    while True:
        ret, frame = cap.read()
        print("ret =", ret)

        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        kps = []

        if res.multi_hand_landmarks:
            hands_sorted = sorted(
                res.multi_hand_landmarks,
                key=lambda lm: min([p.x for p in lm.landmark])
            )

            for lm in hands_sorted[:2]:
                for p in lm.landmark:
                    kps.extend([p.x, p.y, p.z])

            if len(hands_sorted) == 1:
                kps.extend([0.0] * (21 * 3))

            # 画关键点
            for lm in res.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
        else:
            kps = [0.0] * (21 * 3 * 2)

        # 标准化
        arr = np.array(kps, dtype=np.float32)
        if arr.std() > 1e-6:
            arr = (arr - arr.mean()) / (arr.std() + 1e-6)

        rt.push_frame_kps(arr.tolist())
        label = rt.get_smooth_label()

        # ========================
        #      写入数据库日志
        from scripts.log_service import add_log
        CURRENT_USER_ID = 2

        if label != "":
            print(add_log(CURRENT_USER_ID, label, 1.0))
        # ========================
        if label != "":
            print("识别结果:", label)
            log_res = add_log(CURRENT_USER_ID, label, confidence=1.0)
            print("数据库写入：", log_res)

        # 显示识别结果
        cv2.putText(frame, f"Label: {label}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Realtime Sign", frame)

        # 按 q 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
