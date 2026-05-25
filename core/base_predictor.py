"""
Base predictor interface for all prediction models
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .data_models import MarketData, PredictionResult


class BasePredictor(ABC):
    """Abstract base class for all prediction models"""
    
    def __init__(self):
        self.is_trained = False
        self.model_name = self.__class__.__name__
    
    @abstractmethod
    def train(self, historical_data: List[MarketData]) -> None:
        """
        Train the prediction model on historical data
        
        Args:
            historical_data: List of historical market data points
        """
        pass
    
    @abstractmethod
    def predict(self, current_data: MarketData, historical_data: List[MarketData]) -> PredictionResult:
        """
        Make a prediction based on current and historical data
        
        Args:
            current_data: Current market data point
            historical_data: Historical market data for context
            
        Returns:
            PredictionResult containing prediction details
        """
        pass
    
    def is_model_trained(self) -> bool:
        """Check if the model has been trained"""
        return self.is_trained
    
    def get_model_info(self) -> dict:
        """Get information about the model"""
        return {
            'name': self.model_name,
            'is_trained': self.is_trained,
            'type': 'BasePredictor'
        }
    
    def validate_data(self, data: List[MarketData], min_points: int = 10) -> None:
        """
        Validate input data
        
        Args:
            data: Market data to validate
            min_points: Minimum number of data points required
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        if len(data) < min_points:
            raise ValueError(f"Insufficient data: need at least {min_points} points, got {len(data)}")
        
        # Check for required attributes
        required_attrs = ['timestamp', 'price', 'volume', 'close', 'returns']
        for point in data[:5]:  # Check first 5 points
            for attr in required_attrs:
                if not hasattr(point, attr):
                    raise ValueError(f"Missing required attribute: {attr}")
                if getattr(point, attr) is None:
                    raise ValueError(f"Attribute {attr} cannot be None")


class EnsemblePredictor(BasePredictor):
    """Base class for ensemble prediction models"""
    
    def __init__(self):
        super().__init__()
        self.predictors = []
        self.weights = []
    
    def add_predictor(self, predictor: BasePredictor, weight: float = 1.0) -> None:
        """
        Add a predictor to the ensemble
        
        Args:
            predictor: Predictor to add
            weight: Weight for this predictor in ensemble
        """
        self.predictors.append(predictor)
        self.weights.append(weight)
    
    def get_ensemble_info(self) -> dict:
        """Get information about the ensemble"""
        return {
            'name': self.model_name,
            'is_trained': self.is_trained,
            'type': 'EnsemblePredictor',
            'num_predictors': len(self.predictors),
            'predictor_names': [p.model_name for p in self.predictors],
            'weights': self.weights
        }