"""
Simple Flask web application for EpochAI
"""

from flask import Flask, render_template, jsonify
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data.generators import generate_synthetic_data
from predictors.cost_predictor import AdvancedCostPredictor
from core.data_models import FeatureVector
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('web.simple')


def create_simple_app():
    """Create and configure the simple Flask application"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure app
    app.config['SECRET_KEY'] = settings.web.secret_key
    app.config['DEBUG'] = settings.web.debug
    
    # Initialize with minimal data for simplicity
    logger.info("Initializing simple prediction model...")
    predictor = AdvancedCostPredictor()
    sample_data = generate_synthetic_data(100)  # Smaller dataset for simplicity
    
    try:
        predictor.train(sample_data[-50:])  # Train on last 50 points
        logger.info("Simple model initialized successfully")
    except Exception as e:
        logger.error(f"Simple model initialization failed: {e}")
        predictor = None
    
    @app.route('/')
    def index():
        """Simple dashboard page"""
        return render_template('simple_dashboard.html')
    
    @app.route('/api/simple-prediction')
    def simple_prediction():
        """Get a simple prediction"""
        try:
            if predictor is None:
                return jsonify({'error': 'Model not initialized'}), 500
            
            # Use latest data point
            latest_data = sample_data[-1]
            
            # Make prediction
            prediction = predictor.predict(latest_data, sample_data[-20:])
            
            # Return simplified response
            response = {
                'direction': prediction.direction,
                'expected_return': round(prediction.expected_return, 2),
                'confidence': round(prediction.confidence * 100, 1),  # Convert to percentage
                'regime': prediction.regime,
                'risk_level': 'Low' if prediction.risk_metrics['var95'] < 1.5 else 'Medium' if prediction.risk_metrics['var95'] < 3.0 else 'High',
                'timestamp': latest_data.timestamp.isoformat()
            }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Simple prediction failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/market-summary')
    def market_summary():
        """Get simple market summary"""
        try:
            if not sample_data:
                return jsonify({'error': 'No market data available'}), 500
            
            # Calculate simple statistics
            recent_data = sample_data[-10:]  # Last 10 points
            prices = [d.close for d in recent_data]
            
            current_price = prices[-1]
            price_change = ((current_price - prices[0]) / prices[0]) * 100
            avg_price = sum(prices) / len(prices)
            
            # Simple volatility estimate
            price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volatility = (sum([abs(change) for change in price_changes]) / len(price_changes)) * 100
            
            summary = {
                'current_price': round(current_price, 2),
                'price_change_pct': round(price_change, 2),
                'average_price': round(avg_price, 2),
                'volatility_pct': round(volatility, 2),
                'trend': 'Up' if price_change > 0 else 'Down' if price_change < 0 else 'Flat',
                'market_status': 'Active',
                'last_update': recent_data[-1].timestamp.isoformat()
            }
            
            return jsonify(summary)
            
        except Exception as e:
            logger.error(f"Market summary failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/price-history')
    def price_history():
        """Get simple price history"""
        try:
            if not sample_data:
                return jsonify({'error': 'No market data available'}), 500
            
            # Return last 20 data points
            recent_data = sample_data[-20:]
            history = [
                {
                    'date': d.timestamp.strftime('%Y-%m-%d'),
                    'price': round(d.close, 2)
                }
                for d in recent_data
            ]
            
            return jsonify(history)
            
        except Exception as e:
            logger.error(f"Price history failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/model-status')
    def model_status():
        """Get simple model status"""
        try:
            if predictor is None:
                return jsonify({
                    'status': 'Not Available',
                    'trained': False,
                    'error': 'Model not initialized'
                })
            
            info = predictor.get_model_info()
            return jsonify({
                'status': 'Ready' if info['is_trained'] else 'Not Trained',
                'trained': bool(info['is_trained']),  # Ensure boolean
                'model_type': info.get('type', 'Unknown'),
                'data_points': len(sample_data)
            })
            
        except Exception as e:
            logger.error(f"Model status request failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/favicon.ico')
    def favicon():
        """Handle favicon requests"""
        return '', 204  # No content
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_simple_app()
    app.run(
        host=settings.web.host,
        port=settings.web.port,
        debug=settings.web.debug
    )