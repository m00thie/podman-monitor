from typing import List, Dict, Any
from services.logger_service import get_logger

logger = get_logger('container-service')

class ContainerService:
    """Service class for container filtering and sorting operations"""

    @staticmethod
    def filter_containers(containers: List[Dict[str, Any]], filter_type: str) -> List[Dict[str, Any]]:
        """
        Filter containers based on the specified filter type
        
        Args:
            containers: List of container dictionaries
            filter_type: Type of filter to apply ('all', 'healthy', 'unhealthy')
            
        Returns:
            Filtered list of containers
        """
        if not containers or filter_type == 'all':
            return containers
            
        logger.info(f"Filtering containers by: {filter_type}")
        
        filtered = []
        for container in containers:
            is_healthy = ContainerService.is_container_healthy(container)
            
            if (filter_type == 'healthy' and is_healthy) or (filter_type == 'unhealthy' and not is_healthy):
                filtered.append(container)
                
        return filtered
    
    @staticmethod
    def sort_containers(containers: List[Dict[str, Any]], sort_type: str) -> List[Dict[str, Any]]:
        """
        Sort containers based on the specified sort type
        
        Args:
            containers: List of container dictionaries
            sort_type: Type of sort to apply ('healthy-first', 'unhealthy-first')
            
        Returns:
            Sorted list of containers
        """
        if not containers:
            return containers
            
        logger.info(f"Sorting containers by: {sort_type}")
        
        # Create a copy to avoid modifying the original list
        sorted_containers = containers.copy()
        
        # Sort based on health status
        sorted_containers.sort(
            key=lambda c: ContainerService.is_container_healthy(c),
            reverse=(sort_type == 'healthy-first')
        )
        
        return sorted_containers
    
    @staticmethod
    def is_container_healthy(container: Dict[str, Any]) -> bool:
        """
        Determine if a container is healthy based on its status
        
        Args:
            container: Container dictionary
            
        Returns:
            True if the container is healthy, False otherwise
        """
        if not container or 'Status' not in container:
            return False
            
        return 'running' in container['Status'].lower()