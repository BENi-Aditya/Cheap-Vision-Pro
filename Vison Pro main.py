import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Constants
DOUBLE_CLICK_TIME = 0.5  # Time threshold for double-click in seconds
COOLDOWN_TIME = 2.0  # Cooldown time in seconds

# Variables for debounce mechanism
last_switch_time = 0
last_click_time = 0
is_right_clicking = False
is_pinky_thumb_touching = False
is_index_thumb_touching = False
left_click_held = False

# Function to check if fingers are touching
def fingers_touching(hand_landmarks, finger1, finger2):
    finger1_landmark = hand_landmarks.landmark[finger1]
    finger2_landmark = hand_landmarks.landmark[finger2]

    # Calculate the Euclidean distance between the fingers
    distance = ((finger1_landmark.x - finger2_landmark.x) ** 2 + (finger1_landmark.y - finger2_landmark.y) ** 2) ** 0.5

    # If distance is below a threshold, fingers are touching
    return distance < 0.03  # Adjusted threshold for sensitivity

# Initialize webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Convert BGR frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe
    results = hands.process(rgb_frame)

    # Check if hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Check if index and thumb fingers are touching for left click
            if fingers_touching(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.THUMB_TIP):
                # Perform left mouse click and hold
                pyautogui.mouseDown()
                is_index_thumb_touching = True
                left_click_held = True
            else:
                # Release left mouse click hold if previously held
                if left_click_held:
                    pyautogui.mouseUp()
                    left_click_held = False
                is_index_thumb_touching = False

            # Check if middle finger and thumb are touching for right click
            if fingers_touching(hand_landmarks, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.THUMB_TIP):
                # Perform right mouse click
                if not is_right_clicking:
                    pyautogui.click(button='right')
                    is_right_clicking = True
            else:
                is_right_clicking = False

            # Check if pinky and thumb are touching for desktop switching
            if fingers_touching(hand_landmarks, mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.THUMB_TIP):
                is_pinky_thumb_touching = True
            else:
                is_pinky_thumb_touching = False

            # Check for hand gesture for Ctrl + Left Arrow (Switch to previous desktop)
            if is_pinky_thumb_touching and hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x:
                current_time = time.time()
                if current_time - last_switch_time > COOLDOWN_TIME:
                    pyautogui.hotkey('ctrl', 'left')
                    last_switch_time = current_time

            # Check for hand gesture for Ctrl + Right Arrow (Switch to next desktop)
            elif is_pinky_thumb_touching and hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x > hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x:
                current_time = time.time()
                if current_time - last_switch_time > COOLDOWN_TIME:
                    pyautogui.hotkey('ctrl', 'right')
                    last_switch_time = current_time

            # Check for double-click (left click)
            if fingers_touching(hand_landmarks, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.THUMB_TIP):
                current_time = time.time()
                if current_time - last_click_time < DOUBLE_CLICK_TIME:
                    pyautogui.doubleClick()
                last_click_time = current_time

    # Display frame
    cv2.imshow('Hand Tracking', frame)

    # Check for exit key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close all windows
cap.release()
cv2.destroyAllWindows()
