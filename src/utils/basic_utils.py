import os

#  ******** FUnction to load YAML config files ********
import yaml 
def load_yaml_config(file_path: str) -> dict:
    """Load a YAML configuration file and return its contents as a dictionary."""
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


#  ******** Function to save dictionary to YAML file ********def safe_set_env(var_name: str, default: str = ""):
def safe_set_env(var_name: str, default: str = ""):
    """Safely set os.environ with string default - No NoneType errors."""
    value = os.getenv(var_name, default)
    if value is None:
        value = default
    os.environ[var_name] = str(value)