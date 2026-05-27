"""
Unified main Flask web application for EpochAI Dashboard
Features: Background Market Simulation, Live ML Predictor Switching, Telemetry Latency Tracking, Shocks, and Analytics
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import time
import random
import threading
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.data_models import MarketData, FeatureVector
from predictors.cost_predictor import AdvancedCostPredictor
from predictors.optimized_predictor import OptimizedCostPredictor
from predictors.ultimate_predictor import UltimateCostPredictor
from predictors.ensemble_predictor import EnsembleCostPredictor
from data.generators import generate_synthetic_data
from data.loaders import YahooFinanceLoader
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('web.main')

# Global Thread Lock & Market States
lock = threading.Lock()
active_symbol = 'SYNTHETIC'
baseline_price = 100.0
baseline_volatility = 0.02
baseline_trend = 0.001

market_state = {
    'price': 100.0,
    'volatility': 0.02,
    'trend': 0.001,
    'regime': 'STABLE',
    'last_update': datetime.now()
}

price_history = []
sample_data = []  # List of actual MarketData objects for predictor training & scoring
active_shocks = {
    'news': 0.0,
    'volatility': 1.0,
    'trend': 0.0
}

# Globally shared predictor registry
predictors = {}

def simulate_market():
    """Background Daemon Thread: Simulates real-time market data flows"""
    global market_state, price_history, sample_data, active_shocks, baseline_volatility, baseline_trend
    logger.info("Market Simulator Daemon Thread Active")
    
    while True:
        try:
            time.sleep(1.0)
            with lock:
                if not sample_data:
                    continue
                
                # Decay active shocks back towards normal baseline values
                active_shocks['news'] *= 0.82
                active_shocks['trend'] *= 0.85
                active_shocks['volatility'] = 1.0 + (active_shocks['volatility'] - 1.0) * 0.90
                
                # Merge shocks with random volatility / news impacts
                news_impact = random.normalvariate(0, 0.001) + active_shocks['news']
                
                # 1. Update Volatility with mean reversion to baseline_volatility
                # Volatility shock targets (active_shocks['volatility'] - 1.0) * baseline_volatility
                vol_shock_diff = (active_shocks['volatility'] - 1.0) * baseline_volatility
                target_vol = baseline_volatility + vol_shock_diff
                vol_noise = random.normalvariate(0, 0.08 * baseline_volatility)
                
                # Mean reversion coefficient: 0.20 back to target_vol
                market_state['volatility'] += 0.20 * (target_vol - market_state['volatility']) + vol_noise
                market_state['volatility'] = max(0.004, min(0.12, market_state['volatility']))
                
                # 2. Update Trend drift momentum with mean reversion to baseline_trend
                target_trend = baseline_trend + active_shocks['trend']
                trend_noise = random.normalvariate(0, 0.0003)
                
                # Mean reversion coefficient: 0.20 back to target_trend
                market_state['trend'] += 0.20 * (target_trend - market_state['trend']) + trend_noise
                market_state['trend'] = max(-0.015, min(0.015, market_state['trend']))
                
                # Calculate new price with momentum and light mean reversion
                momentum = market_state['trend'] * market_state['price']
                random_move = random.gauss(0, market_state['volatility'] * market_state['price'])
                mean_reversion = (baseline_price - market_state['price']) * 0.0006
                
                price_change = momentum + random_move + mean_reversion + (news_impact * market_state['price'])
                
                old_price = market_state['price']
                market_state['price'] = max(10.0, market_state['price'] + price_change)
                
                # HMM Regime Shifts
                vol = market_state['volatility']
                trend = abs(market_state['trend'])
                if vol > 0.045 and trend > 0.0045:
                    market_state['regime'] = 'VOLATILE_BULL' if market_state['trend'] > 0 else 'VOLATILE_BEAR'
                elif vol > 0.04:
                    market_state['regime'] = 'HIGH_VOLATILITY'
                elif trend > 0.0035:
                    market_state['regime'] = 'STABLE_BULL' if market_state['trend'] > 0 else 'STABLE_BEAR'
                else:
                    market_state['regime'] = 'STABLE'
                
                # Construct high/low/volume
                high = max(old_price, market_state['price']) * (1.0 + random.uniform(0.0001, 0.0015))
                low = min(old_price, market_state['price']) * (1.0 - random.uniform(0.0001, 0.0015))
                volume = int(random.uniform(300000, 1800000) * (vol / 0.02))
                returns = price_change / old_price
                
                # Build unified data point to append to sliding telemetry window
                now = datetime.now()
                new_data = MarketData(
                    timestamp=now,
                    price=market_state['price'],
                    volume=volume,
                    volatility=market_state['volatility'],
                    momentum=market_state['trend'],
                    rsi=min(100.0, max(0.0, 50.0 + market_state['trend'] * 2800.0 + random.gauss(0, 4))),
                    macd=market_state['trend'] * 1200.0 + random.gauss(0, 0.8),
                    high=high,
                    low=low,
                    close=market_state['price'],
                    returns=returns,
                    realized_vol_20d=market_state['volatility'],
                    momentum_5d=market_state['trend'],
                    vix_zscore=max(-4.0, min(4.0, (sample_data[-1].vix_zscore if sample_data else 0.0) + random.gauss(0, 0.15)))
                )
                
                sample_data.append(new_data)
                if len(sample_data) > 400:
                    sample_data.pop(0)
                
                # Save tick histories
                price_history.append({
                    'timestamp': now.strftime('%H:%M:%S'),
                    'price': round(market_state['price'], 2),
                    'volatility': round(market_state['volatility'], 4),
                    'trend': round(market_state['trend'], 4),
                    'regime': market_state['regime'].replace('_', ' ').title()
                })
                if len(price_history) > 100:
                    price_history.pop(0)
                
                market_state['last_update'] = now
                
        except Exception as e:
            logger.error(f"Simulation tick failed: {e}")

def create_main_app():
    """Create and configure the main Flask application"""
    global sample_data, predictors, baseline_price, market_state, price_history, active_symbol, baseline_volatility, baseline_trend
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure app
    app.config['SECRET_KEY'] = settings.web.secret_key
    app.config['DEBUG'] = settings.web.debug
    
    # Initialize & Pre-train predictors in order of complexity
    logger.info("Initializing multi-modal prediction system...")
    sample_data = generate_synthetic_data(252)  # Generate 1 year seed data
    
    predictors['advanced'] = AdvancedCostPredictor()
    predictors['optimized'] = OptimizedCostPredictor()
    predictors['ultimate'] = UltimateCostPredictor()
    predictors['ensemble'] = EnsembleCostPredictor()
    
    # Pre-train models
    for name, pred in predictors.items():
        try:
            pred.train(sample_data[-126:])  # Train on last 6 months seed data
            logger.info(f"Model '{name}' pre-trained successfully")
        except Exception as e:
            logger.error(f"Failed to pre-train model '{name}': {e}")
            
    # Initialize seed market state variables
    last_val = sample_data[-1]
    baseline_price = last_val.close
    baseline_volatility = last_val.volatility
    baseline_trend = last_val.momentum
    market_state['price'] = last_val.close
    market_state['volatility'] = last_val.volatility
    market_state['trend'] = last_val.momentum
    market_state['last_update'] = datetime.now()
    
    for i, data in enumerate(sample_data[-50:]):
        price_history.append({
            'timestamp': (datetime.now() - timedelta(seconds=(50-i))).strftime('%H:%M:%S'),
            'price': round(data.close, 2),
            'volatility': round(data.volatility, 4),
            'trend': round(data.momentum, 4),
            'regime': 'Stable'
        })
    
    # Launch simulation in a separate daemon thread
    simulation_thread = threading.Thread(target=simulate_market, daemon=True)
    simulation_thread.start()
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/')
    def index():
        """Main consolidated intelligence hub page"""
        return render_template('dashboard.html')
    
    @app.route('/predict', methods=['POST', 'GET'])
    def predict():
        """Dynamic Forecast API: Accepts model switcher parameter & computes high-resolution prediction"""
        try:
            model_type = 'advanced'
            if request.method == 'POST':
                if request.is_json:
                    payload = request.get_json() or {}
                    model_type = payload.get('predictor_type', 'advanced').lower()
                else:
                    model_type = request.form.get('predictor_type', 'advanced').lower()
            else:
                model_type = request.args.get('predictor_type', 'advanced').lower()
                
            if model_type not in predictors:
                model_type = 'advanced'
                
            predictor = predictors[model_type]
            
            # Record exact performance counter to showcase millisecond telemetry
            start_time = time.perf_counter()
            
            with lock:
                latest_point = sample_data[-1]
                historical_slice = sample_data[-30:]
                
                prediction = predictor.predict(latest_point, historical_slice)
                
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Format expected return and quantiles accurately
            resp = {
                'predictor_type': model_type.upper(),
                'latency_ms': round(latency_ms, 3),
                'prediction': {
                    'direction': prediction.direction,
                    'expected_return': round(prediction.expected_return, 3),
                    'confidence': round(prediction.confidence, 3),
                    'quantiles': {
                        'p10': round(prediction.quantiles.get('p10', 0.0), 3),
                        'p50': round(prediction.quantiles.get('p50', 0.0), 3),
                        'p90': round(prediction.quantiles.get('p90', 0.0), 3)
                    },
                    'regime': prediction.regime if isinstance(prediction.regime, str) else str(prediction.regime.get('current', 'Stable')),
                    'risk_metrics': {
                        'var95': round(abs(prediction.risk_metrics.get('var95', 0.0)), 3),
                        'max_drawdown': round(prediction.risk_metrics.get('max_drawdown', 0.0), 3)
                    }
                }
            }
            return jsonify(resp)
            
        except Exception as e:
            logger.error(f"Predict route error: {e}")
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/market-data')
    def get_market_data():
        """Retrieve latest market simulator state ticks & history logs"""
        with lock:
            resp = {
                'active_symbol': active_symbol,
                'price': round(market_state['price'], 2),
                'volatility': round(market_state['volatility'], 4),
                'trend': round(market_state['trend'], 4),
                'regime': market_state['regime'].replace('_', ' ').title(),
                'last_update': market_state['last_update'].isoformat(),
                'timestamp': datetime.now().isoformat(),
                'price_history': price_history
            }
        return jsonify(resp)
        
    @app.route('/api/shock', methods=['POST'])
    def inject_shock():
        """Apply market shocks manually (News event, Trend spikes, volatility multipliers)"""
        try:
            payload = request.get_json() or {}
            shock_type = payload.get('shock_type', '')
            
            with lock:
                if shock_type == 'news_positive':
                    active_shocks['news'] += 0.035
                elif shock_type == 'news_negative':
                    active_shocks['news'] -= 0.035
                elif shock_type == 'volatility_spike':
                    active_shocks['volatility'] += 2.2
                elif shock_type == 'trend_bull':
                    active_shocks['trend'] += 0.006
                elif shock_type == 'trend_bear':
                    active_shocks['trend'] -= 0.006
                else:
                    return jsonify({'error': f"Unknown shock parameter: {shock_type}"}), 400
                    
            logger.info(f"Market shock applied: {shock_type}")
            return jsonify({'status': 'applied', 'active_shocks': active_shocks})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/select-ticker', methods=['POST'])
    def select_ticker():
        """Switch current asset to either a real Yahoo Finance ticker or synthetic simulation"""
        global sample_data, active_symbol, baseline_price, market_state, price_history, active_shocks, baseline_volatility, baseline_trend
        try:
            payload = request.get_json() or {}
            symbol = payload.get('symbol', 'SYNTHETIC').strip().upper()
            
            if not symbol:
                return jsonify({'error': 'Symbol parameter is empty'}), 400
                
            logger.info(f"Request to select ticker received: {symbol}")
            
            with lock:
                if symbol == 'SYNTHETIC':
                    active_symbol = 'SYNTHETIC'
                    logger.info("Generating synthetic historical seed data...")
                    new_data = generate_synthetic_data(252)
                else:
                    logger.info(f"Downloading real yfinance historical data for {symbol}...")
                    loader = YahooFinanceLoader()
                    new_data = loader.load_symbol(symbol, period='1y')
                    active_symbol = symbol
                    
                # Train all predictors on the loaded historical data
                logger.info(f"Re-training forecasting models on new {active_symbol} data...")
                for name, pred in predictors.items():
                    try:
                        pred.train(new_data[-126:])
                        logger.info(f"Model '{name}' re-trained successfully on {active_symbol}")
                    except Exception as e:
                        logger.error(f"Failed to re-train model '{name}' on {active_symbol}: {e}")
                        
                # Update global sample data
                sample_data = new_data
                
                # Re-align simulation parameters
                last_val = sample_data[-1]
                baseline_price = last_val.close
                baseline_volatility = last_val.volatility
                baseline_trend = last_val.momentum
                market_state['price'] = last_val.close
                market_state['volatility'] = last_val.volatility
                market_state['trend'] = last_val.momentum
                market_state['regime'] = 'Stable'
                market_state['last_update'] = datetime.now()
                
                # Reset buffers and active shocks
                price_history.clear()
                active_shocks = {'news': 0.0, 'volatility': 1.0, 'trend': 0.0}
                
                # Fill tick histories with trailing closes
                for i, data in enumerate(sample_data[-50:]):
                    price_history.append({
                        'timestamp': (datetime.now() - timedelta(seconds=(50-i))).strftime('%H:%M:%S'),
                        'price': round(data.close, 2),
                        'volatility': round(data.volatility, 4),
                        'trend': round(data.momentum, 4),
                        'regime': 'Stable'
                    })
                    
            logger.info(f"Successfully switched active ticker to {active_symbol}")
            return jsonify({
                'status': 'success',
                'active_symbol': active_symbol,
                'current_price': round(market_state['price'], 2)
            })
            
        except Exception as e:
            logger.error(f"Error switching active ticker: {e}")
            return jsonify({'error': f"Failed to switch to {symbol}: {str(e)}"}), 400
            
    @app.route('/api/reset', methods=['POST', 'GET'])
    def reset_simulation():
        """Reset simulator buffer, active shocks, and re-train baseline ML models"""
        global market_state, price_history, sample_data, active_shocks, active_symbol, baseline_price, baseline_volatility, baseline_trend
        try:
            with lock:
                if active_symbol == 'SYNTHETIC':
                    sample_data = generate_synthetic_data(252)
                else:
                    loader = YahooFinanceLoader()
                    sample_data = loader.load_symbol(active_symbol, period='1y')
                
                # Re-train models
                for name, pred in predictors.items():
                    try:
                        pred.train(sample_data[-126:])
                    except Exception as e:
                        logger.error(f"Re-train failed for '{name}': {e}")
                
                # Clear lists
                price_history.clear()
                active_shocks = {'news': 0.0, 'volatility': 1.0, 'trend': 0.0}
                
                # Re-establish parameters
                last_val = sample_data[-1]
                baseline_price = last_val.close
                baseline_volatility = last_val.volatility
                baseline_trend = last_val.momentum
                market_state = {
                    'price': last_val.close,
                    'volatility': last_val.volatility,
                    'trend': last_val.momentum,
                    'regime': 'Stable',
                    'last_update': datetime.now()
                }
                
                for i, data in enumerate(sample_data[-50:]):
                    price_history.append({
                        'timestamp': (datetime.now() - timedelta(seconds=(50-i))).strftime('%H:%M:%S'),
                        'price': round(data.close, 2),
                        'volatility': round(data.volatility, 4),
                        'trend': round(data.momentum, 4),
                        'regime': 'Stable'
                    })
                    
            logger.info("Market simulator state reset completed successfully")
            return jsonify({'status': 'success'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/backtest')
    def api_backtest():
        """Simulates high-precision model forecasts over historical slides to output rolling stats"""
        try:
            model_type = request.args.get('predictor_type', 'advanced').lower()
            if model_type not in predictors:
                model_type = 'advanced'
                
            predictor = predictors[model_type]
            historical_predictions = []
            
            with lock:
                test_data = sample_data[-60:]  # Take last 60 ticks
                
            for i in range(30, len(test_data)):
                historical_data = test_data[:i]
                latest_point = historical_data[-1]
                
                # Forecast
                prediction = predictor.predict(latest_point, historical_data[-30:])
                
                if i < len(test_data) - 1:
                    actual_return = ((test_data[i+1].close - test_data[i].close) / test_data[i].close) * 100.0
                    is_correct = (prediction.direction == 'UP') == (actual_return > 0)
                    
                    historical_predictions.append({
                        'date': test_data[i].timestamp.strftime('%H:%M:%S'),
                        'predicted_direction': prediction.direction,
                        'predicted_return': round(prediction.expected_return, 3),
                        'actual_return': round(actual_return, 3),
                        'confidence': round(prediction.confidence, 3),
                        'correct': bool(is_correct)
                    })
            return jsonify(historical_predictions)
            
        except Exception as e:
            logger.error(f"Backtest engine failed: {e}")
            return jsonify({'error': str(e)}), 500
            
    @app.route('/model-info')
    def model_info():
        """Provides dynamic engine calibrations and RAM/Speed benchmarks"""
        try:
            model_type = request.args.get('predictor_type', 'advanced').lower()
            if model_type not in predictors:
                model_type = 'advanced'
                
            predictor = predictors[model_type]
            info = predictor.get_model_info()
            
            # Fetch RAM details using psutil dynamically
            memory_usage_mb = 42.0
            try:
                import psutil
                process = psutil.Process(os.getpid())
                memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            except Exception:
                pass
                
            info.update({
                'system_telemetry': {
                    'active_symbol': active_symbol,
                    'memory_usage_mb': round(memory_usage_mb, 2),
                    'sample_buffer_size': len(sample_data),
                    'simulator_status': 'running',
                    'active_shocks': active_shocks
                }
            })
            return jsonify(info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/favicon.ico')
    def favicon():
        """Handle favicon requests cleanly"""
        from flask import send_from_directory
        try:
            return send_from_directory(app.static_folder, 'favicon.ico')
        except:
            return '', 204
            
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Page not found'), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='Internal system error'), 500
        
    return app

if __name__ == '__main__':
    app = create_main_app()
    app.run(
        host=settings.web.host,
        port=settings.web.port,
        debug=settings.web.debug
    )