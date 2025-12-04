import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera cannot be opened!")
    exit()

while True:
    ret, frame = cap.read()
    print("ret =", ret)
    if not ret:
        break

    cv2.imshow("Test Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
