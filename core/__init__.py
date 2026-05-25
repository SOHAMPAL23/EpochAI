"""
EpochAI Core Module
Contains fundamental data structures and base classes
"""

from .data_models import MarketData, PredictionResult
from .base_predictor import BasePredictor
from .exceptions import EpochAIException, InsufficientDataError, ModelNotTrainedError

__all__ = [
    'MarketData',
    'PredictionResult', 
    'BasePredictor',
    'EpochAIException',
    'InsufficientDataError',
    'ModelNotTrainedError'
]