# src/creatorsync_integration.py
"""
Module for integrating The Finisher with CreatorSync.

This module handles data synchronization between The Finisher
and CreatorSync by sending project information to the CreatorSync API.
"""

import requests
import json

# Configuration constants (update these with your actual endpoint and API key)
CREATOR_SYNC_API_URL = "https://api.creatorsync.com/sync"
API_KEY = "your_api_key_here"  # Replace with your actual API key

def sync_project_data(project_data):
    """
    Synchronize project data with CreatorSync.
    
    Args:
        project_data (dict): A dictionary containing project details to be synced.
        
    Returns:
        dict: The response from the CreatorSync API if successful; None otherwise.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        response = requests.post(
            CREATOR_SYNC_API_URL,
            headers=headers,
            data=json.dumps(project_data)
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        print("Sync successful:", result)
        return result
    except requests.RequestException as e:
        print("Error syncing project data:", e)
        return None

def main():
    # Sample project data to sync
    project_data = {
        "project_id": "finisher_001",
        "song_title": "Untitled",
        "lyrics": "Sample lyrics here",
        "status": "in_progress"
    }
    
    # Attempt to sync data with CreatorSync
    sync_project_data(project_data)

if __name__ == "__main__":
    main()
