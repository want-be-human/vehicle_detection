"""
多摄像头实时车辆检测

1. 启动检测逻辑
2. 获取所有检测记录
3. 分析外部文件逻辑

"""

# 车辆检测服务
import os
import cv2
import threading
import glob
import time
from datetime import datetime, timedelta
from app.models.detection import Detection
from app.utils.yolo_integration import YOLOIntegration
from app.utils.logging_utils import log_detection
from app import db
from queue import Queue
from app.utils.websocket_utils import emit_violation_alert

class DetectionService:
    # 存储活跃的处理线程
    active_threads = {}
    
    @staticmethod
    def start_detection(data):
        """
        启动检测逻辑并处理视频存储
        Args:
            data: dict containing:
                - camera_id: 摄像头ID
                - stream_url: 视频流URL
                - model_path: YOLO模型路径
                - tracker_type: 跟踪器类型
                - tracking_config: 自定义跟踪配置路径(可选)
                - save_dir: 视频保存目录
                - retention_days: 视频保存天数(可选)
        """
        try:
            camera_id = data['camera_id']
            
            # 检查是否已有处理线程
            if camera_id in DetectionService.active_threads:
                return {
                    "success": False,
                    "message": f"Camera {camera_id} is already being processed"
                }
            
            # 初始化YOLO和跟踪器
            yolo = YOLOIntegration(
                model_path=data['model_path'],
                tracker_type=data.get('tracker_type', 'bytetrack'),
                tracking_config=data.get('tracking_config')
            )
            
            # 创建存储目录
            save_dir = data['save_dir']
            os.makedirs(save_dir, exist_ok=True)
            
            # 添加存储时间限制
            retention_days = data.get('retention_days', 30)  # 默认保存30天
            
            # 启动视频处理和清理线程
            process_thread = threading.Thread(
                target=DetectionService._process_and_save_stream,
                args=(yolo, data),
                daemon=True
            )
            cleanup_thread = threading.Thread(
                target=DetectionService._cleanup_old_videos,
                args=(data['save_dir'], data['camera_id'], retention_days),
                daemon=True
            )
            
            # 存储线程信息
            DetectionService.active_threads[camera_id] = {
                'thread': process_thread,
                'status': 'starting'
            }
            
            process_thread.start()
            cleanup_thread.start()
            
            return {
                "success": True,
                "status": "started",
                "camera_id": data['camera_id'],
                "retention_days": retention_days
            }
            
        except Exception as e:
            if camera_id in DetectionService.active_threads:
                del DetectionService.active_threads[camera_id]
            raise Exception(f"Detection start failed: {str(e)}")

    @staticmethod
    def _process_and_save_stream(yolo, data):
        """处理视频流并按小时存储"""
        camera_id = data['camera_id']
        stream_url = data['stream_url']
        save_dir = data['save_dir']
        
        try:
            DetectionService.active_threads[camera_id]['status'] = 'running'
            results_generator = yolo.run_tracker_in_thread(camera_id, stream_url)
            
            # 初始化视频写入器
            current_hour = datetime.now().hour
            output_path = DetectionService._get_video_path(save_dir, camera_id, current_hour)
            out = None
            
            for results, violations in results_generator:
                if results:
                    # 发送违规提醒
                    if violations:
                        for violation in violations:
                            emit_violation_alert(violation)
                    
                    # 检查是否需要创建新的视频文件
                    now = datetime.now()
                    if now.hour != current_hour:
                        if out:
                            out.release()
                        current_hour = now.hour
                        output_path = DetectionService._get_video_path(save_dir, camera_id, current_hour)
                        
                        # 更新数据库
                        DetectionService._update_detection_record(camera_id, output_path)
                    
                    # 确保视频写入器已初始化
                    if out is None:
                        frame = results.plot()  # 获取带有检测框的帧
                        height, width = frame.shape[:2]
                        out = cv2.VideoWriter(
                            output_path, 
                            cv2.VideoWriter_fourcc(*'mp4v'), 
                            30, 
                            (width, height)
                        )
                        
                        # 创建初始数据库记录
                        DetectionService._update_detection_record(camera_id, output_path)
                    
                    # 写入帧
                    out.write(results.plot())
                    
        except Exception as e:
            print(f"Stream processing error: {str(e)}")
            DetectionService.active_threads[camera_id]['status'] = 'error'
        finally:
            if out:
                out.release()
            if camera_id in DetectionService.active_threads:
                del DetectionService.active_threads[camera_id]

    @staticmethod
    def _cleanup_old_videos(save_dir, camera_id, retention_days):
        """定期清理过期视频文件"""
        while True:
            try:
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # 查找需要清理的视频文件
                pattern = os.path.join(save_dir, f"camera_{camera_id}_*.mp4")
                video_files = glob.glob(pattern)
                
                for video_path in video_files:
                    # 从文件名获取日期
                    filename = os.path.basename(video_path)
                    try:
                        date_str = filename.split('_')[2]  # 获取YYYYMMDD部分
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        
                        if file_date < cutoff_date:
                            # 删除视频文件
                            os.remove(video_path)
                            
                            # 删除相关的数据库记录
                            DetectionService._delete_detection_record(camera_id, video_path)
                            
                    except (ValueError, IndexError):
                        continue
                        
                # 每天检查一次
                time.sleep(86400)  # 24小时
                
            except Exception as e:
                print(f"Cleanup error: {str(e)}")
                time.sleep(3600)  # 发生错误时1小时后重试

    @staticmethod
    def _delete_detection_record(camera_id, video_path):
        """删除检测记录"""
        try:
            Detection.query.filter_by(
                camera_id=camera_id,
                video_path=video_path
            ).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to delete detection record: {str(e)}")

    @staticmethod
    def _get_video_path(save_dir, camera_id, hour):
        """生成视频文件路径"""
        now = datetime.now()
        filename = f"camera_{camera_id}_{now.strftime('%Y%m%d')}_{hour:02d}.mp4"
        return os.path.join(save_dir, filename)

    @staticmethod
    def _update_detection_record(camera_id, video_path):
        """更新检测记录"""
        try:
            detection = Detection(
                camera_id=camera_id,
                timestamp=datetime.now(),
                video_path=video_path
            )
            db.session.add(detection)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update detection record: {str(e)}")

    @staticmethod
    def get_all_detections():
        """
        获取所有检测记录
        """
        detections = Detection.query.all()
        return [detection.to_dict() for detection in detections]

    @staticmethod
    def analyze_file(data):
        """
        分析外部视频/图片文件
        Args:
            data (dict): {
                'source': 文件路径,
                'model': 模型路径,
                'tracker_type': 跟踪器类型,
                'tracking_config': 跟踪配置(可选),
                'save_dir': 保存目录(可选)
            }
        Returns:
            dict: 分析结果
        """
        try:
            source = data['source']
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source file not found: {source}")
            
            # 验证文件类型
            valid_extensions = ('.mp4', '.avi', '.jpg', '.jpeg', '.png')
            if not source.lower().endswith(valid_extensions):
                raise ValueError(f"Unsupported file type. Supported: {valid_extensions}")
            
            # 创建保存目录
            save_dir = data.get('save_dir', 'outputs')
            os.makedirs(save_dir, exist_ok=True)
            
            # 初始化YOLO
            yolo = YOLOIntegration(
                model_path=data['model'],
                tracker_type=data.get('tracker_type', 'bytetrack'),
                tracking_config=data.get('tracking_config')
            )
            
            # 处理文件
            results = yolo.process_source(source, save_dir)
            
            return {
                "success": True,
                "message": "Analysis completed successfully",
                "results": results
            }
            
        except Exception as e:
            raise Exception(f"File analysis failed: {str(e)}")

    @staticmethod
    def get_processing_status():
        """获取所有处理线程的状态"""
        return {
            camera_id: info['status']
            for camera_id, info in DetectionService.active_threads.items()
        }



