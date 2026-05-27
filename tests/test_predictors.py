"""
Unit tests for prediction models
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from predictors.cost_predictor import AdvancedCostPredictor
from predictors.optimized_predictor import OptimizedCostPredictor
from predictors.ultimate_predictor import UltimateCostPredictor
from data.generators import generate_synthetic_data
from core.exceptions import InsufficientDataError, ModelNotTrainedError


class TestPredictors(unittest.TestCase):
    """Test cases for prediction models"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = generate_synthetic_data(100, seed=42)
        self.small_data = generate_synthetic_data(10, seed=42)
    
    def test_advanced_cost_predictor_initialization(self):
        """Test AdvancedCostPredictor initialization"""
        predictor = AdvancedCostPredictor()
        self.assertFalse(predictor.is_trained)
        self.assertEqual(predictor.model_name, 'AdvancedCostPredictor')
        self.assertIn('xgboost', predictor.models)
        self.assertIn('random_forest', predictor.models)
    
    def test_advanced_cost_predictor_training(self):
        """Test AdvancedCostPredictor training"""
        predictor = AdvancedCostPredictor()
        
        # Test successful training
        predictor.train(self.test_data)
        self.assertTrue(predictor.is_trained)
        
        # Test insufficient data error
        with self.assertRaises(InsufficientDataError):
            predictor.train(self.small_data)
    
    def test_advanced_cost_predictor_prediction(self):
        """Test AdvancedCostPredictor prediction"""
        predictor = AdvancedCostPredictor()
        
        # Test prediction without training
        with self.assertRaises(ModelNotTrainedError):
            predictor.predict(self.test_data[-1], self.test_data)
        
        # Test prediction after training
        predictor.train(self.test_data)
        prediction = predictor.predict(self.test_data[-1], self.test_data)
        
        self.assertIn(prediction.direction, ['UP', 'DOWN', 'NEUTRAL'])
        self.assertIsInstance(prediction.expected_return, float)
        self.assertTrue(0 <= prediction.confidence <= 1)
        self.assertIn('p10', prediction.quantiles)
        self.assertIn('p50', prediction.quantiles)
        self.assertIn('p90', prediction.quantiles)
        self.assertIn('var95', prediction.risk_metrics)
    
    def test_optimized_cost_predictor(self):
        """Test OptimizedCostPredictor"""
        predictor = OptimizedCostPredictor()
        
        # Test training
        predictor.train(self.test_data)
        self.assertTrue(predictor.is_trained)
        
        # Test prediction
        prediction = predictor.predict(self.test_data[-1], self.test_data)
        self.assertIn(prediction.direction, ['UP', 'DOWN', 'NEUTRAL'])
        
        # Test model info
        info = predictor.get_model_info()
        self.assertEqual(info['type'], 'OptimizedCostPredictor')
        self.assertEqual(info['optimization_level'], 'High')
    
    def test_ultimate_cost_predictor(self):
        """Test UltimateCostPredictor"""
        predictor = UltimateCostPredictor()
        
        # Test training with minimal data
        predictor.train(self.test_data[-20:])  # Use only 20 points
        self.assertTrue(predictor.is_trained)
        
        # Test prediction
        prediction = predictor.predict(self.test_data[-1], self.test_data)
        self.assertIn(prediction.direction, ['UP', 'DOWN', 'NEUTRAL'])
        
        # Test model info
        info = predictor.get_model_info()
        self.assertEqual(info['type'], 'UltimateCostPredictor')
        self.assertEqual(info['optimization_level'], 'Ultimate')
    
    def test_predictor_feature_importance(self):
        """Test feature importance extraction"""
        predictor = AdvancedCostPredictor()
        predictor.train(self.test_data)
        
        feature_importance = predictor.get_feature_importance()
        self.assertIsInstance(feature_importance, dict)
        self.assertIn('xgboost', feature_importance)
        self.assertIn('random_forest', feature_importance)
    
    def test_predictor_model_info(self):
        """Test model information retrieval"""
        predictor = AdvancedCostPredictor()
        
        # Test info before training
        info = predictor.get_model_info()
        self.assertFalse(info['is_trained'])
        self.assertEqual(info['type'], 'AdvancedCostPredictor')
        
        # Test info after training
        predictor.train(self.test_data)
        info = predictor.get_model_info()
        self.assertTrue(info['is_trained'])


class TestPredictorPerformance(unittest.TestCase):
    """Performance tests for predictors"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = generate_synthetic_data(200, seed=42)
    
    def test_prediction_speed_comparison(self):
        """Compare prediction speeds across different predictors"""
        import time
        
        predictors = [
            ('Advanced', AdvancedCostPredictor()),
            ('Optimized', OptimizedCostPredictor()),
            ('Ultimate', UltimateCostPredictor())
        ]
        
        results = {}
        
        for name, predictor in predictors:
            # Train predictor
            predictor.train(self.test_data)
            
            # Time predictions
            start_time = time.time()
            for i in range(10):  # 10 predictions
                predictor.predict(self.test_data[-1], self.test_data)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10
            results[name] = avg_time
        
        # Ultimate should be fastest
        self.assertLess(results['Ultimate'], results['Optimized'])
        self.assertLess(results['Optimized'], results['Advanced'])
        
        print(f"Prediction speeds: {results}")


if __name__ == '__main__':
    unittest.main()