"""
Data validation utilities for EpochAI
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta

from core.data_models import MarketData, PredictionResult, FeatureVector
from core.exceptions import InvalidDataError
from config.logging_config import get_logger

logger = get_logger('validation')


class DataValidator:
    """Comprehensive data validation for market data and predictions"""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.validation_errors = []
    
    def validate_market_data(self, data: Union[MarketData, List[MarketData]]) -> bool:
        """
        Validate market data for correctness and consistency
        
        Args:
            data: Single MarketData object or list of MarketData objects
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            InvalidDataError: If strict_mode is True and validation fails
        """
        self.validation_errors.clear()
        
        if isinstance(data, MarketData):
            data = [data]
        
        if not data:
            self._add_error("Data cannot be empty")
            return self._handle_validation_result()
        
        for i, point in enumerate(data):
            self._validate_single_market_data(point, i)
        
        # Validate data consistency across time series
        if len(data) > 1:
            self._validate_time_series_consistency(data)
        
        return self._handle_validation_result()
    
    def _validate_single_market_data(self, data: MarketData, index: int):
        """Validate a single market data point"""
        prefix = f"Data point {index}: "
        
        # Validate required fields
        if not hasattr(data, 'timestamp') or data.timestamp is None:
            self._add_error(f"{prefix}Missing timestamp")
        
        if not hasattr(data, 'price') or data.price is None:
            self._add_error(f"{prefix}Missing price")
        elif data.price <= 0:
            self._add_error(f"{prefix}Price must be positive, got {data.price}")
        
        if not hasattr(data, 'volume') or data.volume is None:
            self._add_error(f"{prefix}Missing volume")
        elif data.volume < 0:
            self._add_error(f"{prefix}Volume cannot be negative, got {data.volume}")
        
        # Validate OHLC data
        if hasattr(data, 'high') and hasattr(data, 'low') and hasattr(data, 'close'):
            if data.high < data.low:
                self._add_error(f"{prefix}High ({data.high}) cannot be less than Low ({data.low})")
            
            if data.close > data.high:
                self._add_error(f"{prefix}Close ({data.close}) cannot be greater than High ({data.high})")
            
            if data.close < data.low:
                self._add_error(f"{prefix}Close ({data.close}) cannot be less than Low ({data.low})")
        
        # Validate technical indicators
        if hasattr(data, 'rsi') and data.rsi is not None:
            if not (0 <= data.rsi <= 100):
                self._add_error(f"{prefix}RSI must be between 0 and 100, got {data.rsi}")
        
        if hasattr(data, 'volatility') and data.volatility is not None:
            if data.volatility < 0:
                self._add_error(f"{prefix}Volatility cannot be negative, got {data.volatility}")
            elif data.volatility > 1.0:  # 100% daily volatility is extreme
                self._add_warning(f"{prefix}Extremely high volatility: {data.volatility}")
        
        # Validate returns
        if hasattr(data, 'returns') and data.returns is not None:
            if abs(data.returns) > 0.5:  # 50% daily return is extreme
                self._add_warning(f"{prefix}Extreme return: {data.returns}")
    
    def _validate_time_series_consistency(self, data: List[MarketData]):
        """Validate consistency across time series"""
        # Check timestamp ordering
        for i in range(1, len(data)):
            if data[i].timestamp <= data[i-1].timestamp:
                self._add_error(f"Timestamps not in ascending order at index {i}")
        
        # Check for reasonable price movements
        for i in range(1, len(data)):
            price_change = abs(data[i].price - data[i-1].price) / data[i-1].price
            if price_change > 0.2:  # 20% price change
                self._add_warning(f"Large price change at index {i}: {price_change:.2%}")
        
        # Check for data gaps
        if len(data) > 2:
            time_deltas = [(data[i].timestamp - data[i-1].timestamp).total_seconds() 
                          for i in range(1, len(data))]
            median_delta = np.median(time_deltas)
            
            for i, delta in enumerate(time_deltas, 1):
                if delta > median_delta * 3:  # Gap more than 3x median
                    self._add_warning(f"Large time gap at index {i}: {delta}s vs median {median_delta}s")
    
    def validate_prediction_result(self, prediction: PredictionResult) -> bool:
        """Validate prediction result"""
        self.validation_errors.clear()
        
        # Validate direction
        if prediction.direction not in ['UP', 'DOWN', 'NEUTRAL']:
            self._add_error(f"Invalid direction: {prediction.direction}")
        
        # Validate confidence
        if not (0 <= prediction.confidence <= 1):
            self._add_error(f"Confidence must be between 0 and 1, got {prediction.confidence}")
        
        # Validate expected return
        if abs(prediction.expected_return) > 50:  # 50% return is extreme
            self._add_warning(f"Extreme expected return: {prediction.expected_return}%")
        
        # Validate quantiles
        if 'p10' in prediction.quantiles and 'p90' in prediction.quantiles:
            if prediction.quantiles['p10'] > prediction.quantiles['p90']:
                self._add_error("P10 quantile cannot be greater than P90 quantile")
        
        # Validate risk metrics
        if 'var95' in prediction.risk_metrics:
            if prediction.risk_metrics['var95'] < 0:
                self._add_error("VaR95 cannot be negative")
        
        return self._handle_validation_result()
    
    def validate_feature_vector(self, features: FeatureVector) -> bool:
        """Validate feature vector"""
        self.validation_errors.clear()
        
        # Validate RSI
        if not (0 <= features.rsi <= 100):
            self._add_error(f"RSI must be between 0 and 100, got {features.rsi}")
        
        # Validate Bollinger Band position
        if not (0 <= features.bb_position <= 1):
            self._add_error(f"Bollinger Band position must be between 0 and 1, got {features.bb_position}")
        
        # Validate volatility
        if features.realized_vol_20d < 0:
            self._add_error(f"Volatility cannot be negative, got {features.realized_vol_20d}")
        
        # Check for NaN or infinite values
        feature_dict = features.to_array()
        for i, value in enumerate(feature_dict):
            if np.isnan(value):
                self._add_error(f"Feature {i} contains NaN value")
            elif np.isinf(value):
                self._add_error(f"Feature {i} contains infinite value")
        
        return self._handle_validation_result()
    
    def validate_data_range(self, values: List[float], min_val: float = None, 
                           max_val: float = None, name: str = "values") -> bool:
        """Validate that values are within specified range"""
        self.validation_errors.clear()
        
        if not values:
            self._add_error(f"{name} cannot be empty")
            return self._handle_validation_result()
        
        for i, value in enumerate(values):
            if np.isnan(value):
                self._add_error(f"{name}[{i}] is NaN")
            elif np.isinf(value):
                self._add_error(f"{name}[{i}] is infinite")
            elif min_val is not None and value < min_val:
                self._add_error(f"{name}[{i}] = {value} is below minimum {min_val}")
            elif max_val is not None and value > max_val:
                self._add_error(f"{name}[{i}] = {value} is above maximum {max_val}")
        
        return self._handle_validation_result()
    
    def validate_data_completeness(self, data: List[MarketData], 
                                  required_fields: List[str] = None) -> bool:
        """Validate data completeness"""
        self.validation_errors.clear()
        
        if not data:
            self._add_error("Data cannot be empty")
            return self._handle_validation_result()
        
        if required_fields is None:
            required_fields = ['timestamp', 'price', 'volume', 'close']
        
        for i, point in enumerate(data):
            for field in required_fields:
                if not hasattr(point, field) or getattr(point, field) is None:
                    self._add_error(f"Data point {i} missing required field: {field}")
        
        return self._handle_validation_result()
    
    def detect_outliers(self, values: List[float], method: str = 'iqr', 
                       threshold: float = 3.0) -> List[int]:
        """Detect outliers in data"""
        if len(values) < 4:
            return []
        
        values_array = np.array(values)
        outlier_indices = []
        
        if method == 'iqr':
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            outlier_indices = [
                i for i, v in enumerate(values) 
                if v < lower_bound or v > upper_bound
            ]
        
        elif method == 'zscore':
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            
            if std_val > 0:
                z_scores = np.abs((values_array - mean_val) / std_val)
                outlier_indices = [
                    i for i, z in enumerate(z_scores) 
                    if z > threshold
                ]
        
        return outlier_indices
    
    def _add_error(self, message: str):
        """Add validation error"""
        self.validation_errors.append(('ERROR', message))
        logger.error(f"Validation error: {message}")
    
    def _add_warning(self, message: str):
        """Add validation warning"""
        self.validation_errors.append(('WARNING', message))
        logger.warning(f"Validation warning: {message}")
    
    def _handle_validation_result(self) -> bool:
        """Handle validation result based on strict mode"""
        has_errors = any(level == 'ERROR' for level, _ in self.validation_errors)
        
        if has_errors and self.strict_mode:
            error_messages = [msg for level, msg in self.validation_errors if level == 'ERROR']
            raise InvalidDataError(f"Validation failed: {'; '.join(error_messages)}")
        
        return not has_errors
    
    def get_validation_errors(self) -> List[tuple]:
        """Get all validation errors and warnings"""
        return self.validation_errors.copy()
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        errors = [msg for level, msg in self.validation_errors if level == 'ERROR']
        warnings = [msg for level, msg in self.validation_errors if level == 'WARNING']
        
        return {
            'is_valid': len(errors) == 0,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'errors': errors,
            'warnings': warnings
        }


def validate_model_inputs(data: List[MarketData], min_points: int = 30) -> bool:
    """Validate inputs for model training"""
    validator = DataValidator(strict_mode=False)
    
    # Basic validation
    if not validator.validate_market_data(data):
        return False
    
    # Check minimum data points
    if len(data) < min_points:
        logger.error(f"Insufficient data for model training: {len(data)} < {min_points}")
        return False
    
    # Check data completeness
    required_fields = ['timestamp', 'price', 'volume', 'close', 'returns']
    if not validator.validate_data_completeness(data, required_fields):
        return False
    
    return True


def sanitize_data(data: List[MarketData]) -> List[MarketData]:
    """Sanitize data by fixing common issues"""
    sanitized_data = []
    
    for i, point in enumerate(data):
        # Create a copy to avoid modifying original
        sanitized_point = MarketData(
            timestamp=point.timestamp,
            price=max(0.01, point.price) if point.price > 0 else 0.01,
            volume=max(0, point.volume),
            volatility=getattr(point, 'volatility', 0.02),
            momentum=getattr(point, 'momentum', 0.0),
            rsi=max(0, min(100, getattr(point, 'rsi', 50))),
            macd=getattr(point, 'macd', 0.0),
            high=point.high if hasattr(point, 'high') else point.price,
            low=point.low if hasattr(point, 'low') else point.price,
            close=point.close,
            returns=getattr(point, 'returns', 0.0),
            realized_vol_20d=getattr(point, 'realized_vol_20d', 0.02),
            momentum_5d=getattr(point, 'momentum_5d', 0.0),
            vix_zscore=getattr(point, 'vix_zscore', 0.0)
        )
        
        # Ensure OHLC consistency
        if sanitized_point.high < sanitized_point.low:
            sanitized_point.high, sanitized_point.low = sanitized_point.low, sanitized_point.high
        
        sanitized_point.close = max(sanitized_point.low, min(sanitized_point.high, sanitized_point.close))
        
        sanitized_data.append(sanitized_point)
    
    logger.info(f"Sanitized {len(sanitized_data)} data points")
    return sanitized_data