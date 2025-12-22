"""
摄像头数据库模型
存储摄像头信息：
    -id
    -名称
    -ip地址
    -端口
    -URL
    -分辨率
    -帧率
    -编码格式
    -模型路径
    -跟踪算法配置路径
    -是否启用
    -状态
    -关联的检测记录反向引用
    -禁停区域

"""

from app import db
from typing import Optional, Any

class Camera(db.Model):
    __tablename__ = 'cameras'

    # 摄像头信息
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # 摄像头连接信息
    ip_address = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)

    # 视频流信息
    resolution = db.Column(db.String(50)) #分辨率
    frame_rate = db.Column(db.Integer) #帧率
    encoding_format = db.Column(db.String(50)) #编码格式
    
    # 模型和跟踪配置信息
    model = db.Column(db.String(255))  # 模型路径
    tracking_config = db.Column(db.String(255))  # 跟踪算法配置路径

    # 摄像头状态信息
    is_active = db.Column(db.Boolean, default=True)  # 摄像头是否启用
    status = db.Column(db.String(20), default='offline')  # 摄像头状态: online/offline/error
    
    # 禁停区域 - 存储格式：JSON字符串 
    # 示例: [{"id": 1, "points": [[x1,y1], [x2,y2], ...]}, {"id": 2, "points": [...]}]
    restricted_areas = db.Column(db.JSON)
    
    # 关联的检测记录反向引用
    detections = db.relationship('Detection', backref='camera', lazy=True)

    def __init__(self, name: str, ip_address: str, port: int, url: str,
                 resolution: Optional[str] = None, frame_rate: Optional[int] = None,
                 encoding_format: Optional[str] = None, model: Optional[str] = None,
                 tracking_config: Optional[str] = None, is_active: bool = True,
                 status: str = 'offline', restricted_areas: Optional[Any] = None):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.url = url
        self.resolution = resolution
        self.frame_rate = frame_rate
        self.encoding_format = encoding_format
        self.model = model
        self.tracking_config = tracking_config
        self.is_active = is_active
        self.status = status
        self.restricted_areas = restricted_areas

    def __repr__(self):
        return f"<Camera {self.name} ({self.ip_address}:{self.port})>"
