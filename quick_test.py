#!/usr/bin/env python3
"""
Quick test of the financial forecasting model
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_generator import generate_synthetic_data
from src.models.ensemble_model import EnsembleForecaster
from src.utils.feature_engineering import FeatureVector

def quick_prediction():
    print("🚀 Starting quick model test...")
    print("=" * 50)
    
    # Generate minimal data for testing
    print("📊 Generating minimal synthetic market data (100 days)...")
    sample_data = generate_synthetic_data(100)  # Small amount of data
    print(f"✅ Generated {len(sample_data)} days of market data")
    
    # Create ensemble forecaster WITHOUT hyperparameter optimization
    print("🤖 Initializing ensemble forecaster (fast mode)...")
    ensemble = EnsembleForecaster(optimize_hyperparams=False)
    
    # Train with minimal data
    print("🏋️ Training models with minimal data...")
    train_data = sample_data[-50:]  # Small training set but enough for models
    
    # Train each model individually with fast settings
    ensemble.xgboost.train(train_data)
    ensemble.random_forest.train(train_data)
    ensemble.lstm.train(train_data)
    
    # Create simple features for prediction
    latest_data = sample_data[-1]
    features = FeatureVector(
        realized_vol_20d=latest_data.realized_vol_20d or 0.2,
        momentum_5d=latest_data.momentum_5d or 0.01,
        vix_zscore=latest_data.vix_zscore or 0,
        sma_20=latest_data.close,
        sma_50=latest_data.close,
        rsi=50,  # Default RSI
        macd=0,  # Default MACD
        bb_position=0.5  # Default Bollinger Band position
    )
    
    print("🔮 Making prediction...")
    prediction = ensemble.predict(features, sample_data[-10:])
    
    print("\n🎯 Quick Prediction Results:")
    print(f"   Direction: {prediction.direction}")
    print(f"   Expected Return: {prediction.expected_return:.3f}%")
    print(f"   Confidence: {prediction.confidence:.3f}")
    print(f"   Quantiles - P10: {prediction.quantiles['p10']:.3f}%, P50: {prediction.quantiles['p50']:.3f}%, P90: {prediction.quantiles['p90']:.3f}%")
    print(f"   Regime: {prediction.regime['current']}")
    print(f"   Risk Metrics: VAR95={prediction.risk_metrics['var95']:.3f}%, MaxDD={prediction.risk_metrics['max_drawdown']:.3f}%")
    
    print("\n✅ Quick model test completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    quick_prediction()