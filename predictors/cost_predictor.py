"""
Advanced cost prediction model with comprehensive features
"""

import numpy as np
from typing import List, Dict
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from core.base_predictor import BasePredictor
from core.data_models import MarketData, PredictionResult
from core.exceptions import InsufficientDataError, ModelNotTrainedError
from features.extractors import BasicFeatureExtractor
from risk.managers import BasicRiskManager
from risk.regime_detection import BasicRegimeDetector
from config.logging_config import get_logger

logger = get_logger('predictors')


class AdvancedCostPredictor(BasePredictor):
    """
    Advanced cost prediction model with comprehensive algorithms and risk management
    """
    
    def __init__(self, model_type: str = 'ensemble'):
        super().__init__()
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Initialize components
        self.feature_extractor = BasicFeatureExtractor()
        self.regime_detector = BasicRegimeDetector()
        self.risk_manager = BasicRiskManager()
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize prediction models"""
        self.models = {
            'xgboost': GradientBoostingRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=300,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'linear': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        # Initialize scalers
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
    
    def train(self, historical_data: List[MarketData]) -> None:
        """Train the prediction models"""
        if len(historical_data) < 30:
            raise InsufficientDataError(30, len(historical_data))
        
        logger.info(f"Training {self.model_name} with {len(historical_data)} data points")
        
        try:
            # Generate features
            X = self.feature_extractor.extract_features(historical_data)
            y = np.array([getattr(d, 'returns', 0) for d in historical_data])
            
            # Split data for training and validation
            split_idx = int(0.8 * len(X))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            if len(X_train) == 0 or len(y_train) == 0:
                raise InsufficientDataError(1, 0, "Not enough data for training after splitting")
            
            # Train each model
            for model_name, model in self.models.items():
                logger.debug(f"Training {model_name} model")
                X_train_scaled = self.scalers[model_name].fit_transform(X_train)
                model.fit(X_train_scaled, y_train)
                
                # Store feature importance
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[model_name] = model.feature_importances_
            
            self.is_trained = True
            logger.info(f"✅ {self.model_name} trained successfully")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def predict(self, current_data: MarketData, historical_data: List[MarketData]) -> PredictionResult:
        """Make a prediction for cost/price movement"""
        if not self.is_trained:
            raise ModelNotTrainedError(self.model_name)
        
        try:
            # Generate features for current data
            X_current = self.feature_extractor.extract_features([current_data])[0].reshape(1, -1)
            
            # Get predictions from all models
            predictions = {}
            for model_name, model in self.models.items():
                X_scaled = self.scalers[model_name].transform(X_current)
                pred = model.predict(X_scaled)[0]
                predictions[model_name] = pred
            
            # Ensemble prediction (weighted average)
            ensemble_pred = np.mean(list(predictions.values()))
            
            # Calculate confidence based on model agreement
            pred_values = list(predictions.values())
            confidence = 1.0 - (np.std(pred_values) / (abs(np.mean(pred_values)) + 0.001))
            confidence = min(0.95, max(0.3, confidence))  # Clamp between 0.3 and 0.95
            
            # Determine direction
            direction = 'UP' if ensemble_pred > 0 else 'DOWN'
            
            # Generate quantiles
            quantiles = self._calculate_quantiles(pred_values)
            
            # Detect market regime
            regime = self.regime_detector.detect_regime(current_data, historical_data[-20:])
            
            # Calculate risk metrics
            risk_metrics = self.risk_manager.calculate_metrics(ensemble_pred, historical_data)
            
            return PredictionResult(
                direction=direction,
                expected_return=ensemble_pred * 100,  # Convert to percentage
                confidence=confidence,
                quantiles=quantiles,
                regime=regime,
                risk_metrics=risk_metrics
            )
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Return neutral prediction on error
            return PredictionResult(
                direction='NEUTRAL',
                expected_return=0.0,
                confidence=0.5,
                quantiles={'p10': -0.5, 'p50': 0.0, 'p90': 0.5},
                regime='UNKNOWN',
                risk_metrics={'var95': 1.0, 'max_drawdown': -5.0}
            )
    
    def _calculate_quantiles(self, predictions: List[float]) -> Dict[str, float]:
        """Calculate prediction quantiles"""
        pred_mean = np.mean(predictions)
        pred_std = np.std(predictions)
        
        return {
            'p10': (pred_mean - 1.28 * pred_std) * 100,
            'p50': pred_mean * 100,
            'p90': (pred_mean + 1.28 * pred_std) * 100
        }
    
    def get_feature_importance(self) -> Dict[str, np.ndarray]:
        """Get feature importance from trained models"""
        if not self.is_trained:
            raise ModelNotTrainedError(self.model_name)
        return self.feature_importance.copy()
    
    def get_model_info(self) -> dict:
        """Get detailed model information"""
        info = super().get_model_info()
        info.update({
            'type': 'AdvancedCostPredictor',
            'model_type': self.model_type,
            'num_models': len(self.models),
            'model_names': list(self.models.keys()),
            'has_feature_importance': bool(self.feature_importance)
        })
        return info