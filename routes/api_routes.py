from flask import Blueprint, jsonify, request
from services.podman_service import PodmanService
from services.container_service import ContainerService
from services.logger_service import get_logger
from typing import Dict, List, Any

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

@api_bp.route('/images')
def images_api():
    """API endpoint to get image information"""
    logger.info("API request for image information")

    # Get all images
    image_info = podman_service.get_all_images()

    # Check if there was an error
    if len(image_info) == 1 and isinstance(image_info[0], dict) and 'error' in image_info[0]:
        return jsonify(image_info[0])

    return jsonify(image_info)

@api_bp.route('/image/<image_id>')
def image_api(image_id):
    """API endpoint to get detailed information about a specific image"""
    logger.info(f"API request for image {image_id} details")
    details = podman_service.get_image_details(image_id)
    return jsonify(details)

@api_bp.route('/image/<image_id>/history')
def image_history_api(image_id):
    """API endpoint to get the build history of a specific image"""
    logger.info(f"API request for image {image_id} build history")
    history = podman_service.get_image_history(image_id)
    return jsonify(history)

@api_bp.route('/image/<image_id>/containers')
def image_containers_api(image_id):
    """API endpoint to get containers using a specific image"""
    logger.info(f"API request for containers using image {image_id}")

    # Get image details to get tags
    image_details = podman_service.get_image_details(image_id)
    containers = []

    # If we have tags, get containers using this image
    if 'Tags' in image_details and image_details['Tags']:
        for tag in image_details['Tags']:
            # Parse image name and tag
            parts = tag.split(':')
            image_name = parts[0]
            image_tag = parts[1] if len(parts) > 1 else 'latest'

            # Get containers using this image
            image_containers = podman_service.get_containers_by_image(image_name, image_tag)
            containers.extend(image_containers)

    return jsonify(containers)

@api_bp.route('/containers/by-image')
def containers_by_image_api():
    """API endpoint to get containers using a specific image name and tag"""
    image_name = request.args.get('name', type=str)
    image_tag = request.args.get('tag', type=str)

    if not image_name:
        return jsonify({"error": "Image name is required"})

    logger.info(f"API request for containers using image {image_name}:{image_tag if image_tag else 'any'}")

    # Get containers using this image
    containers = podman_service.get_containers_by_image(image_name, image_tag)

    return jsonify(containers)

@api_bp.route('/images/tags', methods=['GET'])
def get_image_tags_api():
    """API endpoint to get available tags for an image"""
    image_name = request.args.get('name')

    if not image_name:
        return jsonify({"error": "Image name is required"})

    logger.info(f"API request to get tags for image {image_name}")

    # Get image tags
    result = podman_service.get_image_tags(image_name)

    return jsonify(result)

@api_bp.route('/images/pull', methods=['POST'])
def pull_image_api():
    """API endpoint to pull an image from a registry"""
    data = request.json
    image_name = data.get('name')
    image_tag = data.get('tag', 'latest')

    if not image_name:
        return jsonify({"error": "Image name is required"})

    logger.info(f"API request to pull image {image_name}:{image_tag}")

    # Pull the image
    result = podman_service.pull_image(image_name, image_tag)

    return jsonify(result)
