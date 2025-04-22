import os
import json
import logging
import podman
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('podman_monitor.log')
    ]
)
logger = logging.getLogger('podman-monitor')

# Configuration
PODMAN_SOCKET = os.environ.get('PODMAN_SOCKET', 'unix:///run/podman/podman.sock')

def get_podman_info():
    """Connect to the Podman socket and retrieve container information"""
    try:
        # Get URI from environment or use default
        uri = PODMAN_SOCKET
        
        # Create a Podman client
        podman_client = podman.PodmanClient(base_url=uri)
        
        # Get list of containers
        containers = podman_client.containers.list(all=True)
        
        # Convert container objects to dictionaries
        container_list = []
        for container in containers:
            container.reload()
            container_dict = {
                'Id': container.id,
                'Names': [container.name],
                'Image': container.image.tags[0] if container.image.tags else container.image.id,
                'Status': container.status,
                'State': container.status,
                'Created': container.attrs['Created']
            }
            container_list.append(container_dict)
        
        logger.debug(f"Podman API response: {json.dumps(container_list, indent=2)}")
        return container_list
    except Exception as e:
        error_msg = f"Error connecting to Podman: {str(e)}"
        logger.error(error_msg, e)
        return {"error": error_msg}

@app.route('/')
def index():
    """Render the index page"""
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/api/containers')
def containers():
    """API endpoint to get container information"""
    logger.info("API request for container information")
    container_info = get_podman_info()
    return jsonify(container_info)

if __name__ == '__main__':
    logger.info("Starting Podman Monitor application")
    app.run(host='0.0.0.0', port=5000, debug=True)
