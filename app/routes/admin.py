"""
管理员接口
"""

from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    user_id = request.json['user_id']
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@bp.route('/update_user', methods=['PUT'])
def update_user():
    data = request.json
    user = User.query.get(data['user_id'])
    if user:
        user.username = data.get('username', user.username)
        user.password = data.get('password', user.password)
        user.phone = data.get('phone', user.phone)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404
