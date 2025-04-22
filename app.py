import os
import logging
from flask import Flask

# Import routes
from routes.web_routes import web_bp
from routes.api_routes import api_bp
from services.logger_service import get_logger

# Create Flask application
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
logger = get_logger('podman-monitor')

# Register blueprints
app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    logger.info("Starting Podman Monitor application")
    app.run(host='0.0.0.0', port=5000, debug=True)
