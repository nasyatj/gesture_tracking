import socket
import time
import cv2
import mediapipe as mp
import math

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Set up the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)

# Open webcam
cap = cv2.VideoCapture(0)

# Function to send coordinates to the server
def send_coordinates(x, y):
    try:
        # Send coordinates
        message = f"{x},{y}"
        client.send(message.encode('utf-8'))  # Send the coordinates
        print(f"Sent coordinates: {x}, {y}")
    except (socket.error, socket.timeout) as e:
        print(f"Socket error: {e}")

# Connect to the server once
try:
    client.connect(server_address)
    print(f"Connected to server at {server_address}")
except (socket.error, socket.timeout) as e:
    print(f"Error connecting to server: {e}")
    exit(1)

# Loop to simulate continuous sending of coordinates
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and convert frame to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the hand
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the coordinates of the index finger tip
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x, index_y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])

            # Check if the index finger is on the screen (within the frame)
            if 0 <= index_x < frame.shape[1] and 0 <= index_y < frame.shape[0]:
                send_coordinates(index_x, index_y)

    # Display the frame
    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
client.close()
cv2.destroyAllWindows()