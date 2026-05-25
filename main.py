#!/usr/bin/env python3
"""
EpochAI - Main Entry Point
Multi-Modal Financial Forecasting Engine with Modular Architecture
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('main')


def run_prediction_demo():
    """Run a prediction demonstration"""
    from predictors.cost_predictor import AdvancedCostPredictor
    from data.generators import generate_synthetic_data
    
    print("EpochAI - Financial Forecasting Engine")
    print("=" * 50)
    
    # Generate synthetic data
    print("Generating synthetic market data...")
    historical_data = generate_synthetic_data(252)  # 1 year of data
    print(f"Generated {len(historical_data)} data points")
    
    # Initialize and train predictor
    print("Initializing Advanced Cost Predictor...")
    predictor = AdvancedCostPredictor()
    
    print("Training model...")
    start_time = datetime.now()
    predictor.train(historical_data)
    training_time = (datetime.now() - start_time).total_seconds()
    print(f"Model trained in {training_time:.2f} seconds")
    
    # Make predictions
    print("\nMaking sample predictions:")
    print("-" * 50)
    
    for i in range(3):
        current_data = historical_data[-(i+1)]
        prediction = predictor.predict(current_data, historical_data)
        
        print(f"\nPrediction {i+1}:")
        print(f"   Direction: {prediction.direction}")
        print(f"   Expected Return: {prediction.expected_return:.3f}%")
        print(f"   Confidence: {prediction.confidence:.3f}")
        print(f"   Regime: {prediction.regime}")
        print(f"   Risk VaR95: {prediction.risk_metrics['var95']:.3f}%")
    
    print(f"\nDemonstration completed successfully!")


def run_web_app():
    """Run the web application"""
    from web.apps.main_app import create_main_app
    
    print("Starting EpochAI Web Dashboard...")
    app = create_main_app()
    
    print(f"Server starting on http://{settings.web.host}:{settings.web.port}")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host=settings.web.host,
        port=settings.web.port,
        debug=settings.web.debug
    )


def show_system_info():
    """Show system information"""
    print("EpochAI System Information")
    print("=" * 40)
    print(f"Environment: {settings.environment}")
    print(f"Log Level: {settings.log_level}")
    print(f"Web Host: {settings.web.host}")
    print(f"Web Port: {settings.web.port}")
    print(f"Debug Mode: {settings.web.debug}")
    print(f"Max Training Samples: {settings.model.max_training_samples}")
    print(f"Min Training Samples: {settings.model.min_training_samples}")
    print(f"Data Buffer Size: {settings.data.max_buffer_size}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='EpochAI - Multi-Modal Financial Forecasting Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py demo              # Run prediction demonstration
  python main.py web               # Start web dashboard
  python main.py info              # Show system information
  
For more options, use the scripts in the scripts/ directory:
  python scripts/run_prediction.py --help
  python scripts/run_web_app.py --help
        """
    )
    
    parser.add_argument('command', 
                       choices=['demo', 'web', 'info'],
                       help='Command to run')
    
    parser.add_argument('--log-level', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Override log level')
    
    args = parser.parse_args()
    
    # Override log level if specified
    if args.log_level:
        setup_logging(args.log_level)
    
    try:
        if args.command == 'demo':
            run_prediction_demo()
        elif args.command == 'web':
            run_web_app()
        elif args.command == 'info':
            show_system_info()
        
        return 0
        
    except KeyboardInterrupt:
        print("\nStopped by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())