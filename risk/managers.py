"""
Risk management classes for portfolio and prediction risk assessment
"""

import numpy as np
from typing import List, Dict
from abc import ABC, abstractmethod

from core.data_models import MarketData
from config.logging_config import get_logger

logger = get_logger('risk')


class BaseRiskManager(ABC):
    """Abstract base class for risk managers"""
    
    @abstractmethod
    def calculate_metrics(self, predicted_return: float, historical_data: List[MarketData]) -> Dict[str, float]:
        """Calculate risk metrics"""
        pass


class BasicRiskManager(BaseRiskManager):
    """Basic risk manager with standard risk calculations"""
    
    def __init__(self, var_confidence: float = 0.95):
        self.var_confidence = var_confidence
    
    def calculate_metrics(self, predicted_return: float, historical_data: List[MarketData]) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        if len(historical_data) < 20:
            logger.warning("Insufficient data for risk calculation, using defaults")
            return {'var95': 1.5, 'max_drawdown': -10.0}
        
        try:
            # Calculate historical volatility
            returns = [getattr(d, 'returns', 0) for d in historical_data if hasattr(d, 'returns')]
            if len(returns) < 10:
                returns = [0.01] * 10  # Default if no returns available
            
            hist_vol = np.std(returns) * np.sqrt(252)  # Annualized volatility
            
            # Value at Risk (VaR) - 95% confidence
            var95 = np.percentile(np.abs(returns), 95) * 100 * np.sqrt(10)  # 10-day VaR
            var95 = max(0.5, min(10.0, var95))  # Clamp reasonable values
            
            # Max Drawdown estimate (conservative)
            max_dd = -abs(var95 * 2.5)  # Conservative estimate
            
            # Additional risk metrics
            downside_deviation = self._calculate_downside_deviation(returns)
            sharpe_estimate = (np.mean(returns) * 252) / (hist_vol + 1e-8)  # Avoid division by zero
            
            return {
                'var95': round(var95, 3),
                'max_drawdown': round(max_dd, 3),
                'volatility': round(hist_vol * 100, 3),
                'downside_deviation': round(downside_deviation * 100, 3),
                'sharpe_estimate': round(sharpe_estimate, 3)
            }
            
        except Exception as e:
            logger.error(f"Risk calculation failed: {e}")
            return {'var95': 1.5, 'max_drawdown': -10.0}
    
    def _calculate_downside_deviation(self, returns: List[float]) -> float:
        """Calculate downside deviation (volatility of negative returns)"""
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return 0.0
        return np.std(negative_returns)
    
    def calculate_position_size(self, predicted_return: float, confidence: float, 
                              risk_metrics: Dict[str, float], max_risk: float = 0.02) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            predicted_return: Expected return
            confidence: Prediction confidence
            risk_metrics: Risk metrics dictionary
            max_risk: Maximum risk per trade (default 2%)
            
        Returns:
            Position size as fraction of portfolio
        """
        try:
            # Kelly Criterion: f = (bp - q) / b
            # where b = odds, p = probability of win, q = probability of loss
            
            win_prob = (confidence + 1) / 2  # Convert confidence to probability
            loss_prob = 1 - win_prob
            
            # Use VaR as potential loss estimate
            potential_loss = risk_metrics.get('var95', 2.0) / 100
            
            if potential_loss <= 0:
                return 0.0
            
            # Kelly fraction
            kelly_fraction = (predicted_return * win_prob - loss_prob) / potential_loss
            
            # Apply constraints
            kelly_fraction = max(0, min(kelly_fraction, max_risk))
            
            # Scale by confidence
            position_size = kelly_fraction * confidence
            
            return round(position_size, 4)
            
        except Exception as e:
            logger.error(f"Position size calculation failed: {e}")
            return 0.01  # Conservative default


class OptimizedRiskManager(BaseRiskManager):
    """Optimized risk manager with fast calculations"""
    
    def __init__(self, var_confidence: float = 0.95):
        self.var_confidence = var_confidence
    
    def calculate_metrics(self, predicted_return: float, historical_data: List[MarketData]) -> Dict[str, float]:
        """Fast risk metric calculation using numpy operations"""
        if len(historical_data) < 10:
            return {'var95': 1.5, 'max_drawdown': -10.0}
        
        try:
            # Use numpy for fast historical calculations
            returns = np.array([getattr(d, 'returns', 0) for d in historical_data if hasattr(d, 'returns')])
            if len(returns) < 10:
                returns = np.full(10, 0.01)  # Default if no returns available
            
            # Fast volatility calculation
            hist_vol = np.std(returns) * np.sqrt(252)
            
            # Fast VaR calculation
            var95 = np.percentile(np.abs(returns), 95) * 100 * np.sqrt(10)
            var95 = max(0.5, min(10.0, var95))
            
            # Fast max drawdown estimate
            max_dd = -abs(var95 * 2.5)
            
            return {
                'var95': round(var95, 3),
                'max_drawdown': round(max_dd, 3),
                'volatility': round(hist_vol * 100, 3)
            }
            
        except Exception as e:
            logger.error(f"Optimized risk calculation failed: {e}")
            return {'var95': 1.5, 'max_drawdown': -10.0}


class AdvancedRiskManager(BaseRiskManager):
    """Advanced risk manager with comprehensive risk models"""
    
    def __init__(self, var_confidence: float = 0.95, lookback_window: int = 252):
        self.var_confidence = var_confidence
        self.lookback_window = lookback_window
    
    def calculate_metrics(self, predicted_return: float, historical_data: List[MarketData]) -> Dict[str, float]:
        """Calculate advanced risk metrics including tail risk and correlation"""
        if len(historical_data) < 30:
            logger.warning("Insufficient data for advanced risk calculation")
            return {'var95': 1.5, 'max_drawdown': -10.0}
        
        try:
            returns = np.array([getattr(d, 'returns', 0) for d in historical_data[-self.lookback_window:]])
            
            # Basic metrics
            mean_return = np.mean(returns)
            volatility = np.std(returns)
            
            # VaR and CVaR
            var95 = np.percentile(returns, (1 - self.var_confidence) * 100)
            cvar95 = np.mean(returns[returns <= var95])  # Conditional VaR
            
            # Maximum Drawdown calculation
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdowns)
            
            # Tail risk metrics
            skewness = self._calculate_skewness(returns)
            kurtosis = self._calculate_kurtosis(returns)
            
            # Sharpe ratio
            sharpe_ratio = (mean_return * 252) / (volatility * np.sqrt(252)) if volatility > 0 else 0
            
            return {
                'var95': round(abs(var95) * 100, 3),
                'cvar95': round(abs(cvar95) * 100, 3),
                'max_drawdown': round(max_drawdown * 100, 3),
                'volatility': round(volatility * np.sqrt(252) * 100, 3),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'skewness': round(skewness, 3),
                'kurtosis': round(kurtosis, 3)
            }
            
        except Exception as e:
            logger.error(f"Advanced risk calculation failed: {e}")
            return {'var95': 1.5, 'max_drawdown': -10.0}
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calculate skewness of returns"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0.0
        return np.mean(((returns - mean_return) / std_return) ** 3)
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calculate kurtosis of returns"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0.0
        return np.mean(((returns - mean_return) / std_return) ** 4) - 3  # Excess kurtosis