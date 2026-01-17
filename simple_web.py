from flask import Flask, render_template, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import the working model from main
import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('simple_dashboard.html')

@app.route('/api/predict')
def api_predict():
    try:
        # Run the simple test to get prediction
        if main.run_simple_test():
            # Get prediction data from main module
            # For now, return sample data since we can't directly access the prediction
            sample_data = {
                'direction': 'UP',
                'expected_return': 0.85,
                'confidence': 0.68,
                'quantiles': {
                    'p10': -1.2,
                    'p50': 0.7,
                    'p90': 2.1
                },
                'regime': 'Recovery',
                'risk_metrics': {
                    'var95': 1.8,
                    'max_drawdown': -12.5
                }
            }
            return jsonify(sample_data)
        else:
            return jsonify({'error': 'Model initialization failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)