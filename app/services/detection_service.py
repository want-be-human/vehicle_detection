import cv2
from datetime import datetime, timedelta
import threading
from app.utils.yolo_integration import detect_vehicles
import os

class VideoProcessor:
    def __init__(self, camera_urls, save_dir='processed_videos'):
        self.camera_urls = camera_urls
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def process_stream(self, camera_url, camera_id):
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            print(f"Failed to open camera {camera_id}")
            return

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        save_path = os.path.join(self.save_dir, f"{camera_id}_{datetime.now().strftime('%Y%m%d%H')}.avi")
        out = cv2.VideoWriter(save_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

        next_save_time = datetime.now() + timedelta(hours=1)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Run YOLO detection
            detections = detect_vehicles(frame)
            for vehicle in detections:
                cv2.rectangle(frame, (vehicle['x1'], vehicle['y1']), (vehicle['x2'], vehicle['y2']), (0, 255, 0), 2)
                cv2.putText(frame, vehicle['type'], (vehicle['x1'], vehicle['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            out.write(frame)

            # Check if it's time to save the file and start a new one
            if datetime.now() >= next_save_time:
                out.release()
                save_path = os.path.join(self.save_dir, f"{camera_id}_{datetime.now().strftime('%Y%m%d%H')}.avi")
                out = cv2.VideoWriter(save_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))
                next_save_time += timedelta(hours=1)

        cap.release()
        out.release()

    def start(self):
        threads = []
        for idx, camera_url in enumerate(self.camera_urls):
            t = threading.Thread(target=self.process_stream, args=(camera_url, idx))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
