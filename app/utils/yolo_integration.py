import os
import threading
import cv2
from ultralytics import YOLO
from app.services.violation_service import ViolationService

"""
YOLO 和跟踪算法集成工具

1. 实现YOLO和跟踪算法集成工具
2. 实现实时视频流处理逻辑
3. 实现外部文件分析逻辑

"""

# YOLO 和跟踪算法集成工具
class YOLOIntegration:
    TRACKER_OPTIONS = {
        'botsort': 'botsort.yaml',
        'bytetrack': 'bytetrack.yaml',
        'custom': None  # 用于自定义配置
    }
    
    # 需要检测的类别
    TARGET_CLASSES = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck'
    }




    """
        初始化YOLO模型和跟踪配置
        Args:
            model_path: 模型文件名称
            tracker_type: 跟踪器类型 (botsort/bytetrack/custom)
            tracking_config: 自定义跟踪配置文件路径
    """
    def __init__(self, model_path, tracker_type='botsort', tracking_config=None):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))
        self.model_dir = os.path.join(self.base_path, 'models')
        
        # 加载模型
        self.model_path = os.path.join(self.model_dir, model_path)
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
            
        # 设置跟踪器
        self.tracker_type = tracker_type
        if tracker_type == 'custom':
            if not tracking_config or not os.path.exists(tracking_config):
                raise ValueError("Custom tracker requires valid config path")
            self.tracking_config = tracking_config
        else:
            if tracker_type not in self.TRACKER_OPTIONS:
                raise ValueError(f"Invalid tracker type: {tracker_type}")
            self.tracking_config = self.TRACKER_OPTIONS[tracker_type]




    """
        在独立线程中运行YOLO跟踪器
        Args:
            camera_id: 摄像头ID
            stream_url: 视频流URL
        Returns:
            generator: 生成检测结果的生成器
    """
    def run_tracker_in_thread(self, camera_id, stream_url):
        try:
            # 初始化模型
            model = YOLO(self.model_path)
            model.to('cuda')  # 使用GPU
            
            # 初始化违规检测服务
            violation_service = ViolationService()
            
            # 启动跟踪，只处理目标类别
            results_gen = model.track(
                source=stream_url,
                stream=True,
                tracker=self.tracking_config,
                classes=list(self.TARGET_CLASSES.keys())  # 只检测指定类别
            )
            
            for results in results_gen:
                if results and len(results):
                    result = results[0]  # 获取当前帧的结果
                    
                    # 检查违规情况
                    violations = violation_service.check_violations(camera_id, result)
                    
                    yield result, violations
                    
        except Exception as e:
            print(f"Error processing camera {camera_id}: {str(e)}")
            raise




    """
        启动视频流处理
        Args:
            camera_id: 摄像头ID
            stream_url: 视频流URL
            output_path: 输出视频路径
    """
    def start_stream_processing(self, camera_id, stream_url, output_path):
        try:
            # 创建并启动处理线程
            thread = threading.Thread(
                target=self.run_tracker_in_thread,
                args=(camera_id, stream_url, output_path),
                daemon=True
            )
            thread.start()
            
            return {
                "thread_id": thread.ident,
                "status": "running",
                "camera_id": camera_id,
                "output_path": output_path
            }
            
        except Exception as e:
            raise Exception(f"Failed to start stream processing: {str(e)}")





    """处理输入源(图片/视频)并保存结果"""
    def process_source(self, source, save_dir='outputs'):
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            # 初始化模型
            model = YOLO(self.model_path)
            model.to('cuda')
            
            # 添加文件名处理
            filename = os.path.basename(source)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(save_dir, f"{name}_analyzed{ext}")
            
            # 运行推理
            results = model.track(
                source=source,
                save=True,  # 保存带标注的结果
                project=save_dir,
                name=os.path.basename(output_path),
                tracker=self.tracking_config,
                classes=list(self.TARGET_CLASSES.keys())  # 只检测指定类别
            )
            
            # 汇总检测结果
            summary = {
                "source": source,
                "output_path": output_path,
                "detections": [],
                "total_frames": 0,
                "total_objects": 0
            }
            
            # 处理每一帧的结果
            for r in results:
                if r.boxes is not None:
                    frame_detections = []
                    for box, track_id, cls_id in zip(
                            r.boxes.xywh.cpu(), 
                            r.boxes.id.int().cpu(), 
                            r.boxes.cls.cpu()):
                        if int(cls_id) in self.TARGET_CLASSES:
                            detection = {
                                "track_id": int(track_id),
                                "class": self.TARGET_CLASSES[int(cls_id)],
                                "position": box.tolist()
                            }
                            frame_detections.append(detection)
                    
                    summary["detections"].append(frame_detections)
                    summary["total_objects"] += len(frame_detections)
                summary["total_frames"] += 1
            
            return summary
            
        except Exception as e:
            raise Exception(f"Source processing failed: {str(e)}")




    """可视化检测结果"""    
    def visualize_results(self, frame, results):
        if results.boxes is None or len(results.boxes) == 0:
            return frame
            
        boxes = results.boxes.xywh.cpu()
        track_ids = results.boxes.id.int().cpu().tolist()
        cls_ids = results.boxes.cls.cpu().tolist()
        
        # 绘制检测框和标签
        for box, track_id, cls_id in zip(boxes, track_ids, cls_ids):
            if int(cls_id) in self.TARGET_CLASSES:
                x, y, w, h = map(int, box)
                cls_name = self.TARGET_CLASSES[int(cls_id)]
                
                # 绘制边界框
                cv2.rectangle(frame, (x-w//2, y-h//2), (x+w//2, y+h//2), (0, 255, 0), 2)
                
                # 添加标签
                label = f'{cls_name} #{track_id} ({x},{y})'
                cv2.putText(frame, label, (x-w//2, y-h//2-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        return frame

