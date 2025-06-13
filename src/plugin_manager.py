import importlib
import os

# 🔹 SCALABILITY: This plugin system allows users to extend The Finisher with custom features.
PLUGIN_FOLDER = "src/plugins"

def load_plugins():
    """
    🔹 FUNCTION PURPOSE:
    - Dynamically loads all plugins in the plugins folder.
    - Enables third-party developers to enhance The Finisher.
    
    🔹 WHY IT MATTERS FOR INVESTORS:
    - Creates an open ecosystem for innovation.
    - Encourages community-driven development.
    - Sets the foundation for a future plugin marketplace.
    """
    plugins = {}
    for filename in os.listdir(PLUGIN_FOLDER):
        if filename.endswith(".py") and filename != "plugin_manager.py":
            module_name = f"plugins.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, "run"):
                plugins[module_name] = module.run
    return plugins

def execute_plugin(plugin_name, *args, **kwargs):
    """
    🔹 FUNCTION PURPOSE:
    - Runs a specific plugin if it exists.
    
    🔹 WHY IT MATTERS FOR INVESTORS:
    - Allows users to customize their experience.
    - Opens doors for premium plugin sales.
    """
    plugins = load_plugins()
    if plugin_name in plugins:
        return plugins[plugin_name](*args, **kwargs)
    return f"Plugin '{plugin_name}' not found."

# 🔹 EXAMPLE USAGE:
# Investors can see how plugins are loaded dynamically.
if __name__ == "__main__":
    plugins = load_plugins()
    print(f"Loaded Plugins: {list(plugins.keys())}")
