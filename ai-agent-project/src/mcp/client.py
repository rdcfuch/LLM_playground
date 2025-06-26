from typing import Any, Dict
import requests
import yaml

class MCPClient:
    def __init__(self, config_file: str):
        self.config = self.load_config(config_file)
        self.base_url = self.config.get("mcp_server_url", "http://localhost:5000")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def send_request(self, endpoint: str, data: Dict[str, Any]) -> Any:
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_response(self, endpoint: str) -> Any:
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()