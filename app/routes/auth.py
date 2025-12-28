"""
用户认证相关接口
"""

from flask import Blueprint, request, jsonify
from app.services.auth_service import authenticate_user, register_user

# 将 bp 改为 auth_blueprint
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    register_user(data['username'], data['password'], data['role'])
    return jsonify({'message': 'User registered successfully'}), 200

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    success, token = authenticate_user(data['username'], data['password'])
    if success:
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

