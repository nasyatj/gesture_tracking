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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

pinch_threshold = 0.05  # For pinch gesture sensitivity
pinch_start_time = None
pinch_duration = 3

# Function to calculate Euclidean distance
def calculate_distance(point1, point2):
    return math.sqrt((point1["x"] - point2.x) ** 2 + (point1["y"] - point2.y) ** 2)

# Function to send coordinates of index tip to the server
def send_coordinates(x, y):
    try:
        # Send coordinates
        message = f"{x},{y}"
        client.send(message.encode('utf-8'))  # Send the coordinates
        print(f"Sent coordinates: {x}, {y}")
    except (socket.error, socket.timeout) as e:
        print(f"Socket error: {e}")

# Function to send the "Select" command and coordinates to the server
def send_select_command(x, y):
    try:
        # Send the "Select" command along with the coordinates
        message = f"Select,{x},{y}"
        client.send(message.encode('utf-8'))
        print(f"Sent select command: Select,{x},{y}")
    except (socket.error, socket.timeout) as e:
        print(f"Socket error: {e}")

# Connect to the server once
try:
    client.connect(server_address)
    print(f"Connected to server at {server_address}")
except (socket.error, socket.timeout) as e:
    print(f"Error connecting to server: {e}")
    exit(1)

# Loop to simulate continuous sending of commands
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
            # Draw landmarks on the hand (optional)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Pinch/Select Gesture
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            distance = calculate_distance({"x": thumb_tip.x, "y": thumb_tip.y}, index_tip)

            # Check that middle, ring, and pinky fingers are closed (tips below the knuckles)
            middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
            pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

            # Ensure middle, ring, and pinky fingers are in a fist position
            if (middle_tip.y > middle_mcp.y and
                    ring_tip.y > ring_mcp.y and
                    pinky_tip.y > pinky_mcp.y):

                # If pinch gesture detected
                if distance < pinch_threshold:
                    #Start pinch timer if not already started
                    if pinch_start_time is None:
                        pinch_start_time = time.time()
                    else:
                        # Check if the pinch lasted for 3 seconds
                        if time.time() - pinch_start_time >= pinch_duration:
                            # Pinch lasted for 3 seconds, send select command
                            send_select_command(index_tip.x, index_tip.y)
                            pinch_start_time = None  # Reset the timer after selection

                else:
                    pinch_start_time = None

            # # Get the coordinates of the index finger tip
            # index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            # index_x, index_y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])
            #
            # # Check if the index finger is on the screen (within the frame)
            # if 0 <= index_x < frame.shape[1] and 0 <= index_y < frame.shape[0]:
            #     send_coordinates(index_x, index_y)

    # Display the frame
    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
client.close()
cv2.destroyAllWindows()