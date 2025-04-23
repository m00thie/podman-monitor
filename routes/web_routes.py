from flask import Blueprint, render_template
from services.podman_service import PodmanService
from services.logger_service import get_logger

# Create a logger
logger = get_logger('web-routes')

# Create a Blueprint for web routes
web_bp = Blueprint('web', __name__)

# Create a PodmanService instance
podman_service = PodmanService()

@web_bp.route('/')
def index():
    """Render the index page with general information about Podman"""
    logger.info("Serving index page")
    return render_template('index.html')

@web_bp.route('/containers')
def containers():
    """Render the containers list page"""
    logger.info("Serving containers list page")
    return render_template('containers.html')

@web_bp.route('/container/<container_id>')
def container_details(container_id):
    """Render the container details page"""
    logger.info(f"Serving container details page for container {container_id}")
    details = podman_service.get_container_details(container_id)
    logs = podman_service.get_container_logs(container_id)
    return render_template('container.html', container=details, logs=logs)

@web_bp.route('/images')
def images():
    """Render the images list page"""
    logger.info("Serving images list page")
    return render_template('images.html')

@web_bp.route('/image/<image_id>')
def image_details(image_id):
    """Render the image details page"""
    logger.info(f"Serving image details page for image {image_id}")
    details = podman_service.get_image_details(image_id)
    containers = []

    # If we have tags, get containers using this image
    if 'Tags' in details and details['Tags']:
        for tag in details['Tags']:
            # Parse image name and tag
            parts = tag.split(':')
            image_name = parts[0]
            image_tag = parts[1] if len(parts) > 1 else 'latest'

            # Get containers using this image
            image_containers = podman_service.get_containers_by_image(image_name, image_tag)
            containers.extend(image_containers)

    return render_template('image.html', image=details, containers=containers)
