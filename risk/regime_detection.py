"""
Market regime detection algorithms
"""

import numpy as np
from typing import List, Dict
from abc import ABC, abstractmethod

from core.data_models import MarketData
from config.logging_config import get_logger

logger = get_logger('risk.regime')


class BaseRegimeDetector(ABC):
    """Abstract base class for regime detectors"""
    
    @abstractmethod
    def detect_regime(self, current_data: MarketData, recent_data: List[MarketData]) -> str:
        """Detect current market regime"""
        pass


class BasicRegimeDetector(BaseRegimeDetector):
    """Basic market regime detector based on volatility and momentum"""
    
    def __init__(self, high_vol_threshold: float = 0.03, strong_momentum_threshold: float = 0.03):
        self.high_vol_threshold = high_vol_threshold
        self.strong_momentum_threshold = strong_momentum_threshold
    
    def detect_regime(self, current_data: MarketData, recent_data: List[MarketData]) -> str:
        """Detect current market regime based on recent volatility and momentum"""
        if not recent_data:
            return "STABLE"
        
        try:
            # Calculate recent volatility and momentum
            recent_volatility = np.mean([
                getattr(d, 'volatility', getattr(d, 'realized_vol_20d', 0.2)) 
                for d in recent_data
            ])
            recent_momentum = np.mean([
                getattr(d, 'momentum_5d', getattr(d, 'momentum', 0.01)) 
                for d in recent_data
            ])
            
            # Define regime boundaries
            if recent_volatility > self.high_vol_threshold and abs(recent_momentum) > self.strong_momentum_threshold:
                if recent_momentum > 0:
                    return "VOLATILE_BULL"
                else:
                    return "VOLATILE_BEAR"
            elif recent_volatility > self.high_vol_threshold:
                return "HIGH_VOLATILITY"
            elif recent_momentum > self.strong_momentum_threshold:
                return "BULLISH"
            elif recent_momentum < -self.strong_momentum_threshold:
                return "BEARISH"
            else:
                return "STABLE"
                
        except Exception as e:
            logger.error(f"Regime detection failed: {e}")
            return "UNKNOWN"


class OptimizedRegimeDetector(BaseRegimeDetector):
    """Optimized regime detector with fast numpy calculations"""
    
    def __init__(self, high_vol_threshold: float = 0.03, strong_momentum_threshold: float = 0.03):
        self.high_vol_threshold = high_vol_threshold
        self.strong_momentum_threshold = strong_momentum_threshold
    
    def detect_regime(self, current_data: MarketData, recent_data: List[MarketData]) -> str:
        """Fast regime detection using numpy operations"""
        if not recent_data:
            return "STABLE"
        
        try:
            # Use numpy for fast calculations
            volatilities = np.array([
                getattr(d, 'volatility', getattr(d, 'realized_vol_20d', 0.2)) 
                for d in recent_data
            ])
            momentums = np.array([
                getattr(d, 'momentum_5d', getattr(d, 'momentum', 0.01)) 
                for d in recent_data
            ])
            
            recent_volatility = np.mean(volatilities)
            recent_momentum = np.mean(momentums)
            
            # Fast regime classification
            if recent_volatility > self.high_vol_threshold and abs(recent_momentum) > self.strong_momentum_threshold:
                return "VOLATILE_BULL" if recent_momentum > 0 else "VOLATILE_BEAR"
            elif recent_volatility > self.high_vol_threshold:
                return "HIGH_VOLATILITY"
            elif recent_momentum > self.strong_momentum_threshold:
                return "BULLISH"
            elif recent_momentum < -self.strong_momentum_threshold:
                return "BEARISH"
            else:
                return "STABLE"
                
        except Exception as e:
            logger.error(f"Optimized regime detection failed: {e}")
            return "UNKNOWN"


