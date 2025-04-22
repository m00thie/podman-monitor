from flask import Blueprint, jsonify, request
from services.podman_service import PodmanService
from services.container_service import ContainerService
from services.logger_service import get_logger

# Create a logger
logger = get_logger('api-routes')

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create service instances
podman_service = PodmanService()
container_service = ContainerService()

@api_bp.route('/containers')
def containers():
    """API endpoint to get container information with optional filtering and sorting"""
    filter_type = request.args.get('filter', default='all', type=str)
    sort_type = request.args.get('sort', default='healthy-first', type=str)

    logger.info(f"API request for container information with filter={filter_type}, sort={sort_type}")

    # Get all containers
    container_info = podman_service.get_all_containers()

    # Check if there was an error
    if isinstance(container_info, dict) and 'error' in container_info:
        return jsonify(container_info)

    # Apply filtering if requested
    if filter_type != 'all':
        container_info = container_service.filter_containers(container_info, filter_type)

    # Apply sorting if requested
    if sort_type in ['healthy-first', 'unhealthy-first']:
        container_info = container_service.sort_containers(container_info, sort_type)

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

@api_bp.route('/containers/prune', methods=['POST'])
def prune_containers_api():
    """API endpoint to prune all stopped containers"""
    logger.info("API request to prune containers")
    result = podman_service.prune_containers()
    return jsonify(result)

@api_bp.route('/container/<container_id>/start', methods=['POST'])
def start_container_api(container_id):
    """API endpoint to start a container"""
    logger.info(f"API request to start container {container_id}")
    result = podman_service.start_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/stop', methods=['POST'])
def stop_container_api(container_id):
    """API endpoint to stop a container"""
    logger.info(f"API request to stop container {container_id}")
    result = podman_service.stop_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/restart', methods=['POST'])
def restart_container_api(container_id):
    """API endpoint to restart a container"""
    logger.info(f"API request to restart container {container_id}")
    result = podman_service.restart_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/kill', methods=['POST'])
def kill_container_api(container_id):
    """API endpoint to kill a container"""
    logger.info(f"API request to kill container {container_id}")
    result = podman_service.kill_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/delete', methods=['POST'])
def delete_container_api(container_id):
    """API endpoint to delete a container"""
    logger.info(f"API request to delete container {container_id}")
    result = podman_service.delete_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/pause', methods=['POST'])
def pause_container_api(container_id):
    """API endpoint to pause a container"""
    logger.info(f"API request to pause container {container_id}")
    result = podman_service.pause_container(container_id)
    return jsonify(result)

@api_bp.route('/container/<container_id>/unpause', methods=['POST'])
def unpause_container_api(container_id):
    """API endpoint to unpause a container"""
    logger.info(f"API request to unpause container {container_id}")
    result = podman_service.unpause_container(container_id)
    return jsonify(result)
