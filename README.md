# EpochAI - Multi-Modal Financial Forecasting Engine

EpochAI is a sophisticated, modular financial forecasting system that combines multiple machine learning models with advanced features like hyperparameter optimization, technical indicators, risk analytics, and regime detection.

## 🏗️ Modular Architecture

The project has been completely restructured into a modular architecture for better maintainability, reusability, and scalability:

```
EpochAI/
├── main.py                     # Main entry point
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies (for web UI)
├── config/                    # Configuration management
│   ├── settings.py            # Application settings
│   └── logging_config.py      # Logging configuration
├── core/                      # Core data structures and interfaces
│   ├── data_models.py         # MarketData, PredictionResult classes
│   ├── base_predictor.py      # Base predictor interface
│   └── exceptions.py          # Custom exceptions
├── predictors/                # Prediction models
│   ├── cost_predictor.py      # Advanced cost predictor
│   ├── optimized_predictor.py # Optimized version
│   ├── ultimate_predictor.py  # Ultimate performance version
│   └── ensemble_predictor.py  # Ensemble methods
├── models/                    # Machine learning models
│   ├── ensemble_model.py      # Multi-model ensemble
│   ├── xgboost_model.py       # XGBoost implementation
│   ├── random_forest_model.py # Random Forest implementation
│   └── lstm_model.py          # LSTM implementation
├── features/                  # Feature extraction and engineering
│   ├── extractors.py          # Feature extraction classes
│   ├── engineering.py         # Feature engineering utilities
│   └── technical_indicators.py # Technical analysis indicators
├── risk/                      # Risk management
│   ├── managers.py            # Risk management classes
│   ├── metrics.py             # Risk metric calculations
│   └── regime_detection.py    # Market regime detection
├── data/                      # Data handling
│   ├── generators.py          # Synthetic data generation
│   ├── loaders.py             # Data loading utilities
│   └── processors.py          # Data processing utilities
├── web/                       # Web applications
│   ├── apps/                  # Flask applications
│   │   ├── main_app.py        # Main dashboard
│   │   ├── realtime_app.py    # Real-time dashboard
│   │   └── simple_app.py      # Simple dashboard
│   ├── templates/             # HTML templates
│   ├── static/                # Static assets (CSS, JS)
│   └── api/                   # API routes and serializers
├── utils/                     # Utility functions
│   ├── performance.py         # Performance monitoring
│   ├── validation.py          # Data validation
│   └── helpers.py             # General helpers
├── scripts/                   # Entry point scripts
│   ├── run_prediction.py      # Run predictions
│   ├── run_web_app.py         # Start web applications
│   └── benchmark.py           # Performance benchmarking
├── tests/                     # Unit and integration tests
└── docs/                      # Documentation
```

## 🎯 Features

### Prediction Models
- **Advanced Cost Predictor**: Comprehensive model with full feature set
- **Optimized Cost Predictor**: Performance-optimized for real-time use
- **Ultimate Cost Predictor**: Maximum performance with minimal latency
- **Ensemble Methods**: Combine multiple models for better accuracy

### Machine Learning Models
- **XGBoost**: Gradient boosting for continuous return prediction
- **Random Forest**: Direction classification with confidence scoring
- **LSTM**: Sequence-based learning for quantile forecasts
- **Hidden Markov Model**: Market regime detection
- **GARCH**: Volatility forecasting

### Risk Management
- **Value at Risk (VaR)**: 95% confidence risk estimates
- **Conditional VaR (CVaR)**: Tail risk assessment
- **Maximum Drawdown**: Worst-case scenario analysis
- **Regime Detection**: Market state identification
- **Position Sizing**: Kelly Criterion optimization

### Technical Analysis
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility-based bands
- **Moving Averages**: Simple and exponential
- **ATR**: Average True Range

### Web Applications
- **Main Dashboard**: Comprehensive prediction interface
- **Real-time Dashboard**: Live market simulation
- **Simple Dashboard**: Streamlined interface
- **API Endpoints**: RESTful API for integration

### Performance Features
- **Modular Architecture**: Easy to extend and maintain
- **Configurable Settings**: Environment-based configuration
- **Comprehensive Logging**: Structured logging with levels
- **Performance Monitoring**: Built-in benchmarking tools
- **Data Validation**: Input validation and error handling

## Models

### XGBoost Model
- Predicts continuous returns using gradient boosting
- Optimized with hyperparameter tuning

### Random Forest Model
- Classifies market direction (UP/DOWN) with confidence scoring
- Handles direction prediction with confidence scoring

### LSTM Model
- Provides quantile forecasts for uncertainty estimation
- Uses sequence-based learning

### Hidden Markov Model (HMM)
- Detects market regimes based on volatility and returns
- Identifies 6 different market states

### GARCH Model
- Forecasts volatility using GARCH(1,1) methodology
- Provides time-varying volatility estimates

