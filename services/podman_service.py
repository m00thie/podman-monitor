import os
import json
import podman
import requests
from datetime import datetime
from typing import Union, List, Dict, Any, Optional
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

    def get_all_images(self) -> List[Dict[str, Any]]:
        """Get all images from Podman"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get list of images
            images = podman_client.images.list()

            # Convert image objects to dictionaries
            image_list = []
            for image in images:
                image_dict = {
                    'Id': image.id,
                    'Tags': image.tags,
                    'Created': image.attrs['Created'],
                    'Size': image.attrs['Size'],
                    'RepoTags': image.attrs.get('RepoTags', []),
                    'RepoDigests': image.attrs.get('RepoDigests', [])
                }
                image_list.append(image_dict)

            logger.debug(f"Podman API response for images: {json.dumps(image_list, indent=2)}")
            return image_list
        except Exception as e:
            error_msg = f"Error getting images: {str(e)}"
            logger.error(error_msg, e)
            return [{"error": error_msg}]

    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific image"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get image by ID
            image = podman_client.images.get(image_id)

            # Get detailed information
            details = {
                'Id': image.id,
                'Tags': image.tags,
                'Created': image.attrs['Created'],
                'Size': image.attrs['Size'],
                'Architecture': image.attrs.get('Architecture', ''),
                'Os': image.attrs.get('Os', ''),
                'Author': image.attrs.get('Author', ''),
                'RepoTags': image.attrs.get('RepoTags', []),
                'RepoDigests': image.attrs.get('RepoDigests', []),
                'Config': image.attrs.get('Config', {}),
                'RootFS': image.attrs.get('RootFS', {})
            }

            return details
        except Exception as e:
            error_msg = f"Error getting image details: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def get_image_history(self, image_id: str) -> List[Dict[str, Any]]:
        """Get the build history of a specific image"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get image by ID
            image = podman_client.images.get(image_id)

            # Get image history
            history = image.history()

            # Log the raw history data
            logger.debug(f"Raw image history from Podman API: {json.dumps(history, indent=2)}")
            logger.info(f"Number of layers in image history: {len(history)}")

            # Convert history objects to dictionaries
            history_list = []
            for item in history:
                history_item = {
                    'Id': item.get('Id', ''),
                    'Created': item.get('Created', ''),
                    'CreatedBy': item.get('CreatedBy', ''),
                    'Size': item.get('Size', 0),
                    'Comment': item.get('Comment', '')
                }
                history_list.append(history_item)

            logger.debug(f"Podman API response for image history: {json.dumps(history_list, indent=2)}")
            return history_list
        except Exception as e:
            error_msg = f"Error getting image history: {str(e)}"
            logger.error(error_msg, e)
            return [{"error": error_msg}]

    def get_containers_by_image(self, image_name: str, image_tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get containers that use a specific image"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Get all containers
            all_containers = self.get_all_containers()

            # Filter containers by image name and tag
            filtered_containers = []
            for container in all_containers:
                if isinstance(container, dict) and 'error' not in container:
                    container_image = container.get('Image', '')

                    # Parse image name and tag
                    parts = container_image.split(':')
                    container_image_name = parts[0]
                    container_image_tag = parts[1] if len(parts) > 1 else 'latest'

                    # Check if the container uses the specified image
                    if container_image_name == image_name:
                        if image_tag is None or container_image_tag == image_tag:
                            filtered_containers.append(container)

            return filtered_containers
        except Exception as e:
            error_msg = f"Error getting containers by image: {str(e)}"
            logger.error(error_msg, e)
            return [{"error": error_msg}]

    def get_image_tags(self, image_name: str) -> Dict[str, Any]:
        """Get available tags for an image from Docker Hub"""
        try:
            # Parse image name to handle library images and namespaced images
            if '/' not in image_name:
                # Official image (e.g., ubuntu, nginx)
                repo_url = f"https://hub.docker.com/v2/repositories/library/{image_name}/tags"
            else:
                # User/org image (e.g., user/app, organization/app)
                repo_url = f"https://hub.docker.com/v2/repositories/{image_name}/tags"

            logger.info(f"Fetching tags for image: {image_name} from {repo_url}")

            # Make request to Docker Hub API
            response = requests.get(repo_url, params={"page_size": 100})
            response.raise_for_status()

            data = response.json()

            # Extract tags from response
            tags = []
            if "results" in data:
                for result in data["results"]:
                    if "name" in result:
                        tags.append(result["name"])

            # Sort tags (latest first, then alphabetically)
            if "latest" in tags:
                tags.remove("latest")
                sorted_tags = ["latest"] + sorted(tags)
            else:
                sorted_tags = sorted(tags)

            return {
                "success": True,
                "tags": sorted_tags
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching tags for image {image_name}: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error fetching tags for image {image_name}: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}

    def pull_image(self, image_name: str, tag: str = "latest") -> Dict[str, Any]:
        """Pull an image from a registry"""
        try:
            # Create a Podman client
            podman_client = self._create_client()

            # Format the image name with tag
            full_image_name = f"{image_name}:{tag}"

            # Pull the image
            logger.info(f"Pulling image: {full_image_name}")
            image = podman_client.images.pull(full_image_name)

            # Return success response
            return {
                "success": True, 
                "message": f"Successfully pulled image {full_image_name}",
                "image_id": image.id
            }
        except Exception as e:
            error_msg = f"Error pulling image {image_name}:{tag}: {str(e)}"
            logger.error(error_msg, e)
            return {"error": error_msg}
