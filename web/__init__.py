"""
Web applications module for EpochAI
"""

from .apps.main_app import create_main_app
from .apps.realtime_app import create_realtime_app
from .apps.simple_app import create_simple_app

__all__ = [
    'create_main_app',
    'create_realtime_app', 
    'create_simple_app'
]