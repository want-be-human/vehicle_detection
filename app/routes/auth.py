from flask import Blueprint, request, jsonify
from app.services.auth_service import decode_token
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/users', methods=['POST'])
def create_user():
    token = request.headers.get('Authorization').split(" ")[1]
    decoded = decode_token(token)
    if decoded['role'] != 'admin':
        return {'message': 'Unauthorized'}, 403

    data = request.json
    new_user = User(username=data['username'], password=data['password'], role=data.get('role', 'user'))
    db.session.add(new_user)
    db.session.commit()
    return {'message': 'User created successfully'}, 201

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    token = request.headers.get('Authorization').split(" ")[1]
    decoded = decode_token(token)
    if decoded['role'] != 'admin':
        return {'message': 'Unauthorized'}, 403

    user = User.query.get(user_id)
    if not user:
        return {'message': 'User not found'}, 404

    db.session.delete(user)
    db.session.commit()
    return {'message': 'User deleted successfully'}, 200
