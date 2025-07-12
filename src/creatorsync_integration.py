"""
Module for integrating The Finisher with CreatorSync.

This module provides robust, scalable synchronization of project data with the CreatorSync
platform, featuring advanced error handling, logging, and batch processing capabilities.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Union
from retry import retry
from pydantic import BaseModel, Field, ValidationError
import os
from datetime import datetime
import yaml

# Configure logging for monitoring and analytics, critical for operational insights
logging.basicConfig(
    filename='creatorsync_integration.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load configuration from environment variables or config file for secure and flexible deployment
CONFIG_FILE = os.getenv('CREATORSYNC_CONFIG', 'config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}
    logging.warning("Configuration file not found, using environment variables")

CREATOR_SYNC_API_URL = config.get('CREATOR_SYNC_API_URL', os.getenv('CREATOR_SYNC_API_URL', 'https://api.creatorsync.com/sync'))
API_KEY = config.get('API_KEY', os.getenv('API_KEY', 'your_api_key_here'))
TIMEOUT = config.get('TIMEOUT', 10)  # Default timeout in seconds
MAX_RETRIES = config.get('MAX_RETRIES', 3)  # Default retry attempts
RETRY_DELAY = config.get('RETRY_DELAY', 2)  # Default delay between retries in seconds

# Pydantic model for project data validation, ensuring data integrity
class ProjectData(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=50)
    song_title: str = Field(..., min_length=1, max_length=100)
    lyrics: str = Field(default="", max_length=10000)
    status: str = Field(default="in_progress", pattern="^(in_progress|completed|draft)$")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = Field(default_factory=dict)

class CreatorSyncClient:
    """Client for interacting with the CreatorSync API, designed for scalability and reliability."""
    
    def __init__(self, api_url: str = CREATOR_SYNC_API_URL, api_key: str = API_KEY):
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.session = requests.Session()  # Reuse connections for performance
        logging.info("CreatorSyncClient initialized")

    @retry(requests.RequestException, tries=MAX_RETRIES, delay=RETRY_DELAY, backoff=2, jitter=(0, 1))
    def sync_project_data(self, project_data: Dict) -> Optional[Dict]:
        """
        Synchronize a single project's data with CreatorSync, with retry logic for reliability.
        
        Args:
            project_data (dict): Validated project details to sync.
            
        Returns:
            Optional[Dict]: API response if successful; None otherwise.
        """
        try:
            # Validate project data using Pydantic
            validated_data = ProjectData(**project_data).dict()
            logging.info(f"Syncing project: {validated_data['project_id']}")
            
            response = self.session.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(validated_data),
                timeout=TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            logging.info(f"Sync successful for project {validated_data['project_id']}: {result}")
            return result
        except ValidationError as e:
            logging.error(f"Validation error for project data: {e}")
            return None
        except requests.RequestException as e:
            logging.error(f"Error syncing project {project_data.get('project_id', 'unknown')}: {e}")
            raise  # Let retry mechanism handle retries

    def sync_batch_projects(self, projects: List[Dict]) -> List[Dict]:
        """
        Synchronize multiple projects in a batch, optimizing for high-volume data processing.
        
        Args:
            projects (List[Dict]): List of project data dictionaries to sync.
            
        Returns:
            List[Dict]: List of sync results for each project.
        """
        results = []
        for project in projects:
            result = self.sync_project_data(project)
            results.append({
                "project_id": project.get("project_id", "unknown"),
                "status": "success" if result else "failed",
                "response": result
            })
        logging.info(f"Batch sync completed: {len(results)} projects processed")
        return results

    def close(self):
        """Close the session to free resources, ensuring efficient resource management."""
        self.session.close()
        logging.info("CreatorSyncClient session closed")

def main():
    """Main function demonstrating integration usage, ready for production deployment."""
    client = CreatorSyncClient()
    
    # Sample project data for demonstration
    sample_projects = [
        {
            "project_id": "finisher_001",
            "song_title": "Untitled",
            "lyrics": "Sample lyrics here",
            "status": "in_progress",
            "metadata": {"genre": "pop", "artist": "Demo Artist"}
        },
        {
            "project_id": "finisher_002",
            "song_title": "Dreamscape",
            "lyrics": "Another set of lyrics",
            "status": "draft",
            "metadata": {"genre": "rock", "artist": "Demo Band"}
        }
    ]
    
    # Perform batch synchronization
    results = client.sync_batch_projects(sample_projects)
    for result in results:
        print(f"Project {result['project_id']}: {result['status']}")
    
    client.close()

if __name__ == "__main__":
    main()
