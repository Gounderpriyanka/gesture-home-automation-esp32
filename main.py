import cv2
import mediapipe as mp
import serial
import time

# 🔌 CHANGE COM PORT
ser = serial.Serial('COM3', 9600)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

prev_command = ""

# 👉 Finger counting function
def count_fingers(hand_landmarks):
    fingers = []

    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    tips = [8, 12, 16, 20]
    dips = [6, 10, 14, 18]

    for tip, dip in zip(tips, dips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[dip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    command = ""
    text = "No Gesture"

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            total = count_fingers(handLms)
            print("Fingers:", total)  # Debug

            # 🔥 FINAL GESTURE CONTROL
            if total == 1:
                command = '1'
                text = "LED ON"

            elif total == 0:
                command = '0'
                text = "LED OFF"

            elif total == 2:
                command = '2'
                text = "FAN ON"

            elif total == 3:
                command = '3'
                text = "FAN OFF"

    # 👉 Send only new command
    if command != "" and command != prev_command:
        ser.write(command.encode())
        print("Sent:", text)
        prev_command = command
        time.sleep(0.5)

    cv2.putText(img, text, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Gesture Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
