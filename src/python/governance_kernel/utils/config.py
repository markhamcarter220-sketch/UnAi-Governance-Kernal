"""
Configuration Management

Manages kernel configuration and settings.
"""

from typing import Dict, Any, Optional
import json


class Config:
    """
    Kernel configuration management.

    Handles configuration loading, validation, and access.
    """

    DEFAULT_CONFIG = {
        'strict_mode': True,
        'enable_audit': True,
        'audit_log_file': None,
        'latency_budget_us': 1000,  # 1ms budget
        'enable_all_invariants': True,
        'custom_invariants': [],
    }

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.

        Args:
            config_dict: Configuration dictionary (uses defaults if None)
        """
        self.config = self.DEFAULT_CONFIG.copy()

        if config_dict:
            self.config.update(config_dict)

    @classmethod
    def from_file(cls, config_file: str) -> 'Config':
        """
        Load configuration from JSON file.

        Args:
            config_file: Path to JSON config file

        Returns:
            Config instance
        """
        with open(config_file, 'r') as f:
            config_dict = json.load(f)

        return cls(config_dict)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
