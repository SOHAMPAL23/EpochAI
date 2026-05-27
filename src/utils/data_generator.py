import numpy as np
import pandas as pd
from typing import List
from .feature_engineering import MarketData

def generate_synthetic_data(days: int) -> List[MarketData]:
    """Generate realistic synthetic market data"""
    data = []
    current_price = 10000  # Starting price for NIFTY-like index
    
    # Define market regimes with different characteristics
    regimes = [
        {'name': 'Low Vol Bull', 'mu': 0.0008, 'sigma': 0.008, 'prob': 0.35},  # 35% of time
        {'name': 'High Vol Bull', 'mu': 0.0005, 'sigma': 0.015, 'prob': 0.20},  # 20% of time
        {'name': 'Consolidation', 'mu': 0.0002, 'sigma': 0.007, 'prob': 0.20},  # 20% of time
        {'name': 'Bear', 'mu': -0.0006, 'sigma': 0.018, 'prob': 0.15},         # 15% of time
        {'name': 'Crisis', 'mu': -0.0015, 'sigma': 0.035, 'prob': 0.05},       # 5% of time
        {'name': 'Recovery', 'mu': 0.0012, 'sigma': 0.022, 'prob': 0.05}        # 5% of time
    ]
    
    current_regime = regimes[0]  # Start in Low Vol Bull
    
    for i in range(days):
        # Determine if regime should change based on transition probabilities
        rand = np.random.random()
        cumulative_prob = 0
        for regime in regimes:
            cumulative_prob += regime['prob']
            if rand < cumulative_prob:
                current_regime = regime
                break

        # Generate return with regime characteristics
        # Adding some autocorrelation (AR(1) = 0.05)
        prev_return = data[i-1].returns if i > 0 and hasattr(data[i-1], 'returns') and data[i-1].returns is not None else 0
        auto_correlation = 0.05 * prev_return
        
        # Generate base return with regime characteristics
        base_return = current_regime['mu'] + current_regime['sigma'] * np.random.normal()
        
        # Add autocorrelation and some fat-tail effect
        daily_return = base_return + auto_correlation
        
        # Add occasional jumps for more realistic fat tails
        if np.random.random() < 0.02:  # 2% chance of jump
            daily_return += (np.random.random() - 0.5) * 0.05  # Large move

        # Update price
        current_price = current_price * (1 + daily_return)
        
        # Generate OHLCV with some randomness
        open_price = data[i-1].close if i > 0 else current_price
        high = open_price * (1 + abs(daily_return) * (0.7 + np.random.random() * 0.3))
        low = open_price * (1 - abs(daily_return) * (0.7 + np.random.random() * 0.3))
        close = current_price
        volume = int(100000000 + np.random.random() * 200000000)  # Volume in crores

        data.append(MarketData(
            date=(pd.Timestamp.now() - pd.Timedelta(days=days-i)).strftime('%Y-%m-%d'),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            returns=daily_return
        ))
    
    # Calculate rolling statistics after generating all data
    for i in range(len(data)):
        # Calculate realized volatility (20-day)
        if i >= 19:
            returns = [d.returns for d in data[i-19:i+1] if d.returns is not None]
            if len(returns) > 0:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                data[i].realized_vol_20d = np.sqrt(variance) * np.sqrt(252)  # Annualized
        else:
            data[i].realized_vol_20d = 0.18  # Default value

        # Calculate momentum (5-day)
        if i >= 4:
            start_price = data[i-4].close
            end_price = data[i].close
            data[i].momentum_5d = (end_price - start_price) / start_price
        else:
            data[i].momentum_5d = 0.001  # Default value

        # Calculate VIX-like measure (just as a proxy)
        if i >= 19:
            data[i].vix_zscore = (data[i].realized_vol_20d - 0.18) / 0.05  # Normalize to z-score
        else:
            data[i].vix_zscore = 0.0  # Default value

    return data