#!/usr/bin/env python3
"""
Comprehensive benchmarking script for EpochAI predictors
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from predictors.cost_predictor import AdvancedCostPredictor
from predictors.optimized_predictor import OptimizedCostPredictor
from predictors.ultimate_predictor import UltimateCostPredictor
from data.generators import generate_synthetic_data
from utils.performance import PerformanceMonitor, Timer, optimize_memory, profile_system_resources
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('benchmark')


class PredictorBenchmark:
    """Comprehensive benchmarking for prediction models"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.results = {}
    
    def benchmark_predictor(self, predictor_class, name: str, data_sizes: list, 
                           prediction_counts: list) -> dict:
        """Benchmark a specific predictor"""
        logger.info(f"Benchmarking {name}")
        
        results = {
            'name': name,
            'training_times': {},
            'prediction_times': {},
            'memory_usage': {},
            'accuracy_metrics': {}
        }
        
        for data_size in data_sizes:
            logger.info(f"  Testing with {data_size} data points")
            
            # Generate test data
            test_data = generate_synthetic_data(data_size, seed=42)
            
            # Initialize predictor
            predictor = predictor_class()
            
            # Benchmark training
            with Timer(f"{name} Training ({data_size} points)", log_result=False) as timer:
                try:
                    predictor.train(test_data)
                    training_time = timer.get_elapsed_time()
                    results['training_times'][data_size] = training_time
                    logger.info(f"    Training: {training_time:.4f}s")
                except Exception as e:
                    logger.error(f"    Training failed: {e}")
                    results['training_times'][data_size] = None
                    continue
            
            # Benchmark predictions
            for pred_count in prediction_counts:
                logger.info(f"    Testing {pred_count} predictions")
                
                start_time = time.time()
                successful_predictions = 0
                
                try:
                    for i in range(pred_count):
                        # Use different data points for variety
                        current_data = test_data[-(i % min(len(test_data), 50) + 1)]
                        prediction = predictor.predict(current_data, test_data)
                        successful_predictions += 1
                    
                    total_time = time.time() - start_time
                    avg_time = total_time / successful_predictions if successful_predictions > 0 else 0
                    
                    key = f"{data_size}_{pred_count}"
                    results['prediction_times'][key] = {
                        'total_time': total_time,
                        'avg_time': avg_time,
                        'predictions_per_second': successful_predictions / total_time if total_time > 0 else 0,
                        'successful_predictions': successful_predictions
                    }
                    
                    logger.info(f"      Avg prediction time: {avg_time*1000:.2f}ms")
                    logger.info(f"      Throughput: {successful_predictions/total_time:.1f} pred/s")
                    
                except Exception as e:
                    logger.error(f"    Prediction benchmark failed: {e}")
                    results['prediction_times'][key] = None
            
            # Memory usage
            memory_info = profile_system_resources()
            results['memory_usage'][data_size] = memory_info['memory_rss_mb']
        
        return results
    
    def run_comprehensive_benchmark(self) -> dict:
        """Run comprehensive benchmark across all predictors"""
        logger.info("Starting comprehensive benchmark")
        
        # Test configurations
        data_sizes = [50, 100, 200, 500]
        prediction_counts = [10, 50, 100]
        
        predictors = [
            (AdvancedCostPredictor, 'Advanced'),
            (OptimizedCostPredictor, 'Optimized'),
            (UltimateCostPredictor, 'Ultimate')
        ]
        
        benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': profile_system_resources(),
            'test_config': {
                'data_sizes': data_sizes,
                'prediction_counts': prediction_counts
            },
            'results': {}
        }
        
        for predictor_class, name in predictors:
            try:
                result = self.benchmark_predictor(predictor_class, name, data_sizes, prediction_counts)
                benchmark_results['results'][name] = result
                
                # Optimize memory between tests
                optimize_memory()
                
            except Exception as e:
                logger.error(f"Benchmark failed for {name}: {e}")
                benchmark_results['results'][name] = {'error': str(e)}
        
        return benchmark_results
    
    def generate_report(self, results: dict) -> str:
        """Generate a formatted benchmark report"""
        report = []
        report.append("=" * 80)
        report.append("EpochAI Predictor Benchmark Report")
        report.append("=" * 80)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"System Memory: {results['system_info']['memory_rss_mb']:.1f} MB")
        report.append(f"System CPU: {results['system_info']['cpu_percent']:.1f}%")
        report.append("")
        
        # Training performance comparison
        report.append("Training Performance (seconds)")
        report.append("-" * 50)
        
        data_sizes = results['test_config']['data_sizes']
        predictor_names = list(results['results'].keys())
        
        # Header
        header = f"{'Data Size':<12}"
        for name in predictor_names:
            header += f"{name:<12}"
        report.append(header)
        report.append("-" * len(header))
        
        # Training times
        for size in data_sizes:
            row = f"{size:<12}"
            for name in predictor_names:
                if name in results['results'] and 'training_times' in results['results'][name]:
                    time_val = results['results'][name]['training_times'].get(size)
                    if time_val is not None:
                        row += f"{time_val:<12.4f}"
                    else:
                        row += f"{'FAILED':<12}"
                else:
                    row += f"{'N/A':<12}"
            report.append(row)
        
        report.append("")
        
        # Prediction performance comparison
        report.append("Prediction Performance (ms per prediction)")
        report.append("-" * 60)
        
        # Use largest data size and medium prediction count for comparison
        test_size = max(data_sizes)
        test_count = 50
        key = f"{test_size}_{test_count}"
        
        for name in predictor_names:
            if (name in results['results'] and 
                'prediction_times' in results['results'][name] and
                key in results['results'][name]['prediction_times']):
                
                pred_data = results['results'][name]['prediction_times'][key]
                if pred_data:
                    avg_time_ms = pred_data['avg_time'] * 1000
                    throughput = pred_data['predictions_per_second']
                    report.append(f"{name:<12}: {avg_time_ms:>8.2f} ms/pred, {throughput:>8.1f} pred/s")
                else:
                    report.append(f"{name:<12}: FAILED")
            else:
                report.append(f"{name:<12}: N/A")
        
        report.append("")
        
        # Memory usage comparison
        report.append("Memory Usage (MB)")
        report.append("-" * 30)
        
        for name in predictor_names:
            if name in results['results'] and 'memory_usage' in results['results'][name]:
                memory_usage = results['results'][name]['memory_usage']
                if memory_usage:
                    max_memory = max(memory_usage.values())
                    report.append(f"{name:<12}: {max_memory:>8.1f} MB")
                else:
                    report.append(f"{name:<12}: N/A")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main benchmarking function"""
    parser = argparse.ArgumentParser(description='Benchmark EpochAI Predictors')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark')
    
    args = parser.parse_args()
    
    print("🚀 EpochAI Predictor Benchmark")
    print("=" * 50)
    
    # Initialize benchmark
    benchmark = PredictorBenchmark()
    
    # Run benchmark
    if args.quick:
        logger.info("Running quick benchmark")
        # Quick benchmark with smaller data sizes
        data_sizes = [50, 100]
        prediction_counts = [10, 25]
        
        predictors = [
            (OptimizedCostPredictor, 'Optimized'),
            (UltimateCostPredictor, 'Ultimate')
        ]
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': profile_system_resources(),
            'test_config': {
                'data_sizes': data_sizes,
                'prediction_counts': prediction_counts
            },
            'results': {}
        }
        
        for predictor_class, name in predictors:
            result = benchmark.benchmark_predictor(predictor_class, name, data_sizes, prediction_counts)
            results['results'][name] = result
    else:
        logger.info("Running comprehensive benchmark")
        results = benchmark.run_comprehensive_benchmark()
    
    # Generate report
    if args.json:
        import json
        output = json.dumps(results, indent=2)
    else:
        output = benchmark.generate_report(results)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)
    
    print("\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    main()