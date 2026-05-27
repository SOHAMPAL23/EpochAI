#!/usr/bin/env python3
"""
Script to run cost prediction with EpochAI
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from predictors.cost_predictor import AdvancedCostPredictor
from predictors.optimized_predictor import OptimizedCostPredictor
from predictors.ultimate_predictor import UltimateCostPredictor
from data.generators import generate_synthetic_data
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('scripts')


def main():
    """Main function to run cost prediction"""
    parser = argparse.ArgumentParser(description='Run EpochAI Cost Prediction')
    parser.add_argument('--predictor', choices=['basic', 'optimized', 'ultimate'], 
                       default='basic', help='Predictor type to use')
    parser.add_argument('--data-points', type=int, default=252, 
                       help='Number of synthetic data points to generate')
    parser.add_argument('--predictions', type=int, default=5, 
                       help='Number of predictions to make')
    parser.add_argument('--benchmark', action='store_true', 
                       help='Run performance benchmark')
    
    args = parser.parse_args()
    
    print("🚀 EpochAI Cost Prediction Engine")
    print("=" * 50)
    
    # Select predictor
    if args.predictor == 'basic':
        predictor = AdvancedCostPredictor()
        print("📊 Using Advanced Cost Predictor")
    elif args.predictor == 'optimized':
        predictor = OptimizedCostPredictor()
        print("⚡ Using Optimized Cost Predictor")
    elif args.predictor == 'ultimate':
        predictor = UltimateCostPredictor()
        print("🚀 Using Ultimate Cost Predictor")
    
    # Generate synthetic data
    print(f"📈 Generating {args.data_points} synthetic data points...")
    historical_data = generate_synthetic_data(args.data_points)
    print(f"✅ Generated {len(historical_data)} data points")
    
    # Train model
    print("🤖 Training prediction model...")
    start_time = datetime.now()
    
    try:
        predictor.train(historical_data)
        training_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Model trained in {training_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return 1
    
    # Make predictions
    print(f"\n🎯 Making {args.predictions} predictions:")
    print("-" * 50)
    
    for i in range(args.predictions):
        try:
            # Use different data points for prediction
            current_data = historical_data[-(i+1)]
            prediction = predictor.predict(current_data, historical_data)
            
            print(f"\nPrediction {i+1}:")
            print(f"   Direction: {prediction.direction}")
            print(f"   Expected Return: {prediction.expected_return:.3f}%")
            print(f"   Confidence: {prediction.confidence:.3f}")
            print(f"   Regime: {prediction.regime}")
            print(f"   Quantiles - P10: {prediction.quantiles['p10']:.3f}%, "
                  f"P50: {prediction.quantiles['p50']:.3f}%, "
                  f"P90: {prediction.quantiles['p90']:.3f}%")
            print(f"   Risk - VaR95: {prediction.risk_metrics['var95']:.3f}%, "
                  f"MaxDD: {prediction.risk_metrics['max_drawdown']:.3f}%")
            
        except Exception as e:
            print(f"❌ Prediction {i+1} failed: {e}")
    
    # Run benchmark if requested
    if args.benchmark:
        print(f"\n⚡ Running Performance Benchmark:")
        print("-" * 50)
        
        # Benchmark prediction speed
        start_time = datetime.now()
        benchmark_predictions = 100
        
        for i in range(benchmark_predictions):
            current_data = historical_data[-(i % len(historical_data) + 1)]
            predictor.predict(current_data, historical_data)
        
        benchmark_time = (datetime.now() - start_time).total_seconds()
        avg_prediction_time = (benchmark_time / benchmark_predictions) * 1000
        
        print(f"   Predictions: {benchmark_predictions}")
        print(f"   Total Time: {benchmark_time:.2f} seconds")
        print(f"   Avg Time: {avg_prediction_time:.2f} ms per prediction")
        print(f"   Throughput: {benchmark_predictions / benchmark_time:.1f} predictions/sec")
    
    print(f"\n✅ EpochAI Cost Prediction completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())