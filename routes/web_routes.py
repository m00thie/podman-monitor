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
    """Render the index page"""
    logger.info("Serving index page")
    return render_template('index.html')

@web_bp.route('/container/<container_id>')
def container_details(container_id):
    """Render the container details page"""
    logger.info(f"Serving container details page for container {container_id}")
    details = podman_service.get_container_details(container_id)
    logs = podman_service.get_container_logs(container_id)
    return render_template('container.html', container=details, logs=logs)
