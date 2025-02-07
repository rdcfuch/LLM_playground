import os
import re

def parse_env_value(value):
    """Parse environment variable value, handling quoted strings and special characters."""
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # If value is wrapped in quotes, remove them and handle escape characters
    if (value.startswith('\'') and value.endswith('\'')) or \
       (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
    
    return value

def load_env(env_path='.env'):
    """Load environment variables from .env file."""
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment file {env_path} not found")
    
    env_vars = {}
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Find the first = character (ignoring = in the value)
            if '=' not in line:
                continue
                
            key, value = line.split('=', 1)
            key = key.strip()
            
            if not key:
                continue
                
            # Parse the value
            value = parse_env_value(value)
            
            # Store in dictionary
            env_vars[key] = value
            
            # Set environment variable
            os.environ[key] = value
    
    return env_vars

def export_env(env_path='.env'):
    """Export environment variables and return them as a dictionary."""
    try:
        env_vars = load_env(env_path)
        print(f"Successfully loaded {len(env_vars)} environment variables from {env_path}")
        return env_vars
    except Exception as e:
        print(f"Error loading environment variables: {str(e)}")
        return {}

if __name__ == '__main__':
    # Get the absolute path to the .env file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    
    # Export environment variables
    env_vars = export_env(env_path)
    
    # Print loaded variables (excluding sensitive information)
    print("\nLoaded environment variables:")
    for key in env_vars:
        # Mask sensitive value
        print(f"{key}={env_vars[key]}")