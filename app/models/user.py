"""
用户模型
"""
from app import db
from typing import Optional

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    phone = db.Column(db.String(20), nullable=True)

    def __init__(self, username: str, password: str, role: str = 'user', phone: Optional[str] = None):
        self.username = username
        self.password = password
        self.role = role
        self.phone = phone
