import jwt
from flask import current_app
from werkzeug.security import check_password_hash
from app.models.user import User

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        token = jwt.encode({'id': user.id, 'role': user.role}, current_app.config['SECRET_KEY'], algorithm='HS256')
        return True, token
    return False, None

def decode_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
