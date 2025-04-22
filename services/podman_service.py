import os
import json
import podman
from datetime import datetime
from typing import Union, List, Dict, Any
from services.logger_service import get_logger

logger = get_logger('podman-service')

class PodmanService:
    """Service class for Podman container operations"""

    def __init__(self, socket_url=None):
        """Initialize the PodmanService with the socket URL"""
        self.socket_url = socket_url or os.environ.get('PODMAN_SOCKET', 'unix:///run/podman/podman.sock')

    def _create_client(self):
        """Create and return a new Podman client instance"""
        return podman.PodmanClient(base_url=self.socket_url)

    def get_all_containers(self) -> List[Dict[str, Any]]:
        """Connect to the Podman socket and retrieve container information"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

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

    def get_container_details(self, container_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)
            container.reload()

            # Get detailed information
            details = {
                'Id': container.id,
                'Name': container.name,
                'Image': container.image.tags[0] if container.image.tags else container.image.id,
                'Status': container.status,
                'Created': container.attrs['Created'],
                'Ports': container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                'Command': container.attrs.get('Config', {}).get('Cmd', []),
                'Entrypoint': container.attrs.get('Config', {}).get('Entrypoint', []),
                'Environment': container.attrs.get('Config', {}).get('Env', []),
                'Mounts': container.attrs.get('Mounts', []),
                'NetworkSettings': container.attrs.get('NetworkSettings', {})
            }

            return details
        except Exception as e:
            error_msg = f"Error getting container details: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def get_container_logs(self, container_id: str, tail: int = 100, 
                          since: Union[str, datetime, int, None] = None) -> str:
        """Get logs from a specific container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)
            container.reload()

            # Get logs - properly handle the generator
            # Add since parameter if provided
            kwargs = {'tail': tail, 'stream': False, 'stdout': True, 'stderr': True}

            if since:
                if isinstance(since, str):
                    try:
                        since = datetime.fromisoformat(since)
                    except ValueError:
                        try:
                            since = datetime.fromtimestamp(float(since))
                        except ValueError:
                            raise ValueError("Invalid since format. Use ISO format or epoch timestamp")
                if isinstance(since, datetime):
                    kwargs['since'] = int(since.timestamp())
                elif isinstance(since, (int, float)):
                    kwargs['since'] = int(since)
                else:
                    raise ValueError("since must be a string, datetime object, or seconds since epoch")

            logs_generator = container.logs(stdout=True, stderr=True)

            # If it's bytes, decode it directly
            if isinstance(logs_generator, bytes):
                return logs_generator.decode('utf-8')

            # If it's a generator, collect and decode each chunk
            logs = []
            for chunk in logs_generator:
                if isinstance(chunk, bytes):
                    logs.append(chunk.decode('utf-8'))
                else:
                    logs.append(str(chunk))

            return ''.join(logs)
        except Exception as e:
            error_msg = f"Error getting container logs: {str(e)}"
            logger.error(error_msg, e)
            return f"Error: {error_msg}"

    def prune_containers(self) -> Dict[str, Any]:
        """Prune all stopped containers"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Prune containers
            prune = podman_client.containers.prune()

            logger.info(f"Pruned containers:\n {prune['ContainersDeleted']}")
            return {"prunedCount": len(prune['ContainersDeleted'])}
        except Exception as e:
            error_msg = f"Error pruning containers: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def start_container(self, container_id: str) -> Dict[str, Any]:
        """Start a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Start the container
            container.start()

            logger.info(f"Started container: {container_id}")
            return {"success": True, "message": "Container started successfully"}
        except Exception as e:
            error_msg = f"Error starting container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def stop_container(self, container_id: str) -> Dict[str, Any]:
        """Stop a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Stop the container
            container.stop()

            logger.info(f"Stopped container: {container_id}")
            return {"success": True, "message": "Container stopped successfully"}
        except Exception as e:
            error_msg = f"Error stopping container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def restart_container(self, container_id: str) -> Dict[str, Any]:
        """Restart a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Restart the container
            container.restart()

            logger.info(f"Restarted container: {container_id}")
            return {"success": True, "message": "Container restarted successfully"}
        except Exception as e:
            error_msg = f"Error restarting container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def kill_container(self, container_id: str) -> Dict[str, Any]:
        """Kill a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Kill the container
            container.kill()

            logger.info(f"Killed container: {container_id}")
            return {"success": True, "message": "Container killed successfully"}
        except Exception as e:
            error_msg = f"Error killing container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def delete_container(self, container_id: str) -> Dict[str, Any]:
        """Delete a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Remove the container
            container.remove()

            logger.info(f"Deleted container: {container_id}")
            return {"success": True, "message": "Container deleted successfully"}
        except Exception as e:
            error_msg = f"Error deleting container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def pause_container(self, container_id: str) -> Dict[str, Any]:
        """Pause a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Pause the container
            container.pause()

            logger.info(f"Paused container: {container_id}")
            return {"success": True, "message": "Container paused successfully"}
        except Exception as e:
            error_msg = f"Error pausing container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def unpause_container(self, container_id: str) -> Dict[str, Any]:
        """Unpause a container"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get container by ID
            container = podman_client.containers.get(container_id)

            # Unpause the container
            container.unpause()

            logger.info(f"Unpaused container: {container_id}")
            return {"success": True, "message": "Container unpaused successfully"}
        except Exception as e:
            error_msg = f"Error unpausing container: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}
