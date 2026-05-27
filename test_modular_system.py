#!/usr/bin/env python3
"""
Test script to verify the modular EpochAI system works correctly
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported correctly"""
    print("🔍 Testing module imports...")
    
    try:
        # Core modules
        from core.data_models import MarketData, PredictionResult, FeatureVector
        from core.base_predictor import BasePredictor
        from core.exceptions import EpochAIException, InsufficientDataError
        print("  ✅ Core modules imported successfully")
        
        # Configuration
        from config.settings import settings
        from config.logging_config import setup_logging, get_logger
        print("  ✅ Configuration modules imported successfully")
        
        # Predictors
        from predictors.cost_predictor import AdvancedCostPredictor
        from predictors.optimized_predictor import OptimizedCostPredictor
        from predictors.ultimate_predictor import UltimateCostPredictor
        print("  ✅ Predictor modules imported successfully")
        
        # Features
        from features.extractors import BasicFeatureExtractor, OptimizedFeatureExtractor
        from features.engineering import FeatureEngineer
        from features.technical_indicators import TechnicalIndicators
        print("  ✅ Feature modules imported successfully")
        
        # Risk management
        from risk.managers import BasicRiskManager, OptimizedRiskManager
        from risk.regime_detection import BasicRegimeDetector, OptimizedRegimeDetector
        print("  ✅ Risk management modules imported successfully")
        
        # Data handling
        from data.generators import generate_synthetic_data, SyntheticDataGenerator
        print("  ✅ Data modules imported successfully")
        
        # Utilities
        from utils.helpers import format_currency, format_percentage, calculate_returns
        from utils.performance import PerformanceMonitor, benchmark_function
        from utils.validation import DataValidator, validate_model_inputs
        print("  ✅ Utility modules imported successfully")
        
        # Web applications
        from web.apps.main_app import create_main_app
        from web.apps.realtime_app import create_realtime_app
        from web.apps.simple_app import create_simple_app
        print("  ✅ Web application modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of the modular system"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Import required modules
        from data.generators import generate_synthetic_data
        from predictors.cost_predictor import AdvancedCostPredictor
        from features.engineering import FeatureEngineer
        from utils.validation import DataValidator
        
        # Generate test data
        print("  📊 Generating synthetic data...")
        data = generate_synthetic_data(100, seed=42)
        print(f"    Generated {len(data)} data points")
        
        # Validate data
        print("  🔍 Validating data...")
        validator = DataValidator()
        is_valid = validator.validate_market_data(data)
        print(f"    Data validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        
        # Test feature engineering
        print("  🔧 Testing feature engineering...")
        engineer = FeatureEngineer()
        feature_vector = engineer.create_feature_vector(data, -1)
        print(f"    Created feature vector with {len(feature_vector.to_array())} features")
        
        # Test predictor
        print("  🤖 Testing predictor...")
        predictor = AdvancedCostPredictor()
        predictor.train(data)
        print("    Model trained successfully")
        
        prediction = predictor.predict(data[-1], data)
        print(f"    Prediction: {prediction.direction} ({prediction.expected_return:.3f}%)")
        print(f"    Confidence: {prediction.confidence:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Functionality test failed: {e}")
        return False


def test_performance_comparison():
    """Test performance comparison between different predictors"""
    print("\n⚡ Testing performance comparison...")
    
    try:
        import time
        from data.generators import generate_synthetic_data
        from predictors.cost_predictor import AdvancedCostPredictor
        from predictors.optimized_predictor import OptimizedCostPredictor
        from predictors.ultimate_predictor import UltimateCostPredictor
        
        # Generate test data
        data = generate_synthetic_data(200, seed=42)
        
        predictors = [
            ('Advanced', AdvancedCostPredictor()),
            ('Optimized', OptimizedCostPredictor()),
            ('Ultimate', UltimateCostPredictor())
        ]
        
        results = {}
        
        for name, predictor in predictors:
            print(f"  Testing {name} predictor...")
            
            # Training time
            start_time = time.time()
            predictor.train(data)
            training_time = time.time() - start_time
            
            # Prediction time (average of 10 predictions)
            start_time = time.time()
            for i in range(10):
                predictor.predict(data[-1], data)
            prediction_time = (time.time() - start_time) / 10
            
            results[name] = {
                'training_time': training_time,
                'prediction_time': prediction_time
            }
            
            print(f"    Training: {training_time:.4f}s")
            print(f"    Prediction: {prediction_time*1000:.2f}ms")
        
        # Verify performance ordering (Ultimate should be fastest)
        ultimate_pred_time = results['Ultimate']['prediction_time']
        optimized_pred_time = results['Optimized']['prediction_time']
        advanced_pred_time = results['Advanced']['prediction_time']
        
        if ultimate_pred_time <= optimized_pred_time <= advanced_pred_time:
            print("  ✅ Performance ordering correct (Ultimate ≤ Optimized ≤ Advanced)")
        else:
            print("  ⚠️  Performance ordering unexpected")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance test failed: {e}")
        return False


def test_web_applications():
    """Test web application creation"""
    print("\n🌐 Testing web applications...")
    
    try:
        from web.apps.main_app import create_main_app
        from web.apps.realtime_app import create_realtime_app
        from web.apps.simple_app import create_simple_app
        
        # Test main app creation
        print("  Creating main app...")
        main_app = create_main_app()
        print("    ✅ Main app created successfully")
        
        # Test realtime app creation
        print("  Creating realtime app...")
        realtime_app = create_realtime_app()
        print("    ✅ Realtime app created successfully")
        
        # Test simple app creation
        print("  Creating simple app...")
        simple_app = create_simple_app()
        print("    ✅ Simple app created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Web application test failed: {e}")
        return False


def test_configuration_system():
    """Test configuration system"""
    print("\n⚙️  Testing configuration system...")
    
    try:
        from config.settings import settings, Settings
        from config.logging_config import setup_logging, get_logger
        
        # Test settings access
        print(f"  Environment: {settings.environment}")
        print(f"  Log level: {settings.log_level}")
        print(f"  Web host: {settings.web.host}")
        print(f"  Web port: {settings.web.port}")
        print(f"  Model max training samples: {settings.model.max_training_samples}")
        
        # Test logging setup
        setup_logging('INFO')
        logger = get_logger('test')
        logger.info("Test log message")
        print("    ✅ Logging system working")
        
        # Test settings serialization
        settings_dict = settings.to_dict()
        new_settings = Settings.from_dict(settings_dict)
        print("    ✅ Settings serialization working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 EpochAI Modular System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    tests = [
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Performance Comparison", test_performance_comparison),
        ("Web Applications", test_web_applications),
        ("Configuration System", test_configuration_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())