"""
General helper functions for EpochAI
"""

import numpy as np
from typing import List, Optional
from datetime import datetime, timedelta

from core.data_models import MarketData


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency string"""
    if currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage string"""
    return f"{value:.{decimals}f}%"


def calculate_returns(prices: List[float]) -> List[float]:
    """Calculate returns from price series"""
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns


def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
    """Calculate volatility from returns"""
    if len(returns) < 2:
        return 0.0
    
    vol = np.std(returns)
    
    if annualize:
        vol *= np.sqrt(252)  # Assume 252 trading days per year
    
    return vol


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """Calculate Sharpe ratio"""
    if len(returns) < 2:
        return 0.0
    
    mean_return = np.mean(returns) * 252  # Annualized
    volatility = calculate_volatility(returns, annualize=True)
    
    if volatility == 0:
        return 0.0
    
    return (mean_return - risk_free_rate) / volatility


def calculate_max_drawdown(prices: List[float]) -> float:
    """Calculate maximum drawdown from price series"""
    if len(prices) < 2:
        return 0.0
    
    cumulative = np.cumprod([1 + r for r in calculate_returns(prices)])
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - running_max) / running_max
    
    return np.min(drawdowns)


def resample_data(data: List[MarketData], frequency: str = 'D') -> List[MarketData]:
    """
    Resample market data to different frequency
    
    Args:
        data: List of MarketData objects
        frequency: Target frequency ('D' for daily, 'H' for hourly, etc.)
    
    Returns:
        Resampled data
    """
    if not data:
        return []
    
    # Simple implementation - just return original data for now
    # In a real implementation, you would aggregate OHLCV data properly
    return data


def detect_outliers(values: List[float], method: str = 'iqr', threshold: float = 1.5) -> List[int]:
    """
    Detect outliers in a series of values
    
    Args:
        values: List of values to check
        method: Method to use ('iqr' or 'zscore')
        threshold: Threshold for outlier detection
    
    Returns:
        List of indices of outliers
    """
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


def smooth_series(values: List[float], window: int = 5, method: str = 'sma') -> List[float]:
    """
    Smooth a time series using moving average
    
    Args:
        values: List of values to smooth
        window: Window size for smoothing
        method: Smoothing method ('sma' for simple moving average)
    
    Returns:
        Smoothed values
    """
    if len(values) < window:
        return values.copy()
    
    smoothed = []
    
    if method == 'sma':
        for i in range(len(values)):
            if i < window - 1:
                # For early values, use available data
                smoothed.append(np.mean(values[:i+1]))
            else:
                # Use full window
                smoothed.append(np.mean(values[i-window+1:i+1]))
    
    return smoothed


def generate_date_range(start_date: datetime, end_date: datetime, 
                       frequency: str = 'D') -> List[datetime]:
    """
    Generate a range of dates
    
    Args:
        start_date: Start date
        end_date: End date
        frequency: Frequency ('D' for daily, 'H' for hourly)
    
    Returns:
        List of datetime objects
    """
    dates = []
    current_date = start_date
    
    if frequency == 'D':
        delta = timedelta(days=1)
    elif frequency == 'H':
        delta = timedelta(hours=1)
    elif frequency == 'M':
        delta = timedelta(minutes=1)
    else:
        delta = timedelta(days=1)  # Default to daily
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += delta
    
    return dates


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def normalize_array(arr: List[float], method: str = 'minmax') -> List[float]:
    """
    Normalize an array of values
    
    Args:
        arr: Array to normalize
        method: Normalization method ('minmax' or 'zscore')
    
    Returns:
        Normalized array
    """
    if not arr:
        return []
    
    arr_np = np.array(arr)
    
    if method == 'minmax':
        min_val = np.min(arr_np)
        max_val = np.max(arr_np)
        
        if max_val == min_val:
            return [0.5] * len(arr)  # All values are the same
        
        normalized = (arr_np - min_val) / (max_val - min_val)
    
    elif method == 'zscore':
        mean_val = np.mean(arr_np)
        std_val = np.std(arr_np)
        
        if std_val == 0:
            return [0.0] * len(arr)  # All values are the same
        
        normalized = (arr_np - mean_val) / std_val
    
    else:
        return arr.copy()
    
    return normalized.tolist()