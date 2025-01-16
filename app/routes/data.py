from flask import Blueprint, request, jsonify
from app.models.detection import DetectionRecord

bp = Blueprint('data', __name__)

@bp.route('/records', methods=['GET'])
def get_records():
    records = DetectionRecord.query.all()
    return jsonify([record.to_dict() for record in records])