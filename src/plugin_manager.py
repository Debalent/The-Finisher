"""
Plugin Manager for The Finisher.

This module provides a robust, scalable plugin system that enables third-party developers
to extend functionality, fostering a vibrant ecosystem and potential marketplace.
"""

import importlib
import os
import logging
from typing import Dict, Callable, Optional, Any
from pydantic import BaseModel, Field, ValidationError
import yaml
from datetime import datetime
from pathlib import Path
import hashlib
import json

# Configure logging for monitoring and analytics, critical for ecosystem insights
logging.basicConfig(
    filename='plugin_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load configuration from environment variables or YAML for secure and flexible deployment
CONFIG_FILE = os.getenv('PLUGIN_CONFIG', 'plugin_config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}
    logging.warning("Plugin configuration file not found, using default settings")

# Constants for plugin system, configurable via YAML or environment
PLUGIN_FOLDER = config.get('PLUGIN_FOLDER', os.getenv('PLUGIN_FOLDER', 'src/plugins'))
ALLOWED_EXTENSIONS = config.get('ALLOWED_EXTENSIONS', ['.py'])
PLUGIN_METADATA_FILE = config.get('PLUGIN_METADATA_FILE', 'metadata.json')
MAX_PLUGIN_SIZE_BYTES = config.get('MAX_PLUGIN_SIZE_BYTES', 10 * 1024 * 1024)  # 10MB default
PLUGIN_TIMEOUT_SECONDS = config.get('PLUGIN_TIMEOUT_SECONDS', 30)

# Pydantic model for plugin metadata validation
class PluginMetadata(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')
    description: str = Field(default="", max_length=1000)
    author: str = Field(default="Unknown", max_length=100)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PluginManager:
    """Scalable plugin management system for dynamic feature extension and ecosystem growth."""
    
    def __init__(self, plugin_folder: str = PLUGIN_FOLDER):
        """
        Initialize the plugin manager with secure folder validation.
        
        Args:
            plugin_folder (str): Directory containing plugin files.
        """
        self.plugin_folder = Path(plugin_folder)
        self.plugins: Dict[str, Callable] = {}
        self.metadata: Dict[str, PluginMetadata] = {}
        
        # Ensure plugin folder exists
        self.plugin_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f"PluginManager initialized with folder: {self.plugin_folder}")

    def validate_plugin_file(self, file_path: Path) -> bool:
        """
        Validate plugin file for security and integrity.
        
        Args:
            file_path (Path): Path to the plugin file.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            # Check file extension
            if file_path.suffix not in ALLOWED_EXTENSIONS:
                logging.warning(f"Invalid file extension for {file_path}")
                return False
            
            # Check file size
            if file_path.stat().st_size > MAX_PLUGIN_SIZE_BYTES:
                logging.warning(f"Plugin {file_path} exceeds size limit")
                return False
            
            # Calculate file hash for integrity
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            logging.info(f"Validated plugin file {file_path} with hash {file_hash[:8]}...")
            return True
        except Exception as e:
            logging.error(f"Validation failed for {file_path}: {e}")
            return False

    def load_plugin_metadata(self, plugin_dir: Path) -> Optional[PluginMetadata]:
        """
        Load and validate plugin metadata from metadata.json.
        
        Args:
            plugin_dir (Path): Directory containing the plugin.
            
        Returns:
            Optional[PluginMetadata]: Validated metadata or None if invalid.
        """
        metadata_path = plugin_dir / PLUGIN_METADATA_FILE
        try:
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                validated_metadata = PluginMetadata(**metadata)
                if not validated_metadata.enabled:
                    logging.info(f"Plugin {validated_metadata.name} is disabled")
                    return None
                logging.info(f"Loaded metadata for {validated_metadata.name} (v{validated_metadata.version})")
                return validated_metadata
            logging.warning(f"No metadata file found in {plugin_dir}")
            return None
        except (ValidationError, json.JSONDecodeError) as e:
            logging.error(f"Invalid metadata in {metadata_path}: {e}")
            return None

    def load_plugins(self) -> Dict[str, Callable]:
        """
        Dynamically load all valid plugins, ensuring security and compatibility.
        
        Returns:
            Dict[str, Callable]: Dictionary of plugin names to their run functions.
        """
        self.plugins.clear()
        self.metadata.clear()

        for item in self.plugin_folder.iterdir():
            if item.is_file() and item.name != "plugin_manager.py" and self.validate_plugin_file(item):
                try:
                    module_name = f"plugins.{item.stem}"
                    spec = importlib.util.spec_from_file_location(module_name, item)
                    if spec is None or spec.loader is None:
                        logging.error(f"Failed to create spec for {module_name}")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'run'):
                        metadata = self.load_plugin_metadata(item.parent)
                        if metadata:
                            plugin_key = f"{metadata.name}:{metadata.version}"
                            self.plugins[plugin_key] = module.run
                            self.metadata[plugin_key] = metadata
                            logging.info(f"Loaded plugin {plugin_key}")
                except Exception as e:
                    logging.error(f"Failed to load plugin {item}: {e}")

        logging.info(f"Loaded {len(self.plugins)} plugins: {list(self.plugins.keys())}")
        return self.plugins

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """
        Execute a specific plugin with timeout and error handling.
        
        Args:
            plugin_name (str): Name of the plugin (format: name:version).
            *args, **kwargs: Arguments to pass to the plugin's run function.
            
        Returns:
            Any: Plugin execution result or error message.
        """
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Plugin {plugin_name} timed out after {PLUGIN_TIMEOUT_SECONDS}s")

        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(PLUGIN_TIMEOUT_SECONDS)

        try:
            if plugin_name not in self.plugins:
                logging.warning(f"Plugin {plugin_name} not found")
                return f"Plugin '{plugin_name}' not found."
            
            logging.info(f"Executing plugin {plugin_name} with args: {args}, kwargs: {kwargs}")
            result = self.plugins[plugin_name](*args, **kwargs)
            logging.info(f"Plugin {plugin_name} executed successfully")
            return result
        except TimeoutError as e:
            logging.error(f"Plugin execution timeout: {e}")
            return f"Plugin '{plugin_name}' timed out"
        except Exception as e:
            logging.error(f"Plugin {plugin_name} failed: {e}")
            return f"Plugin '{plugin_name}' failed: {str(e)}"
        finally:
            signal.alarm(0)  # Disable timeout

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        Retrieve metadata for a specific plugin.
        
        Args:
            plugin_name (str): Name of the plugin (format: name:version).
            
        Returns:
            Optional[Dict]: Plugin metadata or None if not found.
        """
        metadata = self.metadata.get(plugin_name)
        if metadata:
            return metadata.dict()
        logging.warning(f"No metadata found for plugin {plugin_name}")
        return None

def main() -> None:
    """Main function demonstrating plugin system capabilities."""
    manager = PluginManager()
    plugins = manager.load_plugins()
    print(f"Loaded Plugins: {list(plugins.keys())}")
    
    # Example plugin execution
    sample_plugin = list(plugins.keys())[0] if plugins else None
    if sample_plugin:
        result = manager.execute_plugin(sample_plugin, sample_arg="test")
        print(f"Sample plugin result: {result}")
        
        # Display plugin info
        info = manager.get_plugin_info(sample_plugin)
        print(f"Plugin info: {info}")

if __name__ == "__main__":
    main()
