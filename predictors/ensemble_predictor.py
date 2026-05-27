"""
Ensemble cost prediction model combining multiple predictors
"""

import numpy as np
from typing import List, Dict, Optional
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from core.base_predictor import EnsemblePredictor
from core.data_models import MarketData, PredictionResult
from core.exceptions import InsufficientDataError, ModelNotTrainedError
from predictors.cost_predictor import AdvancedCostPredictor
from predictors.optimized_predictor import OptimizedCostPredictor
from predictors.ultimate_predictor import UltimateCostPredictor
from config.logging_config import get_logger

logger = get_logger('predictors')


class EnsembleCostPredictor(EnsemblePredictor):
    """
    Ensemble cost prediction model that combines multiple predictors
    """
    
    def __init__(self, predictor_types: List[str] = None, weights: List[float] = None):
        super().__init__()
        
        if predictor_types is None:
            predictor_types = ['advanced', 'optimized', 'ultimate']
        
        if weights is None:
            weights = [0.4, 0.35, 0.25]  # Favor more sophisticated models
        
        if len(predictor_types) != len(weights):
            raise ValueError("Number of predictor types must match number of weights")
        
        # Normalize weights
        total_weight = sum(weights)
        self.weights = [w / total_weight for w in weights]
        
        # Initialize predictors
        for i, pred_type in enumerate(predictor_types):
            predictor = self._create_predictor(pred_type)
            self.add_predictor(predictor, self.weights[i])
        
        logger.info(f"Initialized ensemble with {len(self.predictors)} predictors")
    
    def _create_predictor(self, predictor_type: str):
        """Create a predictor instance based on type"""
        if predictor_type == 'advanced':
            return AdvancedCostPredictor()
        elif predictor_type == 'optimized':
            return OptimizedCostPredictor()
        elif predictor_type == 'ultimate':
            return UltimateCostPredictor()
        else:
            raise ValueError(f"Unknown predictor type: {predictor_type}")
    
    def train(self, historical_data: List[MarketData]) -> None:
        """Train all predictors in the ensemble"""
        if len(historical_data) < 30:
            raise InsufficientDataError(30, len(historical_data))
        
        logger.info(f"Training ensemble with {len(historical_data)} data points")
        
        successful_training = 0
        
        for i, predictor in enumerate(self.predictors):
            try:
                logger.debug(f"Training predictor {i+1}/{len(self.predictors)}: {predictor.model_name}")
                predictor.train(historical_data)
                successful_training += 1
            except Exception as e:
                logger.error(f"Failed to train predictor {predictor.model_name}: {e}")
                # Set weight to 0 for failed predictors
                self.weights[i] = 0.0
        
        if successful_training == 0:
            raise ModelNotTrainedError("All predictors failed to train")
        
        # Renormalize weights after removing failed predictors
        total_weight = sum(self.weights)
        if total_weight > 0:
            self.weights = [w / total_weight for w in self.weights]
        
        self.is_trained = True
        logger.info(f"✅ Ensemble trained successfully with {successful_training}/{len(self.predictors)} predictors")
    
    def predict(self, current_data: MarketData, historical_data: List[MarketData]) -> PredictionResult:
        """Make ensemble prediction by combining individual predictor results"""
        if not self.is_trained:
            raise ModelNotTrainedError(self.model_name)
        
        try:
            # Get predictions from all trained predictors
            predictions = []
            valid_weights = []
            
            for i, predictor in enumerate(self.predictors):
                if self.weights[i] > 0 and predictor.is_trained:
                    try:
                        pred = predictor.predict(current_data, historical_data)
                        predictions.append(pred)
                        valid_weights.append(self.weights[i])
                    except Exception as e:
                        logger.warning(f"Predictor {predictor.model_name} failed to predict: {e}")
                        continue
            
            if not predictions:
                raise ModelNotTrainedError("No predictors available for prediction")
            
            # Normalize weights for valid predictions
            total_weight = sum(valid_weights)
            if total_weight > 0:
                valid_weights = [w / total_weight for w in valid_weights]
            else:
                valid_weights = [1.0 / len(predictions)] * len(predictions)
            
            # Combine predictions using weighted average
            ensemble_prediction = self._combine_predictions(predictions, valid_weights)
            
            return ensemble_prediction
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            # Return neutral prediction on error
            return PredictionResult(
                direction='NEUTRAL',
                expected_return=0.0,
                confidence=0.5,
                quantiles={'p10': -0.5, 'p50': 0.0, 'p90': 0.5},
                regime='UNKNOWN',
                risk_metrics={'var95': 1.0, 'max_drawdown': -5.0}
            )
    
    def _combine_predictions(self, predictions: List[PredictionResult], 
                           weights: List[float]) -> PredictionResult:
        """Combine multiple predictions using weighted averaging"""
        
        # Weighted average of expected returns
        weighted_returns = [pred.expected_return * weight for pred, weight in zip(predictions, weights)]
        ensemble_return = sum(weighted_returns)
        
        # Weighted average of confidences
        weighted_confidences = [pred.confidence * weight for pred, weight in zip(predictions, weights)]
        ensemble_confidence = sum(weighted_confidences)
        
        # Determine ensemble direction based on weighted vote
        up_weight = sum(weight for pred, weight in zip(predictions, weights) if pred.direction == 'UP')
        down_weight = sum(weight for pred, weight in zip(predictions, weights) if pred.direction == 'DOWN')
        neutral_weight = sum(weight for pred, weight in zip(predictions, weights) if pred.direction == 'NEUTRAL')
        
        if up_weight > down_weight and up_weight > neutral_weight:
            ensemble_direction = 'UP'
        elif down_weight > up_weight and down_weight > neutral_weight:
            ensemble_direction = 'DOWN'
        else:
            ensemble_direction = 'NEUTRAL'
        
        # Combine quantiles using weighted averaging
        ensemble_quantiles = {}
        for quantile in ['p10', 'p50', 'p90']:
            weighted_quantiles = [
                pred.quantiles.get(quantile, 0) * weight 
                for pred, weight in zip(predictions, weights)
            ]
            ensemble_quantiles[quantile] = sum(weighted_quantiles)
        
        # Select most common regime (simple majority vote)
        regime_votes = {}
        for pred, weight in zip(predictions, weights):
            regime = pred.regime
            if regime not in regime_votes:
                regime_votes[regime] = 0
            regime_votes[regime] += weight
        
        ensemble_regime = max(regime_votes.items(), key=lambda x: x[1])[0]
        
        # Combine risk metrics using weighted averaging
        ensemble_risk_metrics = {}
        for metric in ['var95', 'max_drawdown']:
            weighted_metrics = [
                pred.risk_metrics.get(metric, 0) * weight 
                for pred, weight in zip(predictions, weights)
            ]
            ensemble_risk_metrics[metric] = sum(weighted_metrics)
        
        return PredictionResult(
            direction=ensemble_direction,
            expected_return=ensemble_return,
            confidence=min(0.95, max(0.3, ensemble_confidence)),  # Clamp confidence
            quantiles=ensemble_quantiles,
            regime=ensemble_regime,
            risk_metrics=ensemble_risk_metrics
        )
    
    def get_predictor_weights(self) -> Dict[str, float]:
        """Get current predictor weights"""
        weights_dict = {}
        for i, predictor in enumerate(self.predictors):
            weights_dict[predictor.model_name] = self.weights[i]
        return weights_dict
    
    def update_weights(self, new_weights: List[float]) -> None:
        """Update predictor weights"""
        if len(new_weights) != len(self.predictors):
            raise ValueError("Number of weights must match number of predictors")
        
        # Normalize weights
        total_weight = sum(new_weights)
        if total_weight > 0:
            self.weights = [w / total_weight for w in new_weights]
        else:
            raise ValueError("All weights cannot be zero")
        
        logger.info(f"Updated ensemble weights: {self.get_predictor_weights()}")
    
    def get_individual_predictions(self, current_data: MarketData, 
                                 historical_data: List[MarketData]) -> Dict[str, PredictionResult]:
        """Get individual predictions from each predictor"""
        if not self.is_trained:
            raise ModelNotTrainedError(self.model_name)
        
        individual_predictions = {}
        
        for predictor in self.predictors:
            if predictor.is_trained:
                try:
                    pred = predictor.predict(current_data, historical_data)
                    individual_predictions[predictor.model_name] = pred
                except Exception as e:
                    logger.warning(f"Failed to get prediction from {predictor.model_name}: {e}")
        
        return individual_predictions
    
    def get_model_info(self) -> dict:
        """Get detailed ensemble information"""
        info = super().get_ensemble_info()
        info.update({
            'type': 'EnsembleCostPredictor',
            'predictor_weights': self.get_predictor_weights(),
            'trained_predictors': sum(1 for p in self.predictors if p.is_trained),
            'total_predictors': len(self.predictors)
        })
        return info


