"""
This script demonstrates how to use the GestureRecognizer task to recognize hand gestures.
"""
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.gesture_recognizer import GestureRecognizerResult

#gesture recognizer
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

#create gesture recognizer instance with live stream mode
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))

model_path = 'gesture_recognizer.task'

options = GestureRecognizerOptions(
    base_options = BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

#video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

with GestureRecognizer.create_from_options(options) as recognizer:
    # frame counter for recognizer timestamp
    frame_counter = 0;
    while True:
        success, image = cap.read()
        if not success:
            break

        # Flip the image horizontally for a mirror effect
        image = cv2.flip(image, 1)

        # Convert the image to RGB format for MediaPipe processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Process the frame with the gesture recognizer
        recognizer.recognize_async(mp_image, frame_counter)
        frame_counter += 1

        # Display the resulting frame
        cv2.imshow("Gesture Recognition", image)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the resources
cap.release()
cv2.destroyAllWindows()