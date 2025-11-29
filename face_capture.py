import cv2
import os

# Create directory for stored faces at the specified path
faces_dir = r'C:\Users\highe\Downloads\NewMove\faces'
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)
    print(f"Created directory: {faces_dir}")

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    print("Error: Could not load face detector")
    exit()

face_count = 0
print("Press 'c' to capture face, 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    # Display the directory path on the screen
    cv2.putText(frame, f"Saving to: {faces_dir}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, f"Faces captured: {face_count}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imshow('Face Capture', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        # Save the face when 'c' is pressed
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_img = frame[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            
            # Save image to the specified directory
            filename = os.path.join(faces_dir, f'face_{face_count}.jpg')
            cv2.imwrite(filename, face_img)
            print(f"Face {face_count} saved to: {filename}")
            face_count += 1
        else:
            print("No face detected to capture!")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Face capture completed. Total faces saved: {face_count}")