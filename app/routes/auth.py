"""
用户认证相关接口
"""

from flask import Blueprint, request, jsonify
from app.services.auth_service import authenticate_user, register_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user = register_user(data['username'], data['password'], data['role'])
    return jsonify({'message': 'User registered successfully'}), 200

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    success, token = authenticate_user(data['username'], data['password'])
    if success:
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

