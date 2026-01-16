#!/usr/bin/env python3
"""
Improved test of the financial forecasting model with better parameters
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_generator import generate_synthetic_data
from src.models.ensemble_model import EnsembleForecaster
from src.utils.feature_engineering import FeatureVector
import numpy as np

def improved_prediction():
    print("🚀 Starting improved model test...")
    print("=" * 50)
    
    # Generate more realistic data for testing
    print("📊 Generating synthetic market data (252 days - 1 year)...")
    sample_data = generate_synthetic_data(252)  # One year of data
    print(f"✅ Generated {len(sample_data)} days of market data")
    
    # Create ensemble forecaster WITHOUT hyperparameter optimization for speed
    print("🤖 Initializing ensemble forecaster...")
    ensemble = EnsembleForecaster(optimize_hyperparams=False)
    
    # Train with more substantial data
    print("🏋️ Training models with adequate data...")
    train_data = sample_data[-126:]  # Use 6 months for training
    
    # Train each model
    ensemble.xgboost.train(train_data)
    ensemble.random_forest.train(train_data)
    ensemble.lstm.train(train_data)
    
    # Create features from latest data
    latest_data = sample_data[-1]
    features = FeatureVector(
        realized_vol_20d=latest_data.realized_vol_20d or 0.2,
        momentum_5d=latest_data.momentum_5d or 0.01,
        vix_zscore=latest_data.vix_zscore or 0,
        sma_20=latest_data.close,
        sma_50=latest_data.close,
        rsi=min(70, max(30, getattr(latest_data, 'rsi', 50))),  # Constrain RSI to reasonable range
        macd=getattr(latest_data, 'macd', 0),
        bb_position=getattr(latest_data, 'bb_position', 0.5)
    )
    
    print("🔮 Making prediction...")
    prediction = ensemble.predict(features, sample_data[-30:])
    
    print("\n🎯 Improved Prediction Results:")
    print(f"   Direction: {prediction.direction}")
    print(f"   Expected Return: {prediction.expected_return:.3f}%")
    print(f"   Confidence: {prediction.confidence:.3f}")
    print(f"   Quantiles - P10: {prediction.quantiles['p10']:.3f}%, P50: {prediction.quantiles['p50']:.3f}%, P90: {prediction.quantiles['p90']:.3f}%")
    print(f"   Regime: {prediction.regime['current']}")
    print(f"   Risk Metrics: VAR95={prediction.risk_metrics['var95']:.3f}%, MaxDD={prediction.risk_metrics['max_drawdown']:.3f}%")
    
    # Additional analysis
    print(f"\n📋 Additional Insights:")
    print(f"   Volatility Forecast: {prediction.risk_metrics['volatility_forecast']:.4f}")
    print(f"   Tail Risk Score: {prediction.risk_metrics['tail_risk_score']:.3f}")
    print(f"   CVaR95: {prediction.risk_metrics['cvar95']:.3f}%")
    
    if prediction.explainability:
        print(f"\n💡 Model Explanations:")
        for explanation in prediction.explainability[:3]:  # Show first 3 explanations
            print(f"   - {explanation}")
    
    print("\n✅ Improved model test completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    improved_prediction()