class AdvancedRegimeDetector(BaseRegimeDetector):
    """Advanced regime detector using multiple indicators and machine learning"""
    
    def __init__(self, lookback_window: int = 20):
        self.lookback_window = lookback_window
        self.regime_history = []
    
    def detect_regime(self, current_data: MarketData, recent_data: List[MarketData]) -> str:
        """Advanced regime detection using multiple technical indicators"""
        if len(recent_data) < self.lookback_window:
            return "INSUFFICIENT_DATA"
        
        try:
            # Use recent data for analysis
            analysis_data = recent_data[-self.lookback_window:]
            
            # Calculate multiple indicators
            volatility_regime = self._detect_volatility_regime(analysis_data)
            momentum_regime = self._detect_momentum_regime(analysis_data)
            trend_regime = self._detect_trend_regime(analysis_data)
            
            # Combine regimes using voting
            regime = self._combine_regimes(volatility_regime, momentum_regime, trend_regime)
            
            # Store in history for trend analysis
            self.regime_history.append(regime)
            if len(self.regime_history) > 50:  # Keep last 50 regimes
                self.regime_history.pop(0)
            
            return regime
            
        except Exception as e:
            logger.error(f"Advanced regime detection failed: {e}")
            return "UNKNOWN"
    
    def _detect_volatility_regime(self, data: List[MarketData]) -> str:
        """Detect volatility-based regime"""
        volatilities = [getattr(d, 'volatility', getattr(d, 'realized_vol_20d', 0.2)) for d in data]
        
        current_vol = np.mean(volatilities[-5:])  # Recent 5 periods
        historical_vol = np.mean(volatilities[:-5])  # Earlier periods
        
        vol_ratio = current_vol / (historical_vol + 1e-8)
        
        if vol_ratio > 1.5:
            return "HIGH_VOLATILITY"
        elif vol_ratio < 0.7:
            return "LOW_VOLATILITY"
        else:
            return "NORMAL_VOLATILITY"
    
    def _detect_momentum_regime(self, data: List[MarketData]) -> str:
        """Detect momentum-based regime"""
        prices = [d.close for d in data]
        returns = np.diff(prices) / prices[:-1]
        
        # Calculate momentum indicators
        short_momentum = np.mean(returns[-5:])  # 5-period momentum
        long_momentum = np.mean(returns[-10:])  # 10-period momentum
        
        if short_momentum > 0.01 and long_momentum > 0.005:
            return "STRONG_BULLISH"
        elif short_momentum > 0.005:
            return "BULLISH"
        elif short_momentum < -0.01 and long_momentum < -0.005:
            return "STRONG_BEARISH"
        elif short_momentum < -0.005:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _detect_trend_regime(self, data: List[MarketData]) -> str:
        """Detect trend-based regime"""
        prices = np.array([d.close for d in data])
        
        # Simple moving averages
        sma_5 = np.mean(prices[-5:])
        sma_10 = np.mean(prices[-10:])
        sma_20 = np.mean(prices)
        
        current_price = prices[-1]
        
        # Trend classification
        if current_price > sma_5 > sma_10 > sma_20:
            return "STRONG_UPTREND"
        elif current_price > sma_5 > sma_10:
            return "UPTREND"
        elif current_price < sma_5 < sma_10 < sma_20:
            return "STRONG_DOWNTREND"
        elif current_price < sma_5 < sma_10:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def _combine_regimes(self, vol_regime: str, mom_regime: str, trend_regime: str) -> str:
        """Combine individual regime signals into overall regime"""
        # Mapping regimes to scores
        regime_scores = {
            'volatility': self._score_volatility_regime(vol_regime),
            'momentum': self._score_momentum_regime(mom_regime),
            'trend': self._score_trend_regime(trend_regime)
        }
        
        # Weighted combination
        total_score = (
            regime_scores['volatility'] * 0.3 +
            regime_scores['momentum'] * 0.4 +
            regime_scores['trend'] * 0.3
        )
        
        # Convert score to regime
        if total_score > 0.6:
            return "BULLISH_REGIME"
        elif total_score > 0.2:
            return "MILD_BULLISH"
        elif total_score < -0.6:
            return "BEARISH_REGIME"
        elif total_score < -0.2:
            return "MILD_BEARISH"
        else:
            return "NEUTRAL_REGIME"
    
    def _score_volatility_regime(self, regime: str) -> float:
        """Convert volatility regime to numerical score"""
        scores = {
            'HIGH_VOLATILITY': -0.3,  # High vol is generally negative
            'NORMAL_VOLATILITY': 0.0,
            'LOW_VOLATILITY': 0.2
        }
        return scores.get(regime, 0.0)
    
    def _score_momentum_regime(self, regime: str) -> float:
        """Convert momentum regime to numerical score"""
        scores = {
            'STRONG_BULLISH': 1.0,
            'BULLISH': 0.5,
            'NEUTRAL': 0.0,
            'BEARISH': -0.5,
            'STRONG_BEARISH': -1.0
        }
        return scores.get(regime, 0.0)
    
    def _score_trend_regime(self, regime: str) -> float:
        """Convert trend regime to numerical score"""
        scores = {
            'STRONG_UPTREND': 1.0,
            'UPTREND': 0.6,
            'SIDEWAYS': 0.0,
            'DOWNTREND': -0.6,
            'STRONG_DOWNTREND': -1.0
        }
        return scores.get(regime, 0.0)
    
    def get_regime_history(self) -> List[str]:
        """Get historical regime classifications"""
        return self.regime_history.copy()
    
    def get_regime_stability(self) -> float:
        """Calculate regime stability (lower values indicate more regime changes)"""
        if len(self.regime_history) < 10:
            return 1.0
        
        # Count regime changes in recent history
        recent_regimes = self.regime_history[-10:]
        changes = sum(1 for i in range(1, len(recent_regimes)) 
                     if recent_regimes[i] != recent_regimes[i-1])
        
        # Stability score (0 = very unstable, 1 = very stable)
        stability = 1.0 - (changes / (len(recent_regimes) - 1))
        return stability