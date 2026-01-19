#!/usr/bin/env python3
"""
ModelQ Pro - Real-Time Cost Prediction Engine
Standalone version for continuous cost forecasting
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the main predictor from our consolidated file
from ModelQ_Cost_Predictor import CostPredictionEngine
import time
import threading

def run_real_time_prediction():
    """Run the cost prediction engine in real-time mode"""
    print("🚀 Starting ModelQ Pro - Real-Time Cost Prediction Engine")
    print("=" * 60)
    
    # Create the prediction engine
    engine = CostPredictionEngine()
    
    # Start simulating data
    print("📈 Starting real-time data simulation...")
    
    # Run data simulation in background
    data_thread = threading.Thread(target=engine.simulate_real_time_data)
    data_thread.daemon = True
    data_thread.start()
    
    # Wait for initial data collection
    print("⏳ Collecting initial market data...")
    while len(engine.data_buffer) < 30:
        time.sleep(0.1)
    
    print(f"✅ Collected {len(engine.data_buffer)} data points, training model...")
    
    # Train the initial model
    engine.train_if_needed()
    
    print("🤖 Model trained successfully! Starting real-time predictions...")
    print("\nLive Predictions (updates every 5 seconds):")
    print("-" * 50)
    
    # Continuous prediction loop
    try:
        while True:
            if engine.predictor.is_trained and len(engine.data_buffer) > 0:
                latest_prediction = engine.get_latest_prediction()
                if latest_prediction:
                    print(f"\r📊 [{time.strftime('%H:%M:%S')}] "
                          f"Direction: {latest_prediction.direction} | "
                          f"Return: {latest_prediction.expected_return:.2f}% | "
                          f"Conf: {latest_prediction.confidence:.2f} | "
                          f"Regime: {latest_prediction.regime} | "
                          f"VaR: {latest_prediction.risk_metrics['var95']:.2f}%", 
                          end="", flush=True)
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping ModelQ Pro...")
        engine.stop()
        print("✅ ModelQ Pro stopped successfully!")

if __name__ == "__main__":
    run_real_time_prediction()