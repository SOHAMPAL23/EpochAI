"""
Core data models for EpochAI financial forecasting system
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class MarketData:
    """Market data point containing price, volume, and technical indicators"""
    timestamp: datetime
    price: float
    volume: float
    volatility: float
    momentum: float
    rsi: float
    macd: float
    high: float
    low: float
    close: float
    returns: float
    realized_vol_20d: float
    momentum_5d: float
    vix_zscore: float
    
    def __post_init__(self):
        """Validate data after initialization"""
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")
        if not (0 <= self.rsi <= 100):
            raise ValueError("RSI must be between 0 and 100")


@dataclass
class PredictionResult:
    """Result of a market prediction containing direction, confidence, and risk metrics"""
    direction: str  # 'UP', 'DOWN', or 'NEUTRAL'
    expected_return: float  # Expected return as percentage
    confidence: float  # Confidence score between 0 and 1
    quantiles: Dict[str, float]  # Prediction quantiles (p10, p50, p90)
    regime: str  # Market regime classification
    risk_metrics: Dict[str, float]  # Risk metrics (var95, max_drawdown, etc.)
    
    def __post_init__(self):
        """Validate prediction result after initialization"""
        if self.direction not in ['UP', 'DOWN', 'NEUTRAL']:
            raise ValueError("Direction must be 'UP', 'DOWN', or 'NEUTRAL'")
        if not (0 <= self.confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")
        
        # Validate quantiles
        required_quantiles = {'p10', 'p50', 'p90'}
        if not required_quantiles.issubset(self.quantiles.keys()):
            raise ValueError(f"Quantiles must contain {required_quantiles}")
        
        # Validate risk metrics
        required_risk_metrics = {'var95', 'max_drawdown'}
        if not required_risk_metrics.issubset(self.risk_metrics.keys()):
            raise ValueError(f"Risk metrics must contain {required_risk_metrics}")


@dataclass
class FeatureVector:
    """Feature vector for model input"""
    realized_vol_20d: float
    momentum_5d: float
    vix_zscore: float
    sma_20: float
    sma_50: float
    rsi: float
    macd: float
    bb_position: float
    
    def to_array(self) -> list:
        """Convert to array format for model input"""
        return [
            self.realized_vol_20d,
            self.momentum_5d,
            self.vix_zscore,
            self.sma_20,
            self.sma_50,
            self.rsi,
            self.macd,
            self.bb_position
        ]


@dataclass
class BacktestResult:
    """Results from backtesting a trading strategy"""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    hit_rate: float
    win_rate: float
    information_coefficient: float
    volatility: float
    profit_factor: float
    num_trades: int
    avg_trade_return: float