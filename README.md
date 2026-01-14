# EpochAI - Multi-Modal Financial Forecasting Engine

Advanced AI-powered financial forecasting system with hyperparameter optimization and explainable AI.

## Features

- **Multi-Modal Forecasting**: Combines XGBoost, Random Forest, LSTM, HMM, and GARCH models
- **Hyperparameter Optimization**: Uses Optuna for advanced hyperparameter tuning
- **Realistic Data Generation**: Creates synthetic market data with 6 market regimes
- **Risk Analytics**: Calculates VaR, CVaR, max drawdown, and tail risk metrics
- **Explainable AI**: SHAP-like feature importance and regime detection
- **Backtesting**: Walk-forward validation with realistic position sizing

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

```python
from financial_model import generate_synthetic_data, EnsembleForecaster

# Generate synthetic market data (3 years)
data = generate_synthetic_data(756)

# Create ensemble forecaster with hyperparameter optimization
ensemble = EnsembleForecaster(optimize_hyperparams=True)

# Train models
train_data = data[-252:]  # Use 1 year of data
ensemble.xgboost.train(train_data)
ensemble.random_forest.train(train_data)
ensemble.lstm.train(train_data)

# Make prediction
latest_features = ensemble._extract_features(data, len(data)-1)
prediction = ensemble.predict(latest_features, data[-50:])

print(f"Direction: {prediction.direction}")
print(f"Expected Return: {prediction.expected_return:.3f}%")
print(f"Confidence: {prediction.confidence:.3f}")
```

### Backtesting

```python
from financial_model import Backtester

# Run walk-forward backtest
backtester = Backtester(optimize_hyperparams=True)
results = backtester.run_walk_forward(data, 200, 20)

print(f"Total Return: {results.total_return:.2f}%")
print(f"Sharpe Ratio: {results.sharpe_ratio:.3f}")
print(f"Max Drawdown: {results.max_drawdown:.2f}%")
print(f"Hit Rate: {results.hit_rate:.3f}")
```

## Model Architecture

### 1. Return Forecaster (XGBoost)
- Uses Gradient Boosting with hyperparameter optimization via Optuna
- Features: volatility, momentum, RSI, MACD, Bollinger Bands, volume indicators
- Optimizes: n_estimators, max_depth, learning_rate, subsample, reg_alpha, reg_lambda

### 2. Direction Classifier (Random Forest)
- Binary classification for up/down prediction
- Optimizes: n_estimators, max_depth, min_samples_split, min_samples_leaf

### 3. Quantile Forecaster (LSTM-inspired)
- Provides P10, P50, P90 return forecasts
- Uses sequence-based features for multi-day predictions

### 4. Regime Detector (HMM)
- Identifies 6 market regimes: Low Vol Bull, High Vol Bull, Consolidation, Bear, Crisis, Recovery
- Uses multivariate Gaussian emissions with regime-specific parameters

### 5. Volatility Forecaster (GARCH)
- GARCH(1,1) model with optimized parameters
- Forecasts volatility for risk-adjusted position sizing

## Hyperparameter Optimization

The system uses Optuna for advanced hyperparameter optimization:

- **XGBoost**: Optimizes tree depth, learning rate, regularization parameters
- **Random Forest**: Optimizes ensemble size, tree depth, sample splits
- **GARCH**: Optimizes omega, alpha, beta parameters for volatility modeling

## Risk Metrics

- **Value at Risk (VaR 95%)**: Maximum expected loss with 95% confidence
- **Conditional Value at Risk (CVaR 95%)**: Expected loss beyond VaR threshold
- **Max Drawdown**: Largest peak-to-trough decline
- **Tail Risk Score**: Probability of >3% loss
- **Sharpe Ratio**: Risk-adjusted return metric

## Performance Targets

- Directional accuracy: 65-70%
- Regime detection: 85%+ accuracy
- Sharpe ratio: >1.5 in backtests
- Max drawdown: <15% in backtests
- Information coefficient: >0.6

## Data Generation

The system generates realistic synthetic market data with:

- 6 market regimes with different statistical properties
- Regime-switching dynamics with Markov transitions
- Volatility clustering and fat-tailed distributions
- Autocorrelation in returns (AR(1) = 0.05)
- Realistic technical indicators

## Note

This system is designed for demonstration using synthetic data and should not be used for real trading without proper validation and risk management.
