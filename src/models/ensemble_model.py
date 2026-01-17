import numpy as np
from typing import Dict, List, Any
from .xgboost_model import ReturnForecaster
from .random_forest_model import DirectionClassifier
from .lstm_model import LSTMForecaster
from .hmm_model import RegimeDetector
from .garch_model import VolatilityForecaster
from ..utils.feature_engineering import MarketData, FeatureVector, ForecastOutput, RiskMetrics

class EnsembleForecaster:
    def __init__(self, optimize_hyperparams=True):
        self.xgboost = ReturnForecaster(optimize_hyperparams=optimize_hyperparams)
        self.random_forest = DirectionClassifier(optimize_hyperparams=optimize_hyperparams)
        self.lstm = LSTMForecaster()
        self.hmm = RegimeDetector()
        self.garch = VolatilityForecaster()
    
    def predict(self, features: FeatureVector, historical_data: List[MarketData]) -> ForecastOutput:
        # 1. Get regime
        regime = self.hmm.detect({
            'volatility': features.realized_vol_20d,
            'returns': features.momentum_5d,
            'vix': features.vix_zscore
        })
        
        # 2. Direction & confidence
        direction, confidence = self.random_forest.predict(features)
        
        # 3. Expected return (XGBoost)
        base_return = self.xgboost.predict(features)
        
        # 4. Quantiles (LSTM)
        sequence = self._prepare_sequence(historical_data)
        quantiles = self.lstm.predict(sequence)
        
        # 5. Volatility forecast
        returns = [d.returns for d in historical_data if d.returns is not None]
        volatility_forecast = self.garch.forecast(returns, 5)
        
        # 6. Enhanced ensemble weighting based on regime and confidence
        regime_weights = self._get_regime_weights(regime['regime'])
        
        # Dynamic confidence-based adjustment
        confidence_adjustment = min(1.5, max(0.3, confidence * 2))  # Scale between 0.3-1.5
        
        # Weighted combination with confidence adjustment
        weighted_xgboost = regime_weights['xgboost'] * base_return * confidence_adjustment
        weighted_lstm = regime_weights['lstm'] * quantiles['p50'] * confidence_adjustment
        
        # Enhanced direction signal with adaptive threshold
        direction_threshold = 0.55  # Lowered threshold for more sensitivity
        direction_signal = 0
        if confidence > direction_threshold:
            # Scale direction signal based on confidence
            direction_strength = (confidence - direction_threshold) * 0.01  # Dynamic strength
            direction_signal = (direction_strength if direction == 1 else -direction_strength)
        
        # Apply adaptive scaling based on volatility
        volatility_factor = min(2.0, max(0.5, 1.0 + (features.realized_vol_20d - 0.2) * 2))  # Adjust for volatility
        
        final_return = (weighted_xgboost + weighted_lstm + direction_signal) * volatility_factor
        
        # 7. Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(quantiles, volatility_forecast[0])
        
        # 8. Generate explainability
        explainability = self._generate_explanations(features, regime['regime'])
        
        return ForecastOutput(
            direction='UP' if direction == 1 else 'DOWN',
            expected_return=final_return * 100,  # Convert to percentage
            confidence=confidence,
            quantiles={
                'p10': quantiles['p10'] * 100,
                'p50': quantiles['p50'] * 100,
                'p90': quantiles['p90'] * 100
            },
            regime={
                'current': regime['regime'],
                'probabilities': regime['probabilities']
            },
            risk_metrics=risk_metrics,
            explainability=explainability
        )
    
    def _prepare_sequence(self, historical_data: List[MarketData]) -> List[List[float]]:
        # Prepare sequence data for LSTM (simplified)
        sequence = []
        for d in historical_data[-30:]:  # Last 30 days
            sequence.append([
                d.close,
                d.returns or 0,
                d.realized_vol_20d or 0,
                d.momentum_5d or 0,
                d.vix_zscore or 0
            ])
        return sequence
    
    def _get_regime_weights(self, regime: str) -> Dict[str, float]:
        weights = {
            'Low Vol Bull': {'xgboost': 0.5, 'lstm': 0.3, 'direction': 0.2},
            'High Vol Bull': {'xgboost': 0.4, 'lstm': 0.4, 'direction': 0.2},
            'Bear': {'xgboost': 0.4, 'lstm': 0.3, 'direction': 0.3},
            'Crisis': {'xgboost': 0.3, 'lstm': 0.5, 'direction': 0.2},  # Higher weight to LSTM in crisis
            'Recovery': {'xgboost': 0.45, 'lstm': 0.35, 'direction': 0.2},
            'Consolidation': {'xgboost': 0.5, 'lstm': 0.3, 'direction': 0.2}
        }
        
        return weights.get(regime, weights['Consolidation'])
    
    def _calculate_risk_metrics(self, quantiles: Dict[str, float], volatility: float) -> Dict[str, float]:
        # VaR 95% (absolute value of 10th percentile)
        var95 = abs(quantiles['p10'])
        
        # CVaR 95% (expected shortfall beyond VaR)
        cvar95 = max(var95 * 1.2, abs(quantiles['p10']) * 1.3)  # More conservative estimate
        
        # Max drawdown (realistic estimate based on volatility)
        # Should be in decimal form, will be converted to percentage later
        # Use a more conservative scaling: max drawdown as function of volatility and expected return
        max_drawdown = -min(0.15, abs(volatility * 0.8) + 0.05) if volatility > 0 else -0.08  # Cap at 15%, combine volatility and base
        
        # Calculate standard deviation from quantiles
        std_estimate = (quantiles['p90'] - quantiles['p10']) / 2.56  # Standard deviation approximation
        
        # Tail risk score (probability of >2% adverse move)
        mean = quantiles['p50']
        z_score_var = (var95 - abs(mean)) / std_estimate if std_estimate != 0 else 0
        tail_risk_score = max(0, min(1, 0.5 * (1 + self._erf(z_score_var / np.sqrt(2)))))
        
        return {
            'var95': var95 * 100,
            'cvar95': cvar95 * 100,
            'max_drawdown': max_drawdown * 100,  # Already calculated as decimal, convert to percentage
            'tail_risk_score': tail_risk_score,
            'volatility_forecast': volatility
        }
    
    def _erf(self, x: float) -> float:
        # Approximation of error function
        sign = 1 if x >= 0 else -1
        x = abs(x)
        
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        t = 1 / (1 + p * x)
        y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
        
        return sign * y
    
    def _generate_explanations(self, features: FeatureVector, regime: str) -> List[str]:
        explanations = []
        
        if features.realized_vol_20d > 0.25:
            explanations.append("High volatility detected, indicating increased market uncertainty")
        elif features.realized_vol_20d < 0.15:
            explanations.append("Low volatility detected, suggesting stable market conditions")
        
        if features.momentum_5d > 0.03:
            explanations.append("Strong positive momentum observed, suggesting upward trend continuation")
        elif features.momentum_5d < -0.03:
            explanations.append("Strong negative momentum observed, suggesting downward trend continuation")
        
        if features.rsi > 70:
            explanations.append("RSI indicates overbought conditions, potential reversal downside")
        elif features.rsi < 30:
            explanations.append("RSI indicates oversold conditions, potential reversal upside")
        
        explanations.append(f"Current market regime: {regime}")
        
        return explanations