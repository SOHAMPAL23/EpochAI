#!/usr/bin/env python3
"""
ModelQ - Multi-Modal Financial Forecasting Engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_generator import generate_synthetic_data
from src.models.ensemble_model import EnsembleForecaster
from src.core.backtesting import Backtester

def run_example():
    print("🚀 Starting ModelQ - Multi-Modal Financial Forecasting Engine...")
    print("=" * 70)
    
    # Generate synthetic market data (3 years of data)
    print("📊 Generating synthetic market data (756 days)...")
    sample_data = generate_synthetic_data(756)  # 3 years of data
    print(f"✅ Generated {len(sample_data)} days of market data")
    
    # Create ensemble forecaster with hyperparameter optimization disabled for faster execution
    print("🤖 Initializing ensemble forecaster (optimization disabled for faster execution)...")
    ensemble = EnsembleForecaster(optimize_hyperparams=False)
    
    # Train models
    print("🏋️ Training models (using default parameters for faster execution)...")
    train_data = sample_data[-252:]  # Use 1 year of data for training
    ensemble.xgboost.train(train_data)
    ensemble.random_forest.train(train_data)
    ensemble.lstm.train(train_data)
    
    # Get latest features
    print("📈 Extracting latest features...")
    latest_features = ensemble._prepare_sequence(sample_data)[-1] if sample_data else None
    
    # Create a simple feature vector for prediction
    latest_data = sample_data[-1]
    features = ensemble._prepare_sequence(sample_data)[-1] if len(ensemble._prepare_sequence(sample_data)) > 0 else [
        latest_data.close,
        latest_data.returns,
        latest_data.realized_vol_20d,
        latest_data.momentum_5d,
        latest_data.vix_zscore
    ]
    
    # Create a simple feature vector
    from src.utils.feature_engineering import FeatureVector
    feature_vector = FeatureVector(
        realized_vol_20d=latest_data.realized_vol_20d or 0.2,
        momentum_5d=latest_data.momentum_5d or 0.01,
        vix_zscore=latest_data.vix_zscore or 0,
        sma_20=latest_data.close,  # Placeholder
        sma_50=latest_data.close,  # Placeholder
        rsi=50,  # Placeholder
        macd=0,  # Placeholder
        bb_position=0.5  # Placeholder
    )
    
    print("🔮 Making prediction...")
    prediction = ensemble.predict(feature_vector, sample_data[-50:])
    
    print("\n🎯 Prediction Results:")
    print(f"   Direction: {prediction.direction}")
    print(f"   Expected Return: {prediction.expected_return:.3f}%")
    print(f"   Confidence: {prediction.confidence:.3f}")
    print(f"   Quantiles - P10: {prediction.quantiles['p10']:.3f}%, P50: {prediction.quantiles['p50']:.3f}%, P90: {prediction.quantiles['p90']:.3f}%")
    print(f"   Regime: {prediction.regime['current']}")
    print(f"   Risk Metrics: VAR95={prediction.risk_metrics['var95']:.3f}%, MaxDD={prediction.risk_metrics['max_drawdown']:.3f}%")
    
    print("\n🧪 Running backtest (with default parameters for faster execution)...")
    backtester = Backtester(optimize_hyperparams=False)
    backtest_results = backtester.run_walk_forward(sample_data, 200, 20)
    
    print("\n📊 Backtest Results:")
    print(f"   Total Return: {backtest_results.total_return:.2f}%")
    print(f"   Annualized Return: {backtest_results.annualized_return:.2f}%")
    print(f"   Sharpe Ratio: {backtest_results.sharpe_ratio:.3f}")
    print(f"   Max Drawdown: {backtest_results.max_drawdown:.2f}%")
    print(f"   Hit Rate: {backtest_results.hit_rate:.3f}")
    print(f"   Win Rate: {backtest_results.win_rate:.3f}")
    print(f"   Information Coefficient: {backtest_results.information_coefficient:.3f}")
    print(f"   Volatility: {backtest_results.volatility:.2f}%")
    print(f"   Profit Factor: {backtest_results.profit_factor:.3f}")
    
    print("\n✅ Model execution completed successfully!")
    print("=" * 70)
    print("💡 Note: This system is designed for demonstration using synthetic data.")
    print("   Do not use for real trading without proper validation and risk management.")

def run_simple_test():
    """Run a simple test to verify the model works"""
    print("🔧 Running simple model test...")
    
    try:
        # Generate minimal data
        sample_data = generate_synthetic_data(100)  # Minimal data for testing
        
        # Create ensemble
        ensemble = EnsembleForecaster(optimize_hyperparams=False)  # Disable optimization for speed
        
        # Train with minimal data
        train_data = sample_data[-50:]
        ensemble.xgboost.train(train_data)
        ensemble.random_forest.train(train_data)
        ensemble.lstm.train(train_data)
        
        # Create simple features
        from src.utils.feature_engineering import FeatureVector
        features = FeatureVector(
            realized_vol_20d=0.2,
            momentum_5d=0.01,
            vix_zscore=0,
            sma_20=10000,
            sma_50=10000,
            rsi=50,
            macd=0,
            bb_position=0.5
        )
        
        # Make prediction
        prediction = ensemble.predict(features, sample_data[-20:])
        
        print("✅ Simple test passed!")
        print(f"   Prediction direction: {prediction.direction}")
        print(f"   Expected return: {prediction.expected_return:.3f}%")
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("ModelQ - Multi-Modal Financial Forecasting Engine")
    print("Initializing and running model...\n")
    
    # Run simple test first
    if run_simple_test():
        print()
        # Run full example
        run_example()
    else:
        print("\n❌ Model initialization failed. Please check dependencies.")
        exit(1)