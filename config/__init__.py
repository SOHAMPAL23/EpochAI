"""
Configuration module for EpochAI
"""

from .settings import Settings, ModelConfig, WebConfig
from .logging_config import setup_logging

__all__ = ['Settings', 'ModelConfig', 'WebConfig', 'setup_logging']