"""
Ultimate performance cost prediction model with maximum optimizations
"""

import numpy as np
from typing import List, Dict
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from collections import deque
import warnings
warnings.filterwarnings('ignore')

from core.base_predictor import BasePredictor
from core.data_models import MarketData, PredictionResult
from core.exceptions import InsufficientDataError, ModelNotTrainedError
from features.extractors import UltraFastFeatureExtractor
from risk.managers import OptimizedRiskManager
from risk.regime_detection import OptimizedRegimeDetector
from config.logging_config import get_logger

logger = get_logger('predictors')


class UltimateCostPredictor(BasePredictor):
    """
    Ultimate performance cost prediction with maximum optimizations
    """
    
    def __init__(self):
        super().__init__()
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Ultra-performance optimization settings
        self.max_training_samples = 1000  # Very limited for speed
        self.feature_cache_size = 50
        self.prediction_cache_size = 10
        
        # Initialize ultra-fast components
        self.feature_extractor = UltraFastFeatureExtractor()
        self.regime_detector = OptimizedRegimeDetector()
        self.risk_manager = OptimizedRiskManager()
        
        # Initialize ultra-lightweight models
        self._initialize_lightweight_models()
    
    def _initialize_lightweight_models(self):
        """Initialize ultra-lightweight, fast models"""
        self.models = {
            'xgboost': GradientBoostingRegressor(
                n_estimators=50,       # Very lightweight
                max_depth=3,           # Shallow trees for speed
                learning_rate=0.1,
                random_state=42,
                subsample=0.8,
                max_features='sqrt'
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=30,       # Very lightweight forest
                max_depth=3,           # Shallow trees
                min_samples_split=8,
                min_samples_leaf=2,
                random_state=42,
                max_features='sqrt'
            )
        }
        
        # Initialize scalers
        for model_name in self.models.keys():
            self.scalers[model_name] = StandardScaler()
    
    def train(self, historical_data: List[MarketData]) -> None:
        """Ultra-fast training"""
        if len(historical_data) < 15:
            raise InsufficientDataError(15, len(historical_data))
        
        logger.info(f"Training {self.model_name} with {len(historical_data)} data points")
        
        # Use only recent data for speed
        if len(historical_data) > self.max_training_samples:
            historical_data = historical_data[-self.max_training_samples:]
        
        try:
            # Generate features
            X = self.feature_extractor.extract_features(historical_data)
            y = np.array([getattr(d, 'returns', 0) for d in historical_data], dtype=np.float32)
            
            # Split data
            split_idx = max(1, int(0.8 * len(X)))
            X_train, y_train = X[:split_idx], y[:split_idx]
            
            # Train models efficiently
            for model_name, model in self.models.items():
                logger.debug(f"Training {model_name} model")
                X_train_scaled = self.scalers[model_name].fit_transform(X_train)
                model.fit(X_train_scaled, y_train)
                
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[model_name] = model.feature_importances_
            
            self.is_trained = True
            logger.info(f"✅ {self.model_name} trained with ultimate speed")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def predict(self, current_data: MarketData, historical_data: List[MarketData]) -> PredictionResult:
        """Ultra-fast prediction"""
        if not self.is_trained:
            raise ModelNotTrainedError(self.model_name)
        
        try:
            # Use minimal recent data only
            if len(historical_data) > 100:
                historical_data = historical_data[-100:]
            
            # Generate features
            X_current = self.feature_extractor.extract_features([current_data])[0].reshape(1, -1)
            
            # Fast ensemble prediction
            predictions = {}
            for model_name, model in self.models.items():
                X_scaled = self.scalers[model_name].transform(X_current)
                pred = model.predict(X_scaled)[0]
                predictions[model_name] = pred
            
            ensemble_pred = np.mean(list(predictions.values()))
            
            # Fast confidence calculation
            pred_values = list(predictions.values())
            confidence = 1.0 - (np.std(pred_values) / (abs(np.mean(pred_values)) + 0.001))
            confidence = min(0.95, max(0.3, confidence))
            
            direction = 'UP' if ensemble_pred > 0 else 'DOWN'
            quantiles = self._calculate_quantiles(pred_values)
            regime = self.regime_detector.detect_regime(current_data, historical_data[-10:])
            risk_metrics = self.risk_manager.calculate_metrics(ensemble_pred, historical_data)
            
            return PredictionResult(
                direction=direction,
                expected_return=ensemble_pred * 100,
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
        """Fast quantile calculation"""
        pred_mean = np.mean(predictions)
        pred_std = np.std(predictions)
        
        return {
            'p10': (pred_mean - 1.28 * pred_std) * 100,
            'p50': pred_mean * 100,
            'p90': (pred_mean + 1.28 * pred_std) * 100
        }
    
    def get_model_info(self) -> dict:
        """Get detailed model information"""
        info = super().get_model_info()
        info.update({
            'type': 'UltimateCostPredictor',
            'max_training_samples': self.max_training_samples,
            'num_models': len(self.models),
            'model_names': list(self.models.keys()),
            'optimization_level': 'Ultimate'
        })
        return info


class UltimatePredictionEngine:
    """Ultra-fast prediction engine with circular buffer"""
    
    def __init__(self):
        self.predictor = UltimateCostPredictor()
        self.data_buffer = deque(maxlen=200)  # Circular buffer for memory efficiency
        self.is_running = False
        self.last_prediction_time = 0
        self.prediction_interval = 0.01  # Predict every 10ms for ultra-high frequency
    
    def add_data_point(self, data_point: MarketData):
        """Ultra-fast data addition"""
        self.data_buffer.append(data_point)
    
    def get_latest_prediction(self) -> PredictionResult:
        """Fast prediction with minimal overhead"""
        if len(self.data_buffer) < 15:
            return None
        
        latest_data = self.data_buffer[-1]
        return self.predictor.predict(latest_data, list(self.data_buffer))
    
    def train_if_needed(self):
        """Fast training check"""
        if len(self.data_buffer) >= 20 and not self.predictor.is_trained:
            self.predictor.train(list(self.data_buffer))
    
    def get_engine_info(self) -> dict:
        """Get engine information"""
        return {
            'predictor_info': self.predictor.get_model_info(),
            'buffer_size': len(self.data_buffer),
            'max_buffer_size': self.data_buffer.maxlen,
            'prediction_interval': self.prediction_interval,
            'is_running': self.is_running
        }