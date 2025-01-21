from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO(r"D:\PycharmProjects\vehicle_detection\app\assets\models\yolo11m.pt")
model=model.to("cuda")

# Open the video file
video_path = r"D:\26075922957-1-192.mp4"
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Loop through the video frames
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    
    if success:
        # Run YOLOv8 tracking on the frame
        results = model.track(frame, persist=True)
        
        # Get the boxes, track IDs and class names
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        cls = results[0].boxes.cls.cpu().tolist()
        names = results[0].names
        
        # Plot the tracks
        for box, track_id, cls_id in zip(boxes, track_ids, cls):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))
            if len(track) > 30:
                track.pop(0)
            
            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, 
                         color=(0, 255, 0), thickness=1)
            
            # Add text label
            label = f'{names[int(cls_id)]} #{track_id} ({int(x)},{int(y)})'
            t_size = cv2.getTextSize(label, 0, fontScale=0.6, thickness=1)[0]
            cv2.putText(frame, label, 
                       (int(x - t_size[0]/2), int(y - 10)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (0,255,0), 1)
        
        # Show the results
        cv2.imshow("Tracking", frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()