## 🚀 Quick Start

### 1. Basic Usage

Run a prediction demonstration:
```bash
python main.py demo
```

Start the web dashboard:
```bash
python main.py web
```

Show system information:
```bash
python main.py info
```

### 2. Advanced Usage

Run specific predictors:
```bash
# Basic predictor
python scripts/run_prediction.py --predictor basic --predictions 5

# Optimized predictor with benchmark
python scripts/run_prediction.py --predictor optimized --benchmark

# Ultimate performance predictor
python scripts/run_prediction.py --predictor ultimate --data-points 500
```

Start specific web applications:
```bash
# Main dashboard
python scripts/run_web_app.py --app main --port 5000

# Real-time dashboard
python scripts/run_web_app.py --app realtime --port 5001

# Simple dashboard
python scripts/run_web_app.py --app simple --port 5002
```

### 3. Programmatic Usage

```python
from predictors.cost_predictor import AdvancedCostPredictor
from data.generators import generate_synthetic_data

# Generate data
data = generate_synthetic_data(252)  # 1 year of data

# Initialize and train predictor
predictor = AdvancedCostPredictor()
predictor.train(data)

# Make prediction
current_data = data[-1]
prediction = predictor.predict(current_data, data)

print(f"Direction: {prediction.direction}")
print(f"Expected Return: {prediction.expected_return:.3f}%")
print(f"Confidence: {prediction.confidence:.3f}")
```

## 📊 Example Output

```
🚀 EpochAI - Financial Forecasting Engine
==================================================
📊 Generating synthetic market data...
✅ Generated 252 data points
🤖 Initializing Advanced Cost Predictor...
🏋️ Training model...
✅ Model trained in 1.23 seconds

🎯 Making sample predictions:
--------------------------------------------------

Prediction 1:
   Direction: UP
   Expected Return: 0.540%
   Confidence: 0.679
   Regime: STABLE
   Risk VaR95: 1.094%

Prediction 2:
   Direction: DOWN
   Expected Return: -0.234%
   Confidence: 0.721
   Regime: BULLISH
   Risk VaR95: 0.876%

Prediction 3:
   Direction: UP
   Expected Return: 0.312%
   Confidence: 0.654
   Regime: HIGH_VOLATILITY
   Risk VaR95: 1.245%

✅ Demonstration completed successfully!
```

## 🔧 Configuration

EpochAI uses a modular configuration system. Settings can be customized in `config/settings.py` or via environment variables:

### Environment Variables
```bash
# Web application settings
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=false
export SECRET_KEY=your-secret-key

# Application settings
export ENVIRONMENT=production
export LOG_LEVEL=INFO
```

### Configuration Classes
- `ModelConfig`: Model training and prediction settings
- `WebConfig`: Web application settings
- `DataConfig`: Data handling configuration
- `RiskConfig`: Risk management parameters

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test categories:
```bash
# Test predictors
python -m pytest tests/test_predictors.py

# Test models
python -m pytest tests/test_models.py

# Test web applications
python -m pytest tests/test_web.py
```

## 📈 Performance

The modular architecture provides different performance tiers:

- **Basic Predictor**: ~50ms per prediction, full feature set
- **Optimized Predictor**: ~20ms per prediction, optimized algorithms
- **Ultimate Predictor**: ~5ms per prediction, maximum performance

Benchmark your system:
```bash
python scripts/run_prediction.py --benchmark
```

## Important Note

This system is designed for demonstration using synthetic data. Do not use for real trading without proper validation and risk management.

## 📦 Dependencies

### Python Dependencies
- Python 3.7+
- NumPy >= 1.21.0
- Pandas >= 1.3.0
- Scikit-learn >= 1.0.0
- Flask (for web applications)
- Optuna >= 3.0.0 (for hyperparameter optimization)
- SciPy >= 1.7.0

### Optional Dependencies
- TensorFlow/Keras (for LSTM models)
- XGBoost (with fallback to GradientBoosting)
- Plotly (for advanced visualizations)

Install all dependencies:
```bash
pip install -r requirements.txt
```

### Node.js Dependencies (for web UI)
```bash
npm install
```

## 🏛️ Architecture Benefits

### Modularity
- **Separation of Concerns**: Each module has a specific responsibility
- **Reusability**: Components can be easily imported and reused
- **Maintainability**: Easy to locate and modify specific functionality

### Scalability
- **Easy Extension**: Add new predictors, models, or web apps easily
- **Performance Tiers**: Choose the right performance level for your needs
- **Configuration Management**: Environment-specific settings

### Reliability
- **Error Handling**: Comprehensive exception handling
- **Data Validation**: Input validation at multiple levels
- **Logging**: Structured logging for debugging and monitoring

### Testing
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Performance Tests**: Benchmark system performance
