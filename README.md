# ModelQ - Multi-Modal Financial Forecasting Engine

ModelQ is a sophisticated financial forecasting system that combines multiple machine learning models with advanced features like hyperparameter optimization, technical indicators, risk analytics, and regime detection.

## Project Structure

```
modelQ/
├── main.py                 # Main entry point
├── quick_test.py          # Quick model test
├── improved_test.py       # Improved model test
├── .gitignore            # Git ignore file
├── README.md             # This file
└── src/                  # Source code directory
    ├── models/           # Machine learning models
    │   ├── __init__.py
    │   ├── ensemble_model.py     # Main ensemble forecaster
    │   ├── xgboost_model.py      # XGBoost return forecaster
    │   ├── random_forest_model.py # Random Forest direction classifier
    │   ├── lstm_model.py         # LSTM quantile forecaster
    │   ├── hmm_model.py          # Hidden Markov Model for regime detection
    │   └── garch_model.py        # GARCH volatility forecaster
    ├── utils/            # Utility functions
    │   ├── __init__.py
    │   ├── data_generator.py     # Synthetic data generation
    │   ├── feature_engineering.py # Feature engineering utilities
    │   └── hyperparameter_optimizer.py # Hyperparameter optimization
    └── core/             # Core functionality
        ├── __init__.py
        └── backtesting.py        # Backtesting framework
```

## Features

- **Multi-Model Ensemble**: Combines XGBoost, Random Forest, LSTM, HMM, and GARCH models
- **Hyperparameter Optimization**: Uses Optuna for automated parameter tuning
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, ATR
- **Risk Analytics**: Value at Risk (VaR), Conditional VaR (CVaR), Max Drawdown
- **Regime Detection**: Identifies market states (Stable, Volatile, Recovery, Growth)
- **Position Sizing**: Kelly Criterion for optimal bet sizing
- **Explainability**: Provides insights into model predictions

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

## Usage

### Quick Test
```bash
python quick_test.py
```

### Improved Test
```bash
python improved_test.py
```

### Full Model Run
```bash
python main.py
```

## Results Example

```
🎯 Prediction Results:
   Direction: UP
   Expected Return: 0.540%
   Confidence: 0.679
   Quantiles - P10: -1.094%, P50: 0.149%, P90: 0.862%
   Regime: Recovery
   Risk Metrics: VAR95=1.094%, MaxDD=-15.000%

📊 Backtest Results:
   Total Return: 0.24%
   Annualized Return: 0.12%
   Sharpe Ratio: 0.182
   Max Drawdown: -0.94%
   Hit Rate: 0.480
   Win Rate: 0.515
```

## Risk Management

The system incorporates comprehensive risk management including:
- Value at Risk (VaR) calculations
- Conditional Value at Risk (CVaR)
- Maximum Drawdown estimation
- Tail risk scoring
- Volatility forecasting

## Important Note

This system is designed for demonstration using synthetic data. Do not use for real trading without proper validation and risk management.

## Dependencies

- Python 3.7+
- NumPy
- Pandas
- Scikit-learn
- XGBoost (optional, with fallback)
- Optuna
- TensorFlow/Keras (for LSTM)