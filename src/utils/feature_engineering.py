from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

@dataclass
class MarketData:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    returns: float = 0.0
    realized_vol_20d: float = 0.0
    momentum_5d: float = 0.0
    vix_zscore: float = 0.0

@dataclass
class FeatureVector:
    realized_vol_20d: float
    momentum_5d: float
    vix_zscore: float
    sma_20: float
    sma_50: float
    rsi: float
    macd: float
    bb_position: float

@dataclass
class ForecastOutput:
    direction: str
    expected_return: float
    confidence: float
    quantiles: Dict[str, float]
    regime: Dict[str, Any]
    risk_metrics: Dict[str, float]
    explainability: List[str]

@dataclass
class RiskMetrics:
    var95: float
    cvar95: float
    max_drawdown: float
    tail_risk_score: float
    volatility_forecast: float

@dataclass
class BacktestResults:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    hit_rate: float
    information_coefficient: float
    volatility: float
    trades: int
    win_rate: float
    profit_factor: float