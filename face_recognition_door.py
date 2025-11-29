import cv2
import numpy as np
import os
import serial
import time
from datetime import datetime

# Initialize serial connection to Arduino
try:
    arduino = serial.Serial('COM5', 9600, timeout=1)  # Change COM port as needed
    time.sleep(2)  # Wait for connection to establish
    print("Arduino connected successfully")
except serial.SerialException as e:
    print(f"Arduino connection failed: {e}")
    arduino = None

# Load known faces
known_faces = []
known_names = []

def load_known_faces():
    # Use the specific directory path
    faces_dir = r'C:\Users\highe\Downloads\NewMove\faces'
    if not os.path.exists(faces_dir):
        print(f"No known faces directory found at: {faces_dir}!")
        return
        
    for file in os.listdir(faces_dir):
        if file.endswith('.jpg') or file.endswith('.png'):
            img_path = os.path.join(faces_dir, file)
            img = cv2.imread(img_path)
            if img is not None:
                known_faces.append(img)
                # Extract name from filename (remove extension)
                name = os.path.splitext(file)[0]
                known_names.append(name)
                print(f"Loaded face: {name}")
            else:
                print(f"Failed to load image: {img_path}")
                
    print(f"Loaded {len(known_faces)} known faces")

def recognize_face(face_roi):
    if len(known_faces) == 0:
        return "Unknown", 0
    
    # Simple recognition using histogram comparison
    best_match = None
    best_score = 0
    
    for i, known_face in enumerate(known_faces):
        # Resize to same dimensions
        known_resized = cv2.resize(known_face, (face_roi.shape[1], face_roi.shape[0]))
        
        # Calculate similarity (using histogram comparison)
        hist1 = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([known_resized], [0], None, [256], [0, 256])
        
        # Normalize histograms for better comparison
        cv2.normalize(hist1, hist1, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 255, cv2.NORM_MINMAX)
        
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        if score > best_score:
            best_score = score
            best_match = known_names[i]
    
    # Threshold for recognition (adjust as needed)
    if best_score > 0.4:
        return best_match, best_score
    else:
        return "Unknown", best_score

# Load known faces
load_known_faces()

# Initialize camera and face detector
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    print("Error: Could not load face detector")
    exit()

# Variables for controlling recognition rate
last_recognition_time = 0
recognition_interval = 2  # seconds
last_detection_time = 0
cooldown_period = 10  # seconds after detection before next detection

# Status variables
door_unlocked = False
unlock_time = 0
unlock_duration = 10  # seconds to keep door unlocked

print("Starting face recognition. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image")
        break
        
    current_time = time.time()
    
    # Display status message
    status_text = "Door Locked"
    status_color = (0, 0, 255)  # Red
    
    if door_unlocked:
        if current_time - unlock_time < unlock_duration:
            status_text = "Door Unlocked"
            status_color = (0, 255, 0)  # Green
        else:
            door_unlocked = False
    
    # Add status text to frame
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # Check if we're in cooldown period after a detection
    in_cooldown = current_time - last_detection_time < cooldown_period
    
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        color = (0, 255, 0) if not in_cooldown else (0, 0, 255)  # Green if not in cooldown, red if in cooldown
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Perform recognition at controlled intervals and if not in cooldown
        if not in_cooldown and current_time - last_recognition_time > recognition_interval:
            face_roi = frame[y:y+h, x:x+w]
            name, confidence = recognize_face(face_roi)
            
            # Display name and confidence
            label = f"{name} ({confidence:.2f})"
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36, 255, 12), 2)
            
            # If recognized and Arduino is connected, send 'D' command
            if name != "Unknown" and arduino is not None:
                arduino.write(b'D')
                door_unlocked = True
                unlock_time = current_time
                last_detection_time = current_time
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Access granted for {name} (confidence: {confidence:.2f})")
            elif name == "Unknown":
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Unknown person detected (confidence: {confidence:.2f})")
            
            last_recognition_time = current_time
    
    # Display cooldown timer if in cooldown
    if in_cooldown:
        remaining = cooldown_period - (current_time - last_detection_time)
        cv2.putText(frame, f"Cooldown: {remaining:.1f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    cv2.imshow('Face Recognition Door System', frame)
    
    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
if arduino is not None:
    arduino.close()
cap.release()
cv2.destroyAllWindows()
print("System shut down")