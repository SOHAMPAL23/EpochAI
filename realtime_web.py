from flask import Flask, render_template, jsonify
import random
import time
import threading
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Global market state
market_state = {
    'price': 100.0,
    'volatility': 0.02,
    'trend': 0.001,
    'regime': 'STABLE',
    'last_update': datetime.now()
}

# Historical data storage
price_history = []
prediction_history = []

def simulate_market():
    """Real-time market simulation"""
    global market_state
    
    while True:
        try:
            # Random market factors
            news_impact = random.uniform(-0.03, 0.03)  # News events
            volatility_shock = random.uniform(0.8, 1.3)  # Volatility changes
            trend_shift = random.uniform(-0.002, 0.003)  # Trend changes
            
            # Apply market dynamics
            market_state['volatility'] *= volatility_shock
            market_state['volatility'] = max(0.005, min(0.08, market_state['volatility']))
            
            market_state['trend'] += trend_shift
            market_state['trend'] = max(-0.01, min(0.01, market_state['trend']))
            
            # Price movement with momentum and mean reversion
            momentum = market_state['trend'] * market_state['price']
            random_move = random.gauss(0, market_state['volatility'] * market_state['price'])
            mean_reversion = (100 - market_state['price']) * 0.001  # Revert to 100
            
            price_change = momentum + random_move + mean_reversion + (news_impact * market_state['price'])
            market_state['price'] = max(50, market_state['price'] + price_change)
            
            # Update regime based on volatility and trend
            update_market_regime()
            
            # Store historical data
            timestamp = datetime.now()
            price_history.append({
                'timestamp': timestamp.isoformat(),
                'price': round(market_state['price'], 2),
                'volatility': round(market_state['volatility'], 4),
                'trend': round(market_state['trend'], 4)
            })
            
            # Keep only last 100 data points
            if len(price_history) > 100:
                price_history.pop(0)
            
            market_state['last_update'] = timestamp
            time.sleep(1)  # Update every second
            
        except Exception as e:
            print(f"Simulation error: {e}")
            time.sleep(1)

def update_market_regime():
    """Update market regime based on current conditions"""
    vol = market_state['volatility']
    trend = abs(market_state['trend'])
    
    if vol > 0.04 and trend > 0.005:
        market_state['regime'] = 'VOLATILE_BULL' if market_state['trend'] > 0 else 'VOLATILE_BEAR'
    elif vol > 0.04:
        market_state['regime'] = 'HIGH_VOLATILITY'
    elif trend > 0.003:
        market_state['regime'] = 'STABLE_BULL' if market_state['trend'] > 0 else 'STABLE_BEAR'
    else:
        market_state['regime'] = 'STABLE'

def advanced_prediction_model():
    """Enhanced prediction algorithm"""
    current_price = market_state['price']
    volatility = market_state['volatility']
    trend = market_state['trend']
    regime = market_state['regime']
    
    # Base prediction from trend
    base_return = trend * 100  # Convert to percentage
    
    # Regime adjustments
    regime_multiplier = 1.0
    if 'BULL' in regime:
        regime_multiplier = 1.3
    elif 'BEAR' in regime:
        regime_multiplier = 0.7
    elif 'VOLATILE' in regime:
        regime_multiplier = 0.8
    
    # Confidence based on regime stability
    confidence_base = 0.7
    if regime == 'STABLE':
        confidence_base = 0.8
    elif 'VOLATILE' in regime:
        confidence_base = 0.5
    
    # Final calculations
    expected_return = base_return * regime_multiplier
    confidence = min(0.95, max(0.3, confidence_base + random.uniform(-0.1, 0.1)))
    
    # Quantiles based on volatility
    spread = volatility * 100 * 2  # 2 standard deviations
    p50 = expected_return
    p10 = p50 - spread * 0.8
    p90 = p50 + spread * 0.6
    
    # Risk metrics
    var95 = abs(p10) * 1.2
    max_drawdown = -abs(var95 * random.uniform(2.5, 4.0))
    
    return {
        'direction': 'UP' if expected_return > 0 else 'DOWN',
        'expected_return': round(expected_return, 3),
        'confidence': round(confidence, 3),
        'quantiles': {
            'p10': round(p10, 3),
            'p50': round(p50, 3),
            'p90': round(p90, 3)
        },
        'regime': regime.replace('_', ' ').title(),
        'risk_metrics': {
            'var95': round(var95, 3),
            'max_drawdown': round(max_drawdown, 3)
        }
    }

# Start market simulation in background thread
simulation_thread = threading.Thread(target=simulate_market, daemon=True)
simulation_thread.start()

@app.route('/')
def index():
    return render_template('realtime_dashboard.html')

@app.route('/api/market-data')
def get_market_data():
    """Get current market data"""
    return jsonify({
        'price': round(market_state['price'], 2),
        'volatility': round(market_state['volatility'], 4),
        'trend': round(market_state['trend'], 4),
        'regime': market_state['regime'].replace('_', ' ').title(),
        'last_update': market_state['last_update'].isoformat(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/prediction')
def get_prediction():
    """Get AI prediction"""
    prediction = advanced_prediction_model()
    
    # Store prediction history
    prediction_record = {
        'timestamp': datetime.now().isoformat(),
        'prediction': prediction
    }
    prediction_history.append(prediction_record)
    
    # Keep last 50 predictions
    if len(prediction_history) > 50:
        prediction_history.pop(0)
    
    return jsonify(prediction)

@app.route('/api/history')
def get_history():
    """Get historical data"""
    return jsonify({
        'prices': price_history[-30:],  # Last 30 points
        'predictions': prediction_history[-10:]  # Last 10 predictions
    })

@app.route('/api/reset')
def reset_market():
    """Reset market to initial state"""
    global market_state
    market_state = {
        'price': 100.0,
        'volatility': 0.02,
        'trend': 0.001,
        'regime': 'STABLE',
        'last_update': datetime.now()
    }
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)