import os
import threading
import cv2
from ultralytics import YOLO

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

    def __init__(self, model_path, tracker_type='bytetrack', tracking_config=None):
        """
        初始化YOLO模型和跟踪配置
        Args:
            model_path: 模型文件名称
            tracker_type: 跟踪器类型 (botsort/bytetrack/custom)
            tracking_config: 自定义跟踪配置文件路径
        """
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

    def run_tracker_in_thread(self, camera_id, stream_url):
        """
        在独立线程中运行YOLO跟踪器
        Args:
            camera_id: 摄像头ID
            stream_url: 视频流URL
        Returns:
            generator: 生成检测结果的生成器
        """
        try:
            # 初始化模型
            model = YOLO(self.model_path)
            model.to('cuda')  # 使用GPU
            
            # 启动跟踪
            return model.track(
                source=stream_url,
                stream=True,
                tracker=self.tracking_config
            )
                    
        except Exception as e:
            print(f"Error processing camera {camera_id}: {str(e)}")
            raise

    def start_stream_processing(self, camera_id, stream_url, output_path):
        """
        启动视频流处理
        Args:
            camera_id: 摄像头ID
            stream_url: 视频流URL
            output_path: 输出视频路径
        """
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

    def process_file(self, file_path):
        """分析外部文件"""
        try:
            model = YOLO(self.model_path)
            model.to('cuda')
            
            results = model.track(
                source=file_path,
                tracker=self.tracking_config
            )
            
            return results
            
        except Exception as e:
            raise Exception(f"File analysis failed: {str(e)}")
    
    def _format_results(self, results):
        """格式化分析结果"""
        formatted_results = {
            "detections": [],
            "summary": {
                "total_frames": len(results),
                "total_detections": 0
            }
        }
        
        # TODO: 实现结果格式化逻辑
        
        return formatted_results

    def process_source(self, source, save_dir='outputs'):
        """
        处理输入源(图片/视频/目录)
        Args:
            source: 输入源路径
            save_dir: 结果保存目录
        Returns:
            dict: 处理结果
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            # 初始化模型
            model = YOLO(self.model_path)
            model.to('cuda')
            
            # 运行推理
            results = model(
                source=source,
                save=True,  # 保存带标注的图片/视频
                project=save_dir,
                stream=True  # 使用生成器模式节省内存
            )
            
            # 处理结果
            processed_results = []
            for r in results:
                if r is not None:
                    # 获取检测结果
                    boxes = r.boxes.numpy()
                    if len(boxes):
                        result_info = {
                            "frame_id": len(processed_results),
                            "detections": [{
                                "class": int(box.cls),
                                "confidence": float(box.conf),
                                "bbox": box.xyxy.tolist()[0]
                            } for box in boxes]
                        }
                        processed_results.append(result_info)
            
            return {
                "total_frames": len(processed_results),
                "results": processed_results,
                "output_path": save_dir
            }
            
        except Exception as e:
            raise Exception(f"Source processing failed: {str(e)}")

