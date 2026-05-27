"""
Feature engineering utilities for EpochAI
"""

import numpy as np
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

from core.data_models import MarketData, FeatureVector
from core.exceptions import FeatureExtractionError
from config.logging_config import get_logger

logger = get_logger('features')


class FeatureEngineer:
    """Main feature engineering class for creating advanced features"""
    
    def __init__(self):
        self.feature_cache = {}
        self.cache_size = 100
    
    def create_feature_vector(self, data: List[MarketData], index: int = -1) -> FeatureVector:
        """
        Create a feature vector from market data
        
        Args:
            data: List of market data points
            index: Index of the data point to create features for (-1 for last)
            
        Returns:
            FeatureVector object
        """
        if not data:
            raise FeatureExtractionError("Data cannot be empty")
        
        if index < 0:
            index = len(data) + index
        
        if index < 0 or index >= len(data):
            raise FeatureExtractionError(f"Invalid index {index} for data length {len(data)}")
        
        current_point = data[index]
        
        # Calculate technical indicators
        sma_20 = self._calculate_sma(data, index, 20)
        sma_50 = self._calculate_sma(data, index, 50)
        rsi = self._calculate_rsi(data, index, 14)
        macd = self._calculate_macd(data, index)
        bb_position = self._calculate_bollinger_position(data, index, 20)
        
        return FeatureVector(
            realized_vol_20d=getattr(current_point, 'realized_vol_20d', 0.2),
            momentum_5d=getattr(current_point, 'momentum_5d', 0.01),
            vix_zscore=getattr(current_point, 'vix_zscore', 0.0),
            sma_20=sma_20,
            sma_50=sma_50,
            rsi=rsi,
            macd=macd,
            bb_position=bb_position
        )
    
    def _calculate_sma(self, data: List[MarketData], index: int, period: int) -> float:
        """Calculate Simple Moving Average"""
        start_idx = max(0, index - period + 1)
        prices = [d.close for d in data[start_idx:index + 1]]
        
        if not prices:
            return data[index].close if index < len(data) else 100.0
        
        return sum(prices) / len(prices)
    
    def _calculate_rsi(self, data: List[MarketData], index: int, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if index < period:
            return 50.0  # Default RSI
        
        # Get price changes
        prices = [d.close for d in data[max(0, index - period):index + 1]]
        if len(prices) < 2:
            return 50.0
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [change for change in changes if change > 0]
        losses = [-change for change in changes if change < 0]
        
        avg_gain = sum(gains) / len(gains) if gains else 0.001
        avg_loss = sum(losses) / len(losses) if losses else 0.001
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return max(0, min(100, rsi))
    
    def _calculate_macd(self, data: List[MarketData], index: int, 
                       fast_period: int = 12, slow_period: int = 26) -> float:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if index < slow_period:
            return 0.0
        
        # Calculate EMAs
        fast_ema = self._calculate_ema(data, index, fast_period)
        slow_ema = self._calculate_ema(data, index, slow_period)
        
        return fast_ema - slow_ema
    
    def _calculate_ema(self, data: List[MarketData], index: int, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if index < period - 1:
            # Use SMA for insufficient data
            return self._calculate_sma(data, index, min(index + 1, period))
        
        prices = [d.close for d in data[max(0, index - period + 1):index + 1]]
        
        if not prices:
            return data[index].close if index < len(data) else 100.0
        
        # Calculate EMA
        multiplier = 2 / (period + 1)
        ema = prices[0]  # Start with first price
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_position(self, data: List[MarketData], index: int, 
                                    period: int = 20, std_dev: float = 2.0) -> float:
        """Calculate position within Bollinger Bands (0 = lower band, 1 = upper band)"""
        if index < period - 1:
            return 0.5  # Default middle position
        
        prices = [d.close for d in data[max(0, index - period + 1):index + 1]]
        
        if len(prices) < 2:
            return 0.5
        
        sma = sum(prices) / len(prices)
        variance = sum((price - sma) ** 2 for price in prices) / len(prices)
        std = variance ** 0.5
        
        current_price = data[index].close
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        if upper_band == lower_band:
            return 0.5
        
        position = (current_price - lower_band) / (upper_band - lower_band)
        return max(0, min(1, position))
    
    def calculate_advanced_features(self, data: List[MarketData], index: int = -1) -> Dict[str, float]:
        """Calculate advanced technical features"""
        if index < 0:
            index = len(data) + index
        
        features = {}
        
        try:
            # Price-based features
            features['price_momentum_5'] = self._calculate_momentum(data, index, 5)
            features['price_momentum_10'] = self._calculate_momentum(data, index, 10)
            features['price_momentum_20'] = self._calculate_momentum(data, index, 20)
            
            # Volatility features
            features['volatility_5'] = self._calculate_volatility(data, index, 5)
            features['volatility_10'] = self._calculate_volatility(data, index, 10)
            features['volatility_20'] = self._calculate_volatility(data, index, 20)
            
            # Volume features
            features['volume_sma_10'] = self._calculate_volume_sma(data, index, 10)
            features['volume_ratio'] = self._calculate_volume_ratio(data, index)
            
            # Technical indicators
            features['williams_r'] = self._calculate_williams_r(data, index, 14)
            features['stochastic_k'] = self._calculate_stochastic_k(data, index, 14)
            features['atr'] = self._calculate_atr(data, index, 14)
            
        except Exception as e:
            logger.warning(f"Error calculating advanced features: {e}")
            # Return default values on error
            for key in ['price_momentum_5', 'price_momentum_10', 'price_momentum_20',
                       'volatility_5', 'volatility_10', 'volatility_20',
                       'volume_sma_10', 'volume_ratio', 'williams_r', 
                       'stochastic_k', 'atr']:
                features[key] = 0.0
        
        return features
    
    def _calculate_momentum(self, data: List[MarketData], index: int, period: int) -> float:
        """Calculate price momentum over period"""
        if index < period:
            return 0.0
        
        current_price = data[index].close
        past_price = data[index - period].close
        
        if past_price == 0:
            return 0.0
        
        return (current_price - past_price) / past_price
    
    def _calculate_volatility(self, data: List[MarketData], index: int, period: int) -> float:
        """Calculate price volatility over period"""
        if index < period:
            return 0.02  # Default volatility
        
        prices = [d.close for d in data[max(0, index - period + 1):index + 1]]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices)) if prices[i-1] != 0]
        
        if not returns:
            return 0.02
        
        return np.std(returns)
    
    def _calculate_volume_sma(self, data: List[MarketData], index: int, period: int) -> float:
        """Calculate volume simple moving average"""
        start_idx = max(0, index - period + 1)
        volumes = [d.volume for d in data[start_idx:index + 1]]
        
        if not volumes:
            return data[index].volume if index < len(data) else 1000000
        
        return sum(volumes) / len(volumes)
    
    def _calculate_volume_ratio(self, data: List[MarketData], index: int) -> float:
        """Calculate current volume to average volume ratio"""
        if index < 10:
            return 1.0
        
        current_volume = data[index].volume
        avg_volume = self._calculate_volume_sma(data, index, 10)
        
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
    
    def _calculate_williams_r(self, data: List[MarketData], index: int, period: int = 14) -> float:
        """Calculate Williams %R"""
        if index < period - 1:
            return -50.0  # Default middle value
        
        period_data = data[max(0, index - period + 1):index + 1]
        highest_high = max(d.high for d in period_data)
        lowest_low = min(d.low for d in period_data)
        current_close = data[index].close
        
        if highest_high == lowest_low:
            return -50.0
        
        williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        return max(-100, min(0, williams_r))
    
    def _calculate_stochastic_k(self, data: List[MarketData], index: int, period: int = 14) -> float:
        """Calculate Stochastic %K"""
        if index < period - 1:
            return 50.0  # Default middle value
        
        period_data = data[max(0, index - period + 1):index + 1]
        highest_high = max(d.high for d in period_data)
        lowest_low = min(d.low for d in period_data)
        current_close = data[index].close
        
        if highest_high == lowest_low:
            return 50.0
        
        stochastic_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        return max(0, min(100, stochastic_k))
    
    def _calculate_atr(self, data: List[MarketData], index: int, period: int = 14) -> float:
        """Calculate Average True Range"""
        if index < period:
            return 0.01  # Default ATR
        
        true_ranges = []
        for i in range(max(1, index - period + 1), index + 1):
            current = data[i]
            previous = data[i - 1]
            
            tr1 = current.high - current.low
            tr2 = abs(current.high - previous.close)
            tr3 = abs(current.low - previous.close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.01