"""
yolo算法集成
"""

import cv2
import numpy as np

# 假设我们已经训练了YOLO模型并将其加载
def detect_vehicles(image_path):
    net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

    image = cv2.imread(image_path)
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    vehicles = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # Confidence threshold
                vehicles.append({'type': class_id, 'confidence': confidence, 'time': 'current_timestamp'})
    return vehicles
