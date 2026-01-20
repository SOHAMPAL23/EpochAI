#!/usr/bin/env python3
"""
ModelQ Pro - High-Performance Real-Time Cost Prediction Engine
Ultra-fast implementation for real-time cost forecasting with optimized performance
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the optimized predictor
from ModelQ_Optimized_Predictor import UltraEfficientPredictionEngine
import time
import threading
from datetime import datetime

def run_high_performance_prediction():
    """Run the cost prediction engine in high-performance mode"""
    print("🚀 Starting ModelQ Pro - High-Performance Cost Prediction Engine")
    print("=" * 70)
    
    # Create the prediction engine
    engine = UltraEfficientPredictionEngine()
    
    # Start simulating data
    print("📈 Starting high-performance data simulation...")
    
    # Run data simulation in background
    data_thread = threading.Thread(target=engine.simulate_real_time_data, args=(2.0,))  # 2 minutes of data
    data_thread.daemon = True
    data_thread.start()
    
    # Wait for initial data collection
    print("⏳ Collecting initial market data...")
    while len(engine.data_buffer) < 20:
        time.sleep(0.05)
    
    print(f"✅ Collected {len(engine.data_buffer)} data points, training model...")
    
    # Train the initial model
    engine.train_if_needed()
    
    print("🤖 Model trained successfully! Starting high-performance predictions...")
    print("\nLive Predictions (high-frequency updates):")
    print("-" * 60)
    
    # Continuous prediction loop with performance metrics
    prediction_count = 0
    start_time = time.time()
    
    try:
        while True:
            if engine.predictor.is_trained and len(engine.data_buffer) > 0:
                latest_prediction = engine.get_latest_prediction()
                if latest_prediction:
                    prediction_count += 1
                    elapsed_time = time.time() - start_time
                    
                    print(f"\r📊 [{time.strftime('%H:%M:%S')}] "
                          f"Dir: {latest_prediction.direction} | "
                          f"Ret: {latest_prediction.expected_return:+.2f}% | "
                          f"Conf: {latest_prediction.confidence:.2f} | "
                          f"Reg: {latest_prediction.regime} | "
                          f"VaR: {latest_prediction.risk_metrics['var95']:.2f}% | "
                          f"Spd: {prediction_count/elapsed_time:.1f} pred/s", 
                          end="", flush=True)
            
            time.sleep(0.05)  # Update every 50ms for high frequency
            
    except KeyboardInterrupt:
        elapsed_time = time.time() - start_time
        print(f"\n\n🛑 Stopping ModelQ Pro...")
        print(f"📈 Performance Summary: {prediction_count} predictions in {elapsed_time:.1f}s ({prediction_count/elapsed_time:.1f} pred/s)")
        engine.stop()
        print("✅ ModelQ Pro stopped successfully!")

def run_benchmark_test():
    """Run a benchmark test to measure performance"""
    print("🚀 Running Performance Benchmark Test...")
    print("=" * 50)
    
    engine = UltraEfficientPredictionEngine()
    
    # Simulate data collection
    start_time = time.time()
    engine.simulate_real_time_data(duration_minutes=1.0)  # 1 minute of data
    data_collection_time = time.time() - start_time
    
    print(f"✅ Data collection: {len(engine.data_buffer)} points in {data_collection_time:.2f}s")
    
    # Train model
    start_time = time.time()
    engine.train_if_needed()
    training_time = time.time() - start_time
    
    print(f"✅ Training: {training_time:.2f}s")
    
    # Test prediction throughput
    print("⚡ Testing prediction throughput...")
    test_predictions = 50
    start_time = time.time()
    
    for i in range(test_predictions):
        if len(engine.data_buffer) > 0:
            current_data = engine.data_buffer[-1]
            prediction = engine.predictor.predict(current_data, engine.data_buffer)
    
    prediction_time = time.time() - start_time
    avg_prediction_time = (prediction_time / test_predictions) * 1000
    throughput = test_predictions / prediction_time
    
    print(f"✅ Prediction throughput: {avg_prediction_time:.2f}ms/prediction ({throughput:.1f} pred/s)")
    
    # Show sample predictions
    print(f"\n🎯 Sample High-Performance Predictions:")
    for i in range(min(3, len(engine.data_buffer))):
        current_data = engine.data_buffer[-(i+1)]
        prediction = engine.predictor.predict(current_data, engine.data_buffer)
        
        print(f"   #{i+1}: {prediction.direction} {prediction.expected_return:+.2f}% "
              f"(Conf: {prediction.confidence:.2f}, Regime: {prediction.regime})")
    
    print(f"\n🏆 Performance Results:")
    print(f"   • Data Collection: {data_collection_time:.2f}s for {len(engine.data_buffer)} points")
    print(f"   • Training Time: {training_time:.2f}s")
    print(f"   • Prediction Speed: {avg_prediction_time:.2f}ms per prediction")
    print(f"   • Throughput: {throughput:.1f} predictions per second")
    
    return {
        'data_collection_time': data_collection_time,
        'training_time': training_time,
        'prediction_speed_ms': avg_prediction_time,
        'throughput': throughput
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ModelQ Pro - High-Performance Cost Prediction')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark')
    parser.add_argument('--live', action='store_true', help='Run live prediction mode')
    
    args = parser.parse_args()
    
    if args.benchmark:
        run_benchmark_test()
    elif args.live or not hasattr(args, 'benchmark'):
        run_high_performance_prediction()