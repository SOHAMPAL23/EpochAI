from flask import Flask, render_template, jsonify
import random
import math

app = Flask(__name__)

def generate_sample_prediction():
    """Generate realistic sample prediction data"""
    directions = ['UP', 'DOWN']
    regimes = ['Recovery', 'Stable', 'Volatile', 'Bull', 'Bear']
    
    direction = random.choice(directions)
    confidence = round(random.uniform(0.5, 0.85), 3)
    
    # Generate correlated returns based on direction and confidence
    base_return = random.uniform(0.2, 2.5) * (1 if direction == 'UP' else -1)
    # Adjust return based on confidence (higher confidence = larger returns)
    adjusted_return = base_return * (0.5 + confidence)
    
    # Generate quantiles with realistic spread
    p50 = round(adjusted_return, 3)
    spread = random.uniform(0.8, 2.0)
    p10 = round(p50 - spread, 3)
    p90 = round(p50 + spread * 0.7, 3)  # P90 closer to P50
    
    # Risk metrics
    var95 = round(abs(p10) * random.uniform(0.8, 1.2), 3)
    max_drawdown = round(-abs(var95 * random.uniform(2.0, 4.0)), 3)
    
    return {
        'direction': direction,
        'expected_return': round(adjusted_return, 3),
        'confidence': confidence,
        'quantiles': {
            'p10': p10,
            'p50': p50,
            'p90': p90
        },
        'regime': random.choice(regimes),
        'risk_metrics': {
            'var95': var95,
            'max_drawdown': max_drawdown
        }
    }

@app.route('/')
def index():
    return render_template('standalone_dashboard.html')

@app.route('/api/predict')
def api_predict():
    try:
        prediction = generate_sample_prediction()
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)