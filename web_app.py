from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.data_generator import generate_synthetic_data
from src.models.ensemble_model import EnsembleForecaster
import json
import plotly.graph_objs as go
import plotly.utils

app = Flask(__name__)

# Initialize model globally
print("Loading model...")
ensemble = EnsembleForecaster(optimize_hyperparams=False)
sample_data = generate_synthetic_data(252)
ensemble.xgboost.train(sample_data[-126:])
ensemble.random_forest.train(sample_data[-126:])
ensemble.lstm.train(sample_data[-126:])
print("Model loaded!")

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get latest data point
        latest_data = sample_data[-1]
        
        # Create feature vector
        features = {
            'realized_vol_20d': latest_data.realized_vol_20d or 0.2,
            'momentum_5d': latest_data.momentum_5d or 0.01,
            'vix_zscore': latest_data.vix_zscore or 0,
            'sma_20': latest_data.close,
            'sma_50': latest_data.close,
            'rsi': 50,
            'macd': 0,
            'bb_position': 0.5
        }
        
        from src.utils.feature_engineering import FeatureVector
        feature_vector = FeatureVector(**features)
        
        # Make prediction
        prediction = ensemble.predict(feature_vector, sample_data[-30:])
        
        # Generate chart data
        dates = [d.date.strftime('%Y-%m-%d') for d in sample_data[-30:]]
        prices = [d.close for d in sample_data[-30:]]
        
        # Create response
        response = {
            'prediction': {
                'direction': prediction.direction,
                'expected_return': round(prediction.expected_return, 3),
                'confidence': round(prediction.confidence, 3),
                'quantiles': {
                    'p10': round(prediction.quantiles['p10'], 3),
                    'p50': round(prediction.quantiles['p50'], 3),
                    'p90': round(prediction.quantiles['p90'], 3)
                },
                'regime': prediction.regime['current'],
                'risk_metrics': {
                    'var95': round(prediction.risk_metrics['var95'], 3),
                    'max_drawdown': round(prediction.risk_metrics['max_drawdown'], 3)
                }
            },
            'chart_data': {
                'dates': dates,
                'prices': prices
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historical')
def historical():
    try:
        # Generate historical predictions for chart
        historical_predictions = []
        test_data = sample_data[-60:]  # Last 60 days
        
        for i in range(30, len(test_data)):
            historical_data = test_data[:i]
            
            # Create features from latest data point
            latest_point = historical_data[-1]
            features = {
                'realized_vol_20d': latest_point.realized_vol_20d or 0.2,
                'momentum_5d': latest_point.momentum_5d or 0.01,
                'vix_zscore': latest_point.vix_zscore or 0,
                'sma_20': latest_point.close,
                'sma_50': latest_point.close,
                'rsi': 50,
                'macd': 0,
                'bb_position': 0.5
            }
            
            from src.utils.feature_engineering import FeatureVector
            feature_vector = FeatureVector(**features)
            
            # Make prediction
            prediction = ensemble.predict(feature_vector, historical_data[-30:])
            
            # Compare with actual next day return
            if i < len(test_data) - 1:
                actual_return = ((test_data[i+1].close - test_data[i].close) / test_data[i].close) * 100
                historical_predictions.append({
                    'date': test_data[i].date.strftime('%Y-%m-%d'),
                    'predicted_direction': prediction.direction,
                    'predicted_return': round(prediction.expected_return, 3),
                    'actual_return': round(actual_return, 3),
                    'confidence': round(prediction.confidence, 3),
                    'correct': (prediction.direction == 'UP') == (actual_return > 0)
                })
        
        return jsonify(historical_predictions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)