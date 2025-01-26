from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.violation_service import ViolationService
from app.models.violation import Violation

violation_blueprint = Blueprint('violation', __name__)
violation_service = ViolationService()

@violation_blueprint.route('/records', methods=['GET'])
def get_violations():
    try:
        filters = {}
        
        if 'camera_id' in request.args:
            filters['camera_id'] = int(request.args.get('camera_id'))
            
        if 'start_time' in request.args:
            filters['start_time'] = datetime.strptime(
                request.args.get('start_time'), 
                '%Y-%m-%d %H:%M:%S'
            )
            
        if 'end_time' in request.args:
            filters['end_time'] = datetime.strptime(
                request.args.get('end_time'), 
                '%Y-%m-%d %H:%M:%S'
            )
            
        if 'vehicle_type' in request.args:
            filters['vehicle_type'] = request.args.get('vehicle_type')

        if 'violation_type' in request.args:
            filters['violation_type'] = request.args.get('violation_type')

        violations = violation_service.get_violations(filters)
        
        return jsonify({
            'success': True,
            'violations': violations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