class AdaptiveEnsemblePredictor(EnsembleCostPredictor):
    """
    Adaptive ensemble that adjusts weights based on recent performance
    """
    
    def __init__(self, predictor_types: List[str] = None, adaptation_window: int = 50):
        super().__init__(predictor_types)
        self.adaptation_window = adaptation_window
        self.performance_history = []
        self.adaptive_weights = self.weights.copy()
    
    def predict(self, current_data: MarketData, historical_data: List[MarketData]) -> PredictionResult:
        """Make adaptive prediction with weight adjustment"""
        # Get individual predictions
        individual_preds = self.get_individual_predictions(current_data, historical_data)
        
        # Use adaptive weights if available
        if len(self.performance_history) >= self.adaptation_window:
            self._update_adaptive_weights()
            # Temporarily use adaptive weights
            original_weights = self.weights.copy()
            self.weights = self.adaptive_weights.copy()
        
        # Make ensemble prediction
        prediction = super().predict(current_data, historical_data)
        
        # Restore original weights if they were changed
        if len(self.performance_history) >= self.adaptation_window:
            self.weights = original_weights
        
        # Store prediction for future adaptation (would need actual outcomes)
        self.performance_history.append({
            'timestamp': current_data.timestamp,
            'individual_predictions': individual_preds,
            'ensemble_prediction': prediction
        })
        
        # Maintain history size
        if len(self.performance_history) > self.adaptation_window * 2:
            self.performance_history = self.performance_history[-self.adaptation_window:]
        
        return prediction
    
    def _update_adaptive_weights(self):
        """Update weights based on recent performance (simplified version)"""
        # This is a simplified version - in practice, you'd need actual outcomes
        # to calculate performance metrics
        
        # For now, just slightly adjust weights based on prediction consistency
        predictor_consistency = {}
        
        for predictor in self.predictors:
            predictor_name = predictor.model_name
            recent_predictions = []
            
            for record in self.performance_history[-self.adaptation_window:]:
                if predictor_name in record['individual_predictions']:
                    pred = record['individual_predictions'][predictor_name]
                    recent_predictions.append(pred.expected_return)
            
            if recent_predictions:
                # Calculate consistency (lower variance = higher consistency)
                consistency = 1.0 / (np.var(recent_predictions) + 0.001)
                predictor_consistency[predictor_name] = consistency
        
        # Adjust weights based on consistency
        if predictor_consistency:
            total_consistency = sum(predictor_consistency.values())
            for i, predictor in enumerate(self.predictors):
                if predictor.model_name in predictor_consistency:
                    consistency_weight = predictor_consistency[predictor.model_name] / total_consistency
                    # Blend with original weight
                    self.adaptive_weights[i] = 0.7 * self.weights[i] + 0.3 * consistency_weight
        
        # Normalize adaptive weights
        total_weight = sum(self.adaptive_weights)
        if total_weight > 0:
            self.adaptive_weights = [w / total_weight for w in self.adaptive_weights]
        
        logger.debug(f"Updated adaptive weights: {dict(zip([p.model_name for p in self.predictors], self.adaptive_weights))}")
    
    def get_model_info(self) -> dict:
        """Get adaptive ensemble information"""
        info = super().get_model_info()
        info.update({
            'type': 'AdaptiveEnsemblePredictor',
            'adaptation_window': self.adaptation_window,
            'performance_history_size': len(self.performance_history),
            'adaptive_weights': dict(zip([p.model_name for p in self.predictors], self.adaptive_weights))
        })
        return info