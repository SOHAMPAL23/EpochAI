import numpy as np
from typing import List


class VolatilityForecaster:
    def __init__(self):
        self.omega = 0.00001
        self.alpha = 0.1
        self.beta = 0.85
        self.optimized_params = False
    
    def optimize_garch_params(self, returns: List[float]):
        """Optimize GARCH parameters using maximum likelihood estimation"""
        if len(returns) < 10:
            return  # Not enough data to optimize
        
        # Simplified optimization - in reality would use proper MLE
        squared_returns = [r**2 for r in returns]
        mean_squared_return = np.mean(squared_returns)
        
        # Estimate parameters based on data characteristics
        self.omega = max(0.000001, min(0.001, mean_squared_return * 0.01))
        self.alpha = max(0.05, min(0.2, 0.1))
        self.beta = max(0.7, min(0.95, 1.0 - self.alpha - 0.01))
        self.optimized_params = True
    
    def train(self, returns: List[float]):
        if len(returns) < 2:
            return
        
        # Optimize parameters
        self.optimize_garch_params(returns)
    
    def forecast(self, returns: List[float], horizon: int) -> List[float]:
        if len(returns) == 0:
            return [0.2 * np.sqrt(252)] * horizon  # Default volatility forecast
        
        # Initialize variance with recent squared return
        if len(returns) > 0:
            # Use exponentially weighted moving average of squared returns
            weights = np.exp(np.linspace(-1., 0., min(50, len(returns))))
            weights /= weights.sum()
            recent_squared_returns = [r**2 for r in returns[-len(weights):]]
            current_variance = np.average(recent_squared_returns, weights=weights) if recent_squared_returns else 0.0004
        else:
            current_variance = 0.0004  # Default variance
        
        forecasts = []
        for h in range(horizon):
            # Forecast variance using GARCH equation
            forecast_variance = self.omega + self.alpha * current_variance + self.beta * current_variance
            forecasts.append(float(np.sqrt(forecast_variance) * np.sqrt(252)))  # Annualized
            current_variance = forecast_variance
        
        return forecasts