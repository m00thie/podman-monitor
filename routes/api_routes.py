from flask import Blueprint, jsonify, request
from services.podman_service import PodmanService
from services.logger_service import get_logger

# Create a logger
logger = get_logger('api-routes')

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create a PodmanService instance
podman_service = PodmanService()

@api_bp.route('/containers')
def containers():
    """API endpoint to get container information"""
    logger.info("API request for container information")
    container_info = podman_service.get_all_containers()
    return jsonify(container_info)

@api_bp.route('/container/<container_id>')
def container_api(container_id):
    """API endpoint to get detailed information about a specific container"""
    logger.info(f"API request for container {container_id} details")
    details = podman_service.get_container_details(container_id)
    return jsonify(details)

@api_bp.route('/container/<container_id>/logs')
def container_logs_api(container_id):
    """API endpoint to get logs from a specific container"""
    logger.info(f"API request for container {container_id} logs")
    tail = request.args.get('tail', default=100, type=int)
    since = request.args.get('since', default=None, type=str)
    logs = podman_service.get_container_logs(container_id, tail=tail, since=since)
    return jsonify({"logs": logs})
