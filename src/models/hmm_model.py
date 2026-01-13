import numpy as np
from typing import Dict, Any
from ..utils.feature_engineering import MarketData

class RegimeDetector:
    def __init__(self):
        self.regimes = ['Low Vol Bull', 'High Vol Bull', 'Consolidation', 'Bear', 'Crisis', 'Recovery']
        self.emission_params = {
            'Low Vol Bull': {
                'volatility': {'mean': 0.15, 'std': 0.02},
                'returns': {'mean': 0.001, 'std': 0.01},
                'vix': {'mean': 15, 'std': 3}
            },
            'High Vol Bull': {
                'volatility': {'mean': 0.25, 'std': 0.05},
                'returns': {'mean': 0.0005, 'std': 0.015},
                'vix': {'mean': 20, 'std': 4}
            },
            'Consolidation': {
                'volatility': {'mean': 0.18, 'std': 0.03},
                'returns': {'mean': 0.0002, 'std': 0.008},
                'vix': {'mean': 18, 'std': 2}
            },
            'Bear': {
                'volatility': {'mean': 0.30, 'std': 0.08},
                'returns': {'mean': -0.001, 'std': 0.02},
                'vix': {'mean': 25, 'std': 5}
            },
            'Crisis': {
                'volatility': {'mean': 0.50, 'std': 0.15},
                'returns': {'mean': -0.005, 'std': 0.03},
                'vix': {'mean': 35, 'std': 10}
            },
            'Recovery': {
                'volatility': {'mean': 0.25, 'std': 0.06},
                'returns': {'mean': 0.002, 'std': 0.018},
                'vix': {'mean': 20, 'std': 6}
            }
        }
        
        # Transition matrix (simplified - in reality this would be learned)
        self.transition_matrix = np.array([
            [0.85, 0.05, 0.05, 0.03, 0.01, 0.01],  # Low Vol Bull
            [0.05, 0.80, 0.05, 0.05, 0.03, 0.02],  # High Vol Bull
            [0.05, 0.05, 0.80, 0.05, 0.03, 0.02],  # Consolidation
            [0.03, 0.05, 0.05, 0.80, 0.05, 0.02],  # Bear
            [0.01, 0.02, 0.02, 0.05, 0.85, 0.05],  # Crisis
            [0.02, 0.03, 0.03, 0.05, 0.02, 0.85]   # Recovery
        ])
    
    def detect(self, observation: Dict[str, float]) -> Dict[str, Any]:
        # Calculate emission probabilities for each regime
        probabilities = []
        
        for regime in self.regimes:
            prob = self._calculate_emission_prob(observation, regime)
            probabilities.append({'regime': regime, 'prob': prob})
        
        # Normalize probabilities
        total = sum(p['prob'] for p in probabilities)
        if total == 0:
            total = 1  # Avoid division by zero
        
        normalized = [{'regime': p['regime'], 'prob': p['prob'] / total} for p in probabilities]
        
        # Find most likely regime
        most_likely = max(normalized, key=lambda x: x['prob'])
        
        return {
            'regime': most_likely['regime'],
            'probabilities': {p['regime']: p['prob'] for p in normalized}
        }
    
    def _calculate_emission_prob(self, obs: Dict[str, float], regime: str) -> float:
        params = self.emission_params[regime]
        
        # Calculate multivariate Gaussian probability
        vol_prob = self._gaussian_pdf(obs['volatility'], params['volatility']['mean'], params['volatility']['std'])
        ret_prob = self._gaussian_pdf(obs['returns'], params['returns']['mean'], params['returns']['std'])
        vix_prob = self._gaussian_pdf(obs['vix'], params['vix']['mean'], params['vix']['std'])
        
        return vol_prob * ret_prob * vix_prob
    
    def _gaussian_pdf(self, x: float, mean: float, std: float) -> float:
        coefficient = 1 / (std * np.sqrt(2 * np.pi))
        exponent = -np.power(x - mean, 2) / (2 * np.power(std, 2))
        return float(coefficient * np.exp(exponent))