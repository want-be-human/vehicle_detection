from flask import Blueprint, jsonify

connect_blueprint = Blueprint('connect', __name__)

@connect_blueprint.route('/api/test')
def test():
    return jsonify({'message': 'Backend server is running'})