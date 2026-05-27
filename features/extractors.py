"""
Feature extraction classes for different performance requirements
"""

import numpy as np
from typing import List
from abc import ABC, abstractmethod

from core.data_models import MarketData
from core.exceptions import FeatureExtractionError
from config.logging_config import get_logger

logger = get_logger('features')


class BaseFeatureExtractor(ABC):
    """Abstract base class for feature extractors"""
    
    @abstractmethod
    def extract_features(self, data: List[MarketData]) -> np.ndarray:
        """Extract features from market data"""
        pass
    
    def validate_data(self, data: List[MarketData]) -> None:
        """Validate input data"""
        if not data:
            raise FeatureExtractionError("Data cannot be empty")
        
        # Check for required attributes
        required_attrs = ['close', 'high', 'low', 'volume']
        for i, point in enumerate(data[:5]):  # Check first 5 points
            for attr in required_attrs:
                if not hasattr(point, attr) or getattr(point, attr) is None:
                    raise FeatureExtractionError(f"Missing {attr} at data point {i}")


class BasicFeatureExtractor(BaseFeatureExtractor):
    """Basic feature extractor with standard calculations"""
    
    def extract_features(self, data: List[MarketData]) -> np.ndarray:
        """Extract basic features from market data"""
        self.validate_data(data)
        
        if len(data) < 20:
            # Return dummy features if insufficient data
            return np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]] * max(1, len(data)))
        
        features = []
        for i, current in enumerate(data):
            try:
                # Basic features
                price_level = current.close
                volatility = getattr(current, 'volatility', getattr(current, 'realized_vol_20d', 0.2))
                momentum = getattr(current, 'momentum_5d', getattr(current, 'momentum', 0.01))
                rsi = getattr(current, 'rsi', 50) if hasattr(current, 'rsi') and current.rsi is not None else 50
                macd = getattr(current, 'macd', 0) if hasattr(current, 'macd') and current.macd is not None else 0
                
                # Advanced features
                volume_ratio = current.volume / 1000000 if current.volume > 0 else 1
                high_low_spread = (current.high - current.low) / current.close if current.close > 0 else 0.01
                price_position = (current.close - current.low) / (current.high - current.low) if (current.high - current.low) > 0 else 0.5
                
                # Trend features
                trend_strength = abs(momentum) * 100
                volatility_normalized = volatility * 100
                
                # Combine all features
                feature_row = [
                    price_level / 10000,  # Normalize price
                    volatility_normalized,
                    momentum * 100,  # Convert to percentage
                    rsi / 100,  # Normalize RSI
                    macd,
                    volume_ratio,
                    high_low_spread,
                    price_position,
                    trend_strength,
                    volatility_normalized
                ]
                
                features.append(feature_row)
                
            except Exception as e:
                logger.warning(f"Error extracting features for data point {i}: {e}")
                # Use default values if extraction fails
                features.append([1.0, 2.0, 1.0, 0.5, 0.0, 1.0, 0.01, 0.5, 1.0, 2.0])
        
        return np.array(features)


class OptimizedFeatureExtractor(BaseFeatureExtractor):
    """Optimized feature extractor using vectorized operations"""
    
    def extract_features(self, data: List[MarketData]) -> np.ndarray:
        """Extract features using vectorized operations for better performance"""
        self.validate_data(data)
        
        if len(data) == 0:
            return np.zeros((1, 10))
        
        try:
            # Convert to numpy arrays for vectorized operations
            closes = np.array([d.close for d in data])
            volumes = np.array([d.volume for d in data])
            volatilities = np.array([getattr(d, 'volatility', getattr(d, 'realized_vol_20d', 0.2)) for d in data])
            momentums = np.array([getattr(d, 'momentum_5d', getattr(d, 'momentum', 0.01)) for d in data])
            rsis = np.array([getattr(d, 'rsi', 50) for d in data])
            macds = np.array([getattr(d, 'macd', 0) for d in data])
            
            # Vectorized calculations
            normalized_prices = closes / 10000  # Normalize price level
            normalized_volatilities = volatilities * 100
            normalized_momentums = momentums * 100
            normalized_rsis = rsis / 100
            normalized_volumes = volumes / 1000000
            
            # Calculate additional features using vectorized operations
            high_lows = np.array([(d.high - d.low) / d.close if d.close > 0 else 0.01 for d in data])
            price_positions = np.array([(d.close - d.low) / (d.high - d.low) if (d.high - d.low) > 0 else 0.5 for d in data])
            
            # Stack all features
            features = np.column_stack([
                normalized_prices,
                normalized_volatilities,
                normalized_momentums,
                normalized_rsis,
                macds,
                normalized_volumes,
                high_lows,
                price_positions,
                np.abs(momentums) * 100,  # Trend strength
                normalized_volatilities  # Duplicate for consistent shape
            ])
            
            return features.astype(np.float32)  # Use float32 for memory efficiency
            
        except Exception as e:
            logger.error(f"Error in optimized feature extraction: {e}")
            # Fallback to basic extraction
            basic_extractor = BasicFeatureExtractor()
            return basic_extractor.extract_features(data)


class UltraFastFeatureExtractor(BaseFeatureExtractor):
    """Ultra-fast feature extractor with minimal memory allocation"""
    
    def extract_features(self, data: List[MarketData]) -> np.ndarray:
        """Ultra-fast feature extraction with pre-allocated arrays"""
        self.validate_data(data)
        
        if len(data) == 0:
            return np.zeros((1, 10), dtype=np.float32)
        
        try:
            # Pre-allocate arrays for efficiency
            n = len(data)
            features = np.zeros((n, 10), dtype=np.float32)
            
            # Extract data in single pass
            for i, d in enumerate(data):
                price_norm = d.close / 10000.0
                vol_norm = getattr(d, 'volatility', getattr(d, 'realized_vol_20d', 0.2)) * 100
                mom_norm = getattr(d, 'momentum_5d', getattr(d, 'momentum', 0.01)) * 100
                rsi_norm = getattr(d, 'rsi', 50) / 100.0
                macd_val = getattr(d, 'macd', 0)
                vol_norm_calc = d.volume / 1000000.0
                hl_spread = (d.high - d.low) / d.close if d.close > 0 else 0.01
                pos = (d.close - d.low) / (d.high - d.low) if (d.high - d.low) > 0 else 0.5
                trend_str = abs(getattr(d, 'momentum_5d', getattr(d, 'momentum', 0.01))) * 100
                
                features[i, :] = [
                    price_norm, vol_norm, mom_norm, rsi_norm, macd_val,
                    vol_norm_calc, hl_spread, pos, trend_str, vol_norm
                ]
            
            return features
            
        except Exception as e:
            logger.error(f"Error in ultra-fast feature extraction: {e}")
            # Return minimal features
            return np.ones((len(data), 10), dtype=np.float32) * 0.5