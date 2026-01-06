import yaml
import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Config:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        # Try to find config.yaml in current directory or parent
        paths = [
            os.path.join(os.getcwd(), 'config.yaml'),
            os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        ]
        
        for config_path in paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._config = yaml.safe_load(f) or {}
                    # Don't log here to avoid circular dependency if logger uses config
                    return
                except Exception as e:
                    print(f"Error loading config from {config_path}: {e}")
        
        print("Warning: config.yaml not found, using defaults")
        self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation (e.g. 'general.timezone')"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# Global instance
config = Config()
