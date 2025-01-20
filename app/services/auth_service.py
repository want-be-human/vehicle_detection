"""
用户认证服务
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
import jwt
import datetime

SECRET_KEY = 'your_secret_key'

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = create_jwt_token(user)
        return True, token
    return False, None

def create_jwt_token(user):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    token = jwt.encode({'user_id': user.id, 'role': user.role, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

def register_user(username, password, role):
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user

