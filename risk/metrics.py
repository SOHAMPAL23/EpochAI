"""
Risk metrics calculations for EpochAI
"""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass

from core.data_models import MarketData
from config.logging_config import get_logger

logger = get_logger('risk.metrics')


@dataclass
class RiskMetrics:
    """Risk metrics data class"""
    var95: float
    cvar95: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    skewness: float
    kurtosis: float


class RiskCalculator:
    """Calculate various risk metrics from return data"""
    
    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        return np.percentile(returns, (1 - confidence) * 100)
    
    @staticmethod
    def calculate_cvar(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if not returns:
            return 0.0
        
        var = RiskCalculator.calculate_var(returns, confidence)
        tail_returns = [r for r in returns if r <= var]
        
        return np.mean(tail_returns) if tail_returns else var
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """Calculate maximum drawdown from price series"""
        if len(prices) < 2:
            return 0.0
        
        # Calculate cumulative returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        cumulative = np.cumprod([1 + r for r in returns])
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(cumulative)
        
        # Calculate drawdowns
        drawdowns = (cumulative - running_max) / running_max
        
        return np.min(drawdowns)
    
    @staticmethod
    def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(returns) < 2:
            return 0.0
        
        vol = np.std(returns)
        
        if annualize:
            vol *= np.sqrt(252)  # Assume 252 trading days
        
        return vol
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns) * 252  # Annualized
        volatility = RiskCalculator.calculate_volatility(returns, annualize=True)
        
        if volatility == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / volatility
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (uses downside deviation instead of total volatility)"""
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns) * 252  # Annualized
        
        # Calculate downside deviation
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return float('inf') if mean_return > risk_free_rate else 0.0
        
        downside_deviation = np.std(negative_returns) * np.sqrt(252)
        
        if downside_deviation == 0:
            return float('inf') if mean_return > risk_free_rate else 0.0
        
        return (mean_return - risk_free_rate) / downside_deviation
    
    @staticmethod
    def calculate_calmar_ratio(returns: List[float], prices: List[float]) -> float:
        """Calculate Calmar ratio (annual return / max drawdown)"""
        if len(returns) < 2 or len(prices) < 2:
            return 0.0
        
        annual_return = np.mean(returns) * 252
        max_dd = abs(RiskCalculator.calculate_max_drawdown(prices))
        
        if max_dd == 0:
            return float('inf') if annual_return > 0 else 0.0
        
        return annual_return / max_dd
    
    @staticmethod
    def calculate_skewness(returns: List[float]) -> float:
        """Calculate skewness of returns"""
        if len(returns) < 3:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return np.mean(((np.array(returns) - mean_return) / std_return) ** 3)
    
    @staticmethod
    def calculate_kurtosis(returns: List[float]) -> float:
        """Calculate excess kurtosis of returns"""
        if len(returns) < 4:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return np.mean(((np.array(returns) - mean_return) / std_return) ** 4) - 3
    
    @staticmethod
    def calculate_all_metrics(returns: List[float], prices: List[float] = None, 
                            risk_free_rate: float = 0.02) -> RiskMetrics:
        """Calculate all risk metrics"""
        if prices is None:
            # Generate prices from returns if not provided
            prices = [100]  # Start with base price
            for ret in returns:
                prices.append(prices[-1] * (1 + ret))
        
        return RiskMetrics(
            var95=abs(RiskCalculator.calculate_var(returns, 0.95)),
            cvar95=abs(RiskCalculator.calculate_cvar(returns, 0.95)),
            max_drawdown=RiskCalculator.calculate_max_drawdown(prices),
            volatility=RiskCalculator.calculate_volatility(returns, annualize=True),
            sharpe_ratio=RiskCalculator.calculate_sharpe_ratio(returns, risk_free_rate),
            sortino_ratio=RiskCalculator.calculate_sortino_ratio(returns, risk_free_rate),
            calmar_ratio=RiskCalculator.calculate_calmar_ratio(returns, prices),
            skewness=RiskCalculator.calculate_skewness(returns),
            kurtosis=RiskCalculator.calculate_kurtosis(returns)
        )