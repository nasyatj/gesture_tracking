import cv2
import mediapipe as mp
import math

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize thresholds and variables
zoom_threshold = 0.05  # For zoom gesture sensitivity
move_threshold = 0.02  # For move gesture sensitivity
pinch_threshold = 0.02  # For pinch gesture sensitivity
fist_threshold = 0.1  # Increased threshold for fist gesture
previous_angle = None
previous_wrist_x, previous_wrist_y = None, None

# Function to calculate Euclidean distance
def calculate_distance(point1, point2):
    return math.sqrt((point1["x"] - point2.x) ** 2 + (point1["y"] - point2.y) ** 2)

# Function to calculate angle between two points
def calculate_angle(wrist, index_tip):
    angle = math.atan2(index_tip.y - wrist.y, index_tip.x - wrist.x) * 180 / math.pi
    return angle

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

            # Zoom In/Out Gesture
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

                if distance < zoom_threshold:
                    cv2.putText(frame, "Zoom In", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                else:
                    cv2.putText(frame, "Zoom Out", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Rotate Gesture
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_angle = calculate_angle(wrist, index_tip)

            if previous_angle is not None:
                if current_angle > previous_angle + 5:
                    cv2.putText(frame, "Rotate Right", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif current_angle < previous_angle - 5:
                    cv2.putText(frame, "Rotate Left", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            previous_angle = current_angle

            # Move Gesture
            wrist_x, wrist_y = wrist.x, wrist.y

            if previous_wrist_x is not None and previous_wrist_y is not None:
                dx = wrist_x - previous_wrist_x
                dy = wrist_y - previous_wrist_y

                if abs(dx) > move_threshold:
                    if dx > 0:
                        cv2.putText(frame, "Move Right", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Move Left", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                if abs(dy) > move_threshold:
                    if dy > 0:
                        cv2.putText(frame, "Move Down", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Move Up", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            previous_wrist_x, previous_wrist_y = wrist_x, wrist_y

            # # Pinch Gesture Detection
            # if distance < pinch_threshold:
            #     cv2.putText(frame, "Pinch - Grab/Select", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

            # Victory Sign Detection (Index and Middle Fingers Extended, Other Fingers Down)
            index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

            # Check if only index and middle fingers are extended
            if (index_mcp.y < ring_tip.y and middle_mcp.y < ring_tip.y and
                thumb_tip.y > index_tip.y and ring_tip.y > index_mcp.y and pinky_tip.y > index_mcp.y):
                cv2.putText(frame, "Victory Sign", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 128), 2)
            else:
                # Thumbs Up/Down Detection (Only Thumb Raised)
                thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                if (thumb_tip.y < thumb_ip.y and
                    index_tip.y > thumb_ip.y and
                    middle_mcp.y > thumb_ip.y and
                    ring_tip.y > thumb_ip.y and pinky_tip.y > thumb_ip.y):
                    cv2.putText(frame, "Thumbs Up", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif thumb_tip.y > thumb_ip.y:
                    cv2.putText(frame, "Thumbs Down", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Fist Clench Detection (All fingertips close to palm center)
            palm_center_x = (wrist.x + middle_mcp.x) / 2
            palm_center_y = (wrist.y + middle_mcp.y) / 2
            palm_center = {"x": palm_center_x, "y": palm_center_y}

            # Check if all fingertips are close to the palm center
            is_fist = all(
                calculate_distance(palm_center, hand_landmarks.landmark[tip]) < fist_threshold
                for tip in [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                            mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
                            mp_hands.HandLandmark.PINKY_TIP]
            )
            if is_fist:
                cv2.putText(frame, "Fist - Close/Stop", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 0, 128), 2)

    # Display the frame
    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
