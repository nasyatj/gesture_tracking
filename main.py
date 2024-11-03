import cv2
import mediapipe as mp
from numpy.lib.twodim_base import fliplr

#video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_drawing = mp.solutions.drawing_utils #module containing functionalities
mp_hands = mp.solutions.hands #module containing functionalities
hand = mp_hands.Hands() #object of the class Hands

#reading video frame by frame
while True:
    success, image = cap.read()
    if success:
        image = cv2.flip(image, 1)
        RGB_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hand.process(RGB_image)


        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                print("hand!")
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("My Image", image)
        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()