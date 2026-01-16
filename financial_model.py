import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, roc_auc_score
from scipy.stats import randint, uniform
import optuna
from optuna.integration import OptunaSearchCV
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MarketData:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    returns: float = 0.0
    realized_vol_20d: float = 0.0
    momentum_5d: float = 0.0
    vix_zscore: float = 0.0

@dataclass
class FeatureVector:
    realized_vol_20d: float
    momentum_5d: float
    vix_zscore: float
    sma_20: float
    sma_50: float
    rsi: float
    macd: float
    bb_position: float

@dataclass
class ForecastOutput:
    direction: str
    expected_return: float
    confidence: float
    quantiles: Dict[str, float]
    regime: Dict[str, Any]
    risk_metrics: Dict[str, float]
    explainability: List[str]

@dataclass
class RiskMetrics:
    var95: float
    cvar95: float
    max_drawdown: float
    tail_risk_score: float
    volatility_forecast: float

@dataclass
class BacktestResults:
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    hit_rate: float
    information_coefficient: float
    volatility: float
    trades: int
    win_rate: float
    profit_factor: float

class HyperparameterOptimizer:
    """Advanced hyperparameter optimization using Optuna"""
    
    def __init__(self):
        self.study = None
    
    def optimize_xgboost(self, X_train, y_train, X_val, y_val):
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
                'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 1.0),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10)
            }
            
            model = GradientBoostingRegressor(**params, random_state=42)
            model.fit(X_train, y_train)
            pred = model.predict(X_val)
            mse = mean_squared_error(y_val, pred)
            return mse
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=100)
        return study.best_params
    
    def optimize_random_forest(self, X_train, y_train, X_val, y_val):
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 5, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'bootstrap': trial.suggest_categorical('bootstrap', [True, False])
            }
            
            model = RandomForestClassifier(**params, random_state=42)
            model.fit(X_train, y_train)
            pred = model.predict(X_val)
            accuracy = accuracy_score(y_val, pred)
            return -accuracy  # Minimize negative accuracy (maximize accuracy)
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=100)
        return study.best_params

class ReturnForecaster:
    def __init__(self, optimize_hyperparams=True):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.optimize_hyperparams = optimize_hyperparams
        self.optimizer = HyperparameterOptimizer()
        self.best_params = None
    
    def prepare_features(self, data: List[MarketData]):
        """Prepare features from market data"""
        features = []
        targets = []
        
        for i in range(len(data) - 1):
            # Create feature vector from current data point
            feat = [
                data[i].realized_vol_20d,
                data[i].momentum_5d,
                data[i].vix_zscore,
                data[i].close,  # Price level
                data[i].volume,  # Volume
                self.calculate_sma(data, i, 20),
                self.calculate_sma(data, i, 50),
                self.calculate_rsi(data, i, 14),
                self.calculate_macd(data, i),
                self.calculate_bb_position(data, i, 20),
                self.calculate_atr(data, i, 14),
                self.calculate_volume_ratio(data, i, 20)
            ]
            
            # Target is next period return
            target = data[i + 1].returns
            
            features.append(feat)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def calculate_sma(self, data: List[MarketData], index: int, period: int) -> float:
        start = max(0, index - period + 1)
        prices = [d.close for d in data[start:index+1]]
        return sum(prices) / len(prices) if prices else 0
    
    def calculate_rsi(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 50  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(max(0, index - period + 1), index + 1):
            if i == 0:
                continue
            
            change = data[i].close - data[i-1].close
            
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return 50
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, data: List[MarketData], index: int) -> float:
        if index < 26:
            return 0
        
        ema12 = self.calculate_ema(data, index, 12)
        ema26 = self.calculate_ema(data, index, 26)
        
        return ema12 - ema26
    
    def calculate_ema(self, data: List[MarketData], index: int, period: int) -> float:
        multiplier = 2 / (period + 1)
        ema = data[max(0, index - period)].close  # Starting value
        
        for i in range(max(0, index - period) + 1, index + 1):
            ema = (data[i].close - ema) * multiplier + ema
        
        return ema
    
    def calculate_bb_position(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 0.5  # Middle of bands
        
        sma = self.calculate_sma(data, index, period)
        prices = [d.close for d in data[max(0, index - period + 1):index + 1]]
        price_std = np.std(prices)
        
        upper_band = sma + (2 * price_std)
        lower_band = sma - (2 * price_std)
        
        if upper_band == lower_band:
            return 0.5  # Avoid division by zero
        
        return (data[index].close - lower_band) / (upper_band - lower_band)
    
    def calculate_atr(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 0.01  # Default small value
        
        tr_values = []
        for i in range(max(0, index - period + 1), index + 1):
            high = data[i].high
            low = data[i].low
            prev_close = data[i-1].close if i > 0 else data[i].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)
        
        return sum(tr_values) / len(tr_values)
    
    def calculate_volume_ratio(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 1.0  # Default ratio
        
        current_vol = data[index].volume
        avg_vol = sum([d.volume for d in data[max(0, index - period + 1):index + 1]]) / period
        
        return current_vol / avg_vol if avg_vol > 0 else 1.0
    
    def train(self, data: List[MarketData]):
        if len(data) < 50:  # Need minimum data points
            raise ValueError("Insufficient data for training")
        
        # Prepare features and targets
        X, y = self.prepare_features(data)
        
        if len(X) == 0 or len(y) == 0:
            raise ValueError("No features or targets generated")
        
        # Split data for hyperparameter optimization
        split_idx = int(0.8 * len(X))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        if self.optimize_hyperparams and len(X_val) > 0:
            # Optimize hyperparameters
            best_params = self.optimizer.optimize_xgboost(X_train_scaled, y_train, X_val_scaled, y_val)
            self.best_params = best_params
            self.model = GradientBoostingRegressor(**best_params, random_state=42)
        else:
            # Use default parameters
            self.model = GradientBoostingRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        
        # Final training on all data
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, features: FeatureVector) -> float:
        if not self.is_trained:
            # Return a neutral prediction if not trained
            return 0.001
        
        # Prepare feature vector for prediction
        feat_array = np.array([
            features.realized_vol_20d,
            features.momentum_5d,
            features.vix_zscore,
            features.sma_20,  # Using SMA as proxy for price level
            1000000,  # Using average volume as proxy
            features.sma_20,
            features.sma_50,
            features.rsi,
            features.macd,
            features.bb_position,
            0.01,  # ATR placeholder
            1.0    # Volume ratio placeholder
        ]).reshape(1, -1)
        
        # Scale the features
        feat_scaled = self.scaler.transform(feat_array)
        
        # Make prediction
        prediction = self.model.predict(feat_scaled)[0]
        return float(prediction)

class DirectionClassifier:
    def __init__(self, optimize_hyperparams=True):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.optimize_hyperparams = optimize_hyperparams
        self.optimizer = HyperparameterOptimizer()
        self.best_params = None
    
    def prepare_features(self, data: List[MarketData]):
        """Prepare features for direction classification"""
        features = []
        targets = []
        
        for i in range(len(data) - 1):
            # Create feature vector from current data point
            feat = [
                data[i].realized_vol_20d,
                data[i].momentum_5d,
                data[i].vix_zscore,
                data[i].rsi,
                data[i].macd,
                data[i].bb_position,
                data[i].close,
                data[i].volume,
                self.calculate_sma(data, i, 20),
                self.calculate_atr(data, i, 14),
                self.calculate_volume_ratio(data, i, 20)
            ]
            
            # Target is direction (1 for up, 0 for down)
            target = 1 if data[i + 1].returns > 0 else 0
            
            features.append(feat)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def calculate_sma(self, data: List[MarketData], index: int, period: int) -> float:
        start = max(0, index - period + 1)
        prices = [d.close for d in data[start:index+1]]
        return sum(prices) / len(prices) if prices else 0
    
    def calculate_macd(self, data: List[MarketData], index: int) -> float:
        if index < 26:
            return 0
        
        ema12 = self.calculate_ema(data, index, 12)
        ema26 = self.calculate_ema(data, index, 26)
        
        return ema12 - ema26
    
    def calculate_ema(self, data: List[MarketData], index: int, period: int) -> float:
        multiplier = 2 / (period + 1)
        ema = data[max(0, index - period)].close  # Starting value
        
        for i in range(max(0, index - period) + 1, index + 1):
            ema = (data[i].close - ema) * multiplier + ema
        
        return ema
    
    def calculate_atr(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 0.01  # Default small value
        
        tr_values = []
        for i in range(max(0, index - period + 1), index + 1):
            high = data[i].high
            low = data[i].low
            prev_close = data[i-1].close if i > 0 else data[i].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)
        
        return sum(tr_values) / len(tr_values)
    
    def calculate_volume_ratio(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 1.0  # Default ratio
        
        current_vol = data[index].volume
        avg_vol = sum([d.volume for d in data[max(0, index - period + 1):index + 1]]) / period
        
        return current_vol / avg_vol if avg_vol > 0 else 1.0
    
    def train(self, data: List[MarketData]):
        if len(data) < 50:  # Need minimum data points
            raise ValueError("Insufficient data for training")
        
        # Prepare features and targets
        X, y = self.prepare_features(data)
        
        if len(X) == 0 or len(y) == 0:
            raise ValueError("No features or targets generated")
        
        # Split data for hyperparameter optimization
        split_idx = int(0.8 * len(X))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        if self.optimize_hyperparams and len(X_val) > 0:
            # Optimize hyperparameters
            best_params = self.optimizer.optimize_random_forest(X_train_scaled, y_train, X_val_scaled, y_val)
            self.best_params = best_params
            self.model = RandomForestClassifier(**best_params, random_state=42)
        else:
            # Use default parameters
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                random_state=42
            )
        
        # Final training on all data
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, features: FeatureVector) -> Tuple[int, float]:
        if not self.is_trained:
            # Return neutral prediction if not trained
            return 1, 0.6  # Default to UP with 60% confidence
        
        # Prepare feature vector for prediction
        feat_array = np.array([
            features.realized_vol_20d,
            features.momentum_5d,
            features.vix_zscore,
            features.rsi,
            features.macd,
            features.bb_position,
            features.sma_20,
            1000000,  # Volume placeholder
            features.sma_20,
            0.01,     # ATR placeholder
            1.0       # Volume ratio placeholder
        ]).reshape(1, -1)
        
        # Scale the features
        feat_scaled = self.scaler.transform(feat_array)
        
        # Make prediction
        direction = int(self.model.predict(feat_scaled)[0])
        confidence = float(np.max(self.model.predict_proba(feat_scaled)[0]))
        
        return direction, confidence

class LSTMForecaster:
    """Placeholder for LSTM model - would require TensorFlow/Keras in real implementation"""
    def __init__(self):
        # In a real implementation, this would use TensorFlow/Keras
        # For this example, we'll simulate LSTM behavior with optimized random forest
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_sequences(self, data: List[MarketData], seq_length: int = 30):
        """Prepare sequences for LSTM-like forecasting"""
        X, y_p10, y_p50, y_p90 = [], [], [], []
        
        for i in range(seq_length, len(data)):
            # Take the last seq_length days of features
            sequence = []
            for j in range(i - seq_length, i):
                sequence.extend([
                    data[j].close,
                    data[j].returns,
                    data[j].realized_vol_20d,
                    data[j].momentum_5d,
                    data[j].vix_zscore
                ])
            
            X.append(sequence)
            
            # Targets: future quantiles (simplified)
            future_returns = [data[k].returns for k in range(i, min(i+5, len(data)))]
            if future_returns:
                sorted_returns = sorted(future_returns)
                y_p10.append(sorted_returns[0] if len(sorted_returns) > 0 else 0)
                y_p50.append(sorted_returns[len(sorted_returns)//2] if len(sorted_returns) > 0 else 0)
                y_p90.append(sorted_returns[-1] if len(sorted_returns) > 0 else 0)
            else:
                y_p10.append(0)
                y_p50.append(0)
                y_p90.append(0)
        
        return np.array(X), np.array(y_p10), np.array(y_p50), np.array(y_p90)
    
    def train(self, data: List[MarketData]):
        if len(data) < 50:  # Need minimum data points
            print("Insufficient data for LSTM training, using default model")
            return
        
        X, y_p10, y_p50, y_p90 = self.prepare_sequences(data)
        
        if len(X) == 0:
            print("No sequences prepared for LSTM training")
            return
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train separate models for each quantile
        self.model_p10 = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model_p50 = RandomForestRegressor(n_estimators=100, random_state=42) 
        self.model_p90 = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.model_p10.fit(X_scaled, y_p10)
        self.model_p50.fit(X_scaled, y_p50)
        self.model_p90.fit(X_scaled, y_p90)
        
        self.is_trained = True
    
    def predict(self, sequence: List[List[float]]) -> Dict[str, float]:
        if not self.is_trained:
            # Simulate LSTM predictions for quantiles
            return {
                'p10': -0.005,
                'p50': 0.001,
                'p90': 0.008
            }
        
        # Flatten the sequence to match training format
        flat_sequence = []
        for row in sequence[-30:]:  # Use last 30 days
            flat_sequence.extend(row[:5])  # Use first 5 features per day
        
        # Pad or truncate to fixed length
        while len(flat_sequence) < 30 * 5:  # 30 days * 5 features
            flat_sequence.append(0)
        flat_sequence = flat_sequence[:30 * 5]  # Ensure exactly 150 features
        
        # Reshape for prediction
        X_pred = np.array(flat_sequence).reshape(1, -1)
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # Predict each quantile
        p10 = self.model_p10.predict(X_pred_scaled)[0]
        p50 = self.model_p50.predict(X_pred_scaled)[0]
        p90 = self.model_p90.predict(X_pred_scaled)[0]
        
        return {
            'p10': float(p10),
            'p50': float(p50),
            'p90': float(p90)
        }

class RegimeDetector:
    def __init__(self):
        self.regimes = ['Low Vol Bull', 'High Vol Bull', 'Consolidation', 'Bear', 'Crisis', 'Recovery']
        self.emission_params = {
            'Low Vol Bull': {
                'volatility': {'mean': 0.15, 'std': 0.02},
                'returns': {'mean': 0.001, 'std': 0.01},
                'vix': {'mean': 15, 'std': 3}
            },
            'High Vol Bull': {
                'volatility': {'mean': 0.25, 'std': 0.05},
                'returns': {'mean': 0.0005, 'std': 0.015},
                'vix': {'mean': 20, 'std': 4}
            },
            'Consolidation': {
                'volatility': {'mean': 0.18, 'std': 0.03},
                'returns': {'mean': 0.0002, 'std': 0.008},
                'vix': {'mean': 18, 'std': 2}
            },
            'Bear': {
                'volatility': {'mean': 0.30, 'std': 0.08},
                'returns': {'mean': -0.001, 'std': 0.02},
                'vix': {'mean': 25, 'std': 5}
            },
            'Crisis': {
                'volatility': {'mean': 0.50, 'std': 0.15},
                'returns': {'mean': -0.005, 'std': 0.03},
                'vix': {'mean': 35, 'std': 10}
            },
            'Recovery': {
                'volatility': {'mean': 0.25, 'std': 0.06},
                'returns': {'mean': 0.002, 'std': 0.018},
                'vix': {'mean': 20, 'std': 6}
            }
        }
        
        # Transition matrix (simplified - in reality this would be learned)
        self.transition_matrix = np.array([
            [0.85, 0.05, 0.05, 0.03, 0.01, 0.01],  # Low Vol Bull
            [0.05, 0.80, 0.05, 0.05, 0.03, 0.02],  # High Vol Bull
            [0.05, 0.05, 0.80, 0.05, 0.03, 0.02],  # Consolidation
            [0.03, 0.05, 0.05, 0.80, 0.05, 0.02],  # Bear
            [0.01, 0.02, 0.02, 0.05, 0.85, 0.05],  # Crisis
            [0.02, 0.03, 0.03, 0.05, 0.02, 0.85]   # Recovery
        ])
    
    def detect(self, observation: Dict[str, float]) -> Dict[str, Any]:
        # Calculate emission probabilities for each regime
        probabilities = []
        
        for regime in self.regimes:
            prob = self._calculate_emission_prob(observation, regime)
            probabilities.append({'regime': regime, 'prob': prob})
        
        # Normalize probabilities
        total = sum(p['prob'] for p in probabilities)
        if total == 0:
            total = 1  # Avoid division by zero
        
        normalized = [{'regime': p['regime'], 'prob': p['prob'] / total} for p in probabilities]
        
        # Find most likely regime
        most_likely = max(normalized, key=lambda x: x['prob'])
        
        return {
            'regime': most_likely['regime'],
            'probabilities': {p['regime']: p['prob'] for p in normalized}
        }
    
    def _calculate_emission_prob(self, obs: Dict[str, float], regime: str) -> float:
        params = self.emission_params[regime]
        
        # Calculate multivariate Gaussian probability
        vol_prob = self._gaussian_pdf(obs['volatility'], params['volatility']['mean'], params['volatility']['std'])
        ret_prob = self._gaussian_pdf(obs['returns'], params['returns']['mean'], params['returns']['std'])
        vix_prob = self._gaussian_pdf(obs['vix'], params['vix']['mean'], params['vix']['std'])
        
        return vol_prob * ret_prob * vix_prob
    
    def _gaussian_pdf(self, x: float, mean: float, std: float) -> float:
        coefficient = 1 / (std * np.sqrt(2 * np.pi))
        exponent = -np.power(x - mean, 2) / (2 * np.power(std, 2))
        return float(coefficient * np.exp(exponent))

class VolatilityForecaster:
    def __init__(self):
        self.omega = 0.00001
        self.alpha = 0.1
        self.beta = 0.85
        self.optimized_params = False
    
    def optimize_garch_params(self, returns: List[float]):
        """Optimize GARCH parameters using maximum likelihood estimation"""
        if len(returns) < 10:
            return  # Not enough data to optimize
        
        # Simplified optimization - in reality would use proper MLE
        squared_returns = [r**2 for r in returns]
        mean_squared_return = np.mean(squared_returns)
        
        # Estimate parameters based on data characteristics
        self.omega = max(0.000001, min(0.001, mean_squared_return * 0.01))
        self.alpha = max(0.05, min(0.2, 0.1))
        self.beta = max(0.7, min(0.95, 1.0 - self.alpha - 0.01))
        self.optimized_params = True
    
    def train(self, returns: List[float]):
        if len(returns) < 2:
            return
        
        # Optimize parameters
        self.optimize_garch_params(returns)
    
    def forecast(self, returns: List[float], horizon: int) -> List[float]:
        if len(returns) == 0:
            return [0.2 * np.sqrt(252)] * horizon  # Default volatility forecast
        
        # Initialize variance with recent squared return
        if len(returns) > 0:
            # Use exponentially weighted moving average of squared returns
            weights = np.exp(np.linspace(-1., 0., min(50, len(returns))))
            weights /= weights.sum()
            recent_squared_returns = [r**2 for r in returns[-len(weights):]]
            current_variance = np.average(recent_squared_returns, weights=weights) if recent_squared_returns else 0.0004
        else:
            current_variance = 0.0004  # Default variance
        
        forecasts = []
        for h in range(horizon):
            # Forecast variance using GARCH equation
            forecast_variance = self.omega + self.alpha * current_variance + self.beta * current_variance
            forecasts.append(float(np.sqrt(forecast_variance) * np.sqrt(252)))  # Annualized
            current_variance = forecast_variance
        
        return forecasts

class EnsembleForecaster:
    def __init__(self, optimize_hyperparams=True):
        self.xgboost = ReturnForecaster(optimize_hyperparams=optimize_hyperparams)
        self.random_forest = DirectionClassifier(optimize_hyperparams=optimize_hyperparams)
        self.lstm = LSTMForecaster()
        self.hmm = RegimeDetector()
        self.garch = VolatilityForecaster()
    
    def predict(self, features: FeatureVector, historical_data: List[MarketData]) -> ForecastOutput:
        # 1. Get regime
        regime = self.hmm.detect({
            'volatility': features.realized_vol_20d,
            'returns': features.momentum_5d,
            'vix': features.vix_zscore
        })
        
        # 2. Direction & confidence
        direction, confidence = self.random_forest.predict(features)
        
        # 3. Expected return (XGBoost)
        base_return = self.xgboost.predict(features)
        
        # 4. Quantiles (LSTM)
        sequence = self._prepare_sequence(historical_data)
        quantiles = self.lstm.predict(sequence)
        
        # 5. Volatility forecast
        returns = [d.returns for d in historical_data if d.returns is not None]
        volatility_forecast = self.garch.forecast(returns, 5)
        
        # 6. Ensemble weighting based on regime
        regime_weights = self._get_regime_weights(regime['regime'])
        final_return = (
            regime_weights['xgboost'] * base_return +
            regime_weights['lstm'] * quantiles['p50'] +
            regime_weights['direction'] * (0.005 if direction == 1 else -0.005)
        )
        
        # 7. Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(quantiles, volatility_forecast[0])
        
        # 8. Generate explainability
        explainability = self._generate_explanations(features, regime['regime'])
        
        return ForecastOutput(
            direction='UP' if direction == 1 else 'DOWN',
            expected_return=final_return * 100,  # Convert to percentage
            confidence=confidence,
            quantiles={
                'p10': quantiles['p10'] * 100,
                'p50': quantiles['p50'] * 100,
                'p90': quantiles['p90'] * 100
            },
            regime={
                'current': regime['regime'],
                'probabilities': regime['probabilities']
            },
            risk_metrics=risk_metrics,
            explainability=explainability
        )
    
    def _prepare_sequence(self, historical_data: List[MarketData]) -> List[List[float]]:
        # Prepare sequence data for LSTM (simplified)
        sequence = []
        for d in historical_data[-30:]:  # Last 30 days
            sequence.append([
                d.close,
                d.returns or 0,
                d.realized_vol_20d or 0,
                d.momentum_5d or 0,
                d.vix_zscore or 0
            ])
        return sequence
    
    def _get_regime_weights(self, regime: str) -> Dict[str, float]:
        weights = {
            'Low Vol Bull': {'xgboost': 0.5, 'lstm': 0.3, 'direction': 0.2},
            'High Vol Bull': {'xgboost': 0.4, 'lstm': 0.4, 'direction': 0.2},
            'Bear': {'xgboost': 0.4, 'lstm': 0.3, 'direction': 0.3},
            'Crisis': {'xgboost': 0.3, 'lstm': 0.5, 'direction': 0.2},  # Higher weight to LSTM in crisis
            'Recovery': {'xgboost': 0.45, 'lstm': 0.35, 'direction': 0.2},
            'Consolidation': {'xgboost': 0.5, 'lstm': 0.3, 'direction': 0.2}
        }
        
        return weights.get(regime, weights['Consolidation'])
    
    def _calculate_risk_metrics(self, quantiles: Dict[str, float], volatility: float) -> Dict[str, float]:
        # VaR 95% (absolute value of 10th percentile)
        var95 = abs(quantiles['p10'])
        
        # CVaR 95% (expected shortfall beyond VaR)
        cvar95 = var95 * 1.2  # Simplified approximation
        
        # Max drawdown (estimated based on volatility and return)
        max_drawdown = min(-2, -abs(quantiles['p10']) * 150)  # Conservative estimate
        
        # Tail risk score (probability of >3% loss)
        # Assuming normal distribution between quantiles
        mean = quantiles['p50']
        std = (quantiles['p90'] - quantiles['p10']) / 2.56  # Approx from 90th-10th percentiles
        
        # Calculate probability of >3% loss
        z_score = (0.03 - abs(mean)) / std if std != 0 else 0
        tail_risk_score = max(0, min(1, 0.5 * (1 - self._erf(z_score / np.sqrt(2)))))
        
        return {
            'var95': var95 * 100,
            'cvar95': cvar95 * 100,
            'max_drawdown': max_drawdown,
            'tail_risk_score': tail_risk_score,
            'volatility_forecast': volatility
        }
    
    def _erf(self, x: float) -> float:
        # Approximation of error function
        sign = 1 if x >= 0 else -1
        x = abs(x)
        
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        t = 1 / (1 + p * x)
        y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
        
        return sign * y
    
    def _generate_explanations(self, features: FeatureVector, regime: str) -> List[str]:
        explanations = []
        
        if features.realized_vol_20d > 0.25:
            explanations.append("High volatility detected, indicating increased market uncertainty")
        elif features.realized_vol_20d < 0.15:
            explanations.append("Low volatility detected, suggesting stable market conditions")
        
        if features.momentum_5d > 0.03:
            explanations.append("Strong positive momentum observed, suggesting upward trend continuation")
        elif features.momentum_5d < -0.03:
            explanations.append("Strong negative momentum observed, suggesting downward trend continuation")
        
        if features.rsi > 70:
            explanations.append("RSI indicates overbought conditions, potential reversal downside")
        elif features.rsi < 30:
            explanations.append("RSI indicates oversold conditions, potential reversal upside")
        
        explanations.append(f"Current market regime: {regime}")
        
        return explanations

class Backtester:
    def __init__(self, optimize_hyperparams=True):
        self.ensemble = EnsembleForecaster(optimize_hyperparams=optimize_hyperparams)
    
    def run_walk_forward(
        self, 
        data: List[MarketData], 
        train_window: int, 
        test_window: int
    ) -> BacktestResults:
        results = []
        equity = [100000]  # Start with 100k
        
        for i in range(train_window, len(data) - test_window, test_window):
            # 1. Train on window
            train_data = data[i - train_window:i]
            self._train_models(train_data)
            
            # 2. Test on next period
            test_data = data[i:i + test_window]
            
            for j in range(len(test_data) - 1):
                features = self._extract_features(test_data, j)
                forecast = self.ensemble.predict(features, test_data[:j+1])
                
                actual_return = (test_data[j+1].close - test_data[j].close) / test_data[j].close
                
                # Calculate position size (Kelly criterion)
                position_size = self._calculate_position_size(
                    forecast.expected_return / 100,
                    forecast.confidence,
                    forecast.risk_metrics['volatility_forecast']
                )
                
                # Calculate PnL
                pnl = position_size * actual_return * equity[-1]
                equity.append(equity[-1] + pnl)
                
                results.append({
                    'date': test_data[j].date,
                    'forecast': forecast.expected_return,
                    'actual': actual_return * 100,
                    'direction': forecast.direction,
                    'correct': (forecast.direction == 'UP') == (actual_return > 0),
                    'pnl': pnl,
                    'equity': equity[-1]
                })
        
        return self._calculate_metrics(results, equity)
    
    def _train_models(self, data: List[MarketData]):
        # Train all models
        self.ensemble.xgboost.train(data)
        self.ensemble.random_forest.train(data)
        self.ensemble.lstm.train(data)
        
        # Train GARCH model separately
        returns = [d.returns for d in data if d.returns is not None]
        self.ensemble.garch.train(returns)
    
    def _extract_features(self, data: List[MarketData], index: int) -> FeatureVector:
        # Extract features for the given index
        current = data[index]
        
        # Calculate technical indicators
        sma_20 = sum([d.close for d in data[max(0, index-19):index+1]]) / min(20, index+1)
        sma_50 = sum([d.close for d in data[max(0, index-49):index+1]]) / min(50, index+1)
        
        # Calculate RSI (simplified)
        rsi = 50  # Default
        if index >= 14:
            gains = 0
            losses = 0
            for i in range(max(0, index-13), index+1):
                if i > 0:
                    change = data[i].close - data[i-1].close
                    if change > 0:
                        gains += change
                    else:
                        losses += abs(change)
            avg_gain = gains / 14
            avg_loss = losses / 14
            if avg_loss != 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        
        # Calculate MACD (simplified)
        ema12 = self._calculate_ema(data, index, 12)
        ema26 = self._calculate_ema(data, index, 26)
        macd = ema12 - ema26
        
        # Calculate Bollinger Band position
        bb_upper = sma_20 + (2 * np.std([d.close for d in data[max(0, index-19):index+1]]))
        bb_lower = sma_20 - (2 * np.std([d.close for d in data[max(0, index-19):index+1]]))
        bb_position = 0.5 if bb_upper == bb_lower else (current.close - bb_lower) / (bb_upper - bb_lower)
        
        return FeatureVector(
            realized_vol_20d=current.realized_vol_20d or 0.2,
            momentum_5d=current.momentum_5d or 0.01,
            vix_zscore=current.vix_zscore or 0,
            sma_20=sma_20,
            sma_50=sma_50,
            rsi=rsi,
            macd=macd,
            bb_position=bb_position
        )
    
    def _calculate_ema(self, data: List[MarketData], index: int, period: int) -> float:
        multiplier = 2 / (period + 1)
        ema = data[max(0, index - period)].close  # Starting value
        
        for i in range(max(0, index - period) + 1, index + 1):
            ema = (data[i].close - ema) * multiplier + ema
        
        return ema
    
    def _calculate_position_size(
        self, 
        expected_return: float, 
        confidence: float, 
        volatility: float
    ) -> float:
        # Kelly criterion with half-Kelly for safety
        win_prob = confidence
        win_size = abs(expected_return)
        lose_size = volatility * 2  # Approximate loss
        
        if lose_size == 0:
            return 0  # Avoid division by zero
        
        kelly = (win_prob / lose_size) - ((1 - win_prob) / win_size)
        half_kelly = max(0, min(0.25, kelly / 2))  # Cap at 25%
        
        return half_kelly
    
    def _calculate_metrics(self, results: List[Dict], equity: List[float]) -> BacktestResults:
        if not results:
            return BacktestResults(
                total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
                max_drawdown=0.0, hit_rate=0.0, information_coefficient=0.0,
                volatility=0.0, trades=0, win_rate=0.0, profit_factor=0.0
            )
        
        # Calculate returns
        returns = [(equity[i] - equity[i-1]) / equity[i-1] for i in range(1, len(equity))]
        total_return = (equity[-1] - equity[0]) / equity[0]
        annualized_return = ((1 + total_return) ** (252 / len(returns)) - 1) if returns else 0.0
        
        # Risk metrics
        volatility = np.std(returns) * np.sqrt(252) if returns else 0.0
        sharpe_ratio = annualized_return / volatility if volatility != 0 else 0.0
        
        # Drawdown
        drawdowns = []
        peak = equity[0]
        for e in equity:
            peak = max(peak, e)
            drawdowns.append((e - peak) / peak)
        max_drawdown = min(drawdowns) if drawdowns else 0.0
        
        # Accuracy
        correct = sum(1 for r in results if r['correct'])
        hit_rate = correct / len(results) if results else 0.0
        
        # Win rate
        profitable_trades = sum(1 for r in results if r['pnl'] > 0)
        win_rate = profitable_trades / len(results) if results else 0.0
        
        # Profit factor
        gross_profit = sum(max(0, r['pnl']) for r in results)
        gross_loss = sum(min(0, r['pnl']) for r in results)
        profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else float('inf')
        
        # Information coefficient
        forecasts = [r['forecast'] for r in results]
        actuals = [r['actual'] for r in results]
        if len(set(forecasts)) > 1 and len(set(actuals)) > 1:  # Avoid correlation on constant arrays
            ic = np.corrcoef(forecasts, actuals)[0, 1] if len(forecasts) > 1 else 0.0
        else:
            ic = 0.0
        
        return BacktestResults(
            total_return=total_return * 100,
            annualized_return=annualized_return * 100,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown * 100,
            hit_rate=hit_rate,
            information_coefficient=ic,
            volatility=volatility * 100,
            trades=len(results),
            win_rate=win_rate,
            profit_factor=profit_factor
        )

# Example usage and testing
def generate_synthetic_data(days: int) -> List[MarketData]:
    """Generate realistic synthetic market data"""
    data = []
    current_price = 10000  # Starting price for NIFTY-like index
    
    # Define market regimes with different characteristics
    regimes = [
        {'name': 'Low Vol Bull', 'mu': 0.0008, 'sigma': 0.008, 'prob': 0.35},  # 35% of time
        {'name': 'High Vol Bull', 'mu': 0.0005, 'sigma': 0.015, 'prob': 0.20},  # 20% of time
        {'name': 'Consolidation', 'mu': 0.0002, 'sigma': 0.007, 'prob': 0.20},  # 20% of time
        {'name': 'Bear', 'mu': -0.0006, 'sigma': 0.018, 'prob': 0.15},         # 15% of time
        {'name': 'Crisis', 'mu': -0.0015, 'sigma': 0.035, 'prob': 0.05},       # 5% of time
        {'name': 'Recovery', 'mu': 0.0012, 'sigma': 0.022, 'prob': 0.05}        # 5% of time
    ]
    
    current_regime = regimes[0]  # Start in Low Vol Bull
    
    for i in range(days):
        # Determine if regime should change based on transition probabilities
        rand = np.random.random()
        cumulative_prob = 0
        for regime in regimes:
            cumulative_prob += regime['prob']
            if rand < cumulative_prob:
                current_regime = regime
                break

        # Generate return with regime characteristics
        # Adding some autocorrelation (AR(1) = 0.05)
        prev_return = data[i-1].returns if i > 0 and hasattr(data[i-1], 'returns') and data[i-1].returns is not None else 0
        auto_correlation = 0.05 * prev_return
        
        # Generate base return with regime characteristics
        base_return = current_regime['mu'] + current_regime['sigma'] * np.random.normal()
        
        # Add autocorrelation and some fat-tail effect
        daily_return = base_return + auto_correlation
        
        # Add occasional jumps for more realistic fat tails
        if np.random.random() < 0.02:  # 2% chance of jump
            daily_return += (np.random.random() - 0.5) * 0.05  # Large move

        # Update price
        current_price = current_price * (1 + daily_return)
        
        # Generate OHLCV with some randomness
        open_price = data[i-1].close if i > 0 else current_price
        high = open_price * (1 + abs(daily_return) * (0.7 + np.random.random() * 0.3))
        low = open_price * (1 - abs(daily_return) * (0.7 + np.random.random() * 0.3))
        close = current_price
        volume = int(100000000 + np.random.random() * 200000000)  # Volume in crores

        data.append(MarketData(
            date=pd.Timestamp.now() - pd.Timedelta(days=days-i)).strftime('%Y-%m-%d'),
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            returns=daily_return
        ))
    
    # Calculate rolling statistics after generating all data
    for i in range(len(data)):
        # Calculate realized volatility (20-day)
        if i >= 19:
            returns = [d.returns for d in data[i-19:i+1] if d.returns is not None]
            if len(returns) > 0:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                data[i].realized_vol_20d = np.sqrt(variance) * np.sqrt(252)  # Annualized
        else:
            data[i].realized_vol_20d = 0.18  # Default value

        # Calculate momentum (5-day)
        if i >= 4:
            start_price = data[i-4].close
            end_price = data[i].close
            data[i].momentum_5d = (end_price - start_price) / start_price
        else:
            data[i].momentum_5d = 0.001  # Default value

        # Calculate VIX-like measure (just as a proxy)
        if i >= 19:
            data[i].vix_zscore = (data[i].realized_vol_20d - 0.18) / 0.05  # Normalize to z-score
        else:
            data[i].vix_zscore = 0.0  # Default value

    return data

def run_example():
    print("Running advanced financial forecasting ensemble example with hyperparameter optimization...")
    
    # Generate synthetic market data
    print("Generating synthetic market data...")
    sample_data = generate_synthetic_data(756)  # 3 years of data
    print(f"Generated {len(sample_data)} days of market data")
    
    # Create ensemble forecaster with hyperparameter optimization enabled
    print("Creating ensemble forecaster with hyperparameter optimization...")
    ensemble = EnsembleForecaster(optimize_hyperparams=True)
    
    # Train models
    print("Training models with hyperparameter optimization...")
    train_data = sample_data[-252:]  # Use 1 year of data for training
    ensemble.xgboost.train(train_data)
    ensemble.random_forest.train(train_data)
    ensemble.lstm.train(train_data)
    
    # Get latest features
    latest_features = ensemble._extract_sequence(sample_data)[-1] if hasattr(ensemble, '_extract_sequence') else FeatureVector(
        realized_vol_20d=sample_data[-1].realized_vol_20d or 0.2,
        momentum_5d=sample_data[-1].momentum_5d or 0.01,
        vix_zscore=sample_data[-1].vix_zscore or 0,
        sma_20=sum([d.close for d in sample_data[-20:]]) / 20,
        sma_50=sum([d.close for d in sample_data[-50:]]) / 50,
        rsi=50,  # Simplified
        macd=0,  # Simplified
        bb_position=0.5  # Simplified
    )
    
    print("Latest features:", {
        'realized_vol_20d': latest_features.realized_vol_20d,
        'momentum_5d': latest_features.momentum_5d,
        'vix_zscore': latest_features.vix_zscore,
        'rsi': latest_features.rsi
    })
    
    # Make a prediction
    print("Making prediction...")
    prediction = ensemble.predict(latest_features, sample_data[-50:])
    print("\nPrediction:")
    print(f"Direction: {prediction.direction}")
    print(f"Expected Return: {prediction.expected_return:.3f}%")
    print(f"Confidence: {prediction.confidence:.3f}")
    print(f"Quantiles - P10: {prediction.quantiles['p10']:.3f}%, P50: {prediction.quantiles['p50']:.3f}%, P90: {prediction.quantiles['p90']:.3f}%")
    print(f"Regime: {prediction.regime['current']}")
    print(f"Risk Metrics: VAR95={prediction.risk_metrics['var95']:.3f}%, MaxDD={prediction.risk_metrics['max_drawdown']:.3f}%")
    
    # Run backtest
    print("\nRunning backtest...")
    backtester = Backtester(optimize_hyperparams=True)
    backtest_results = backtester.run_walk_forward(sample_data, 200, 20)
    print("\nBacktest Results:")
    print(f"Total Return: {backtest_results.total_return:.2f}%")
    print(f"Annualized Return: {backtest_results.annualized_return:.2f}%")
    print(f"Sharpe Ratio: {backtest_results.sharpe_ratio:.3f}")
    print(f"Max Drawdown: {backtest_results.max_drawdown:.2f}%")
    print(f"Hit Rate: {backtest_results.hit_rate:.3f}")
    print(f"Win Rate: {backtest_results.win_rate:.3f}")
    print(f"Information Coefficient: {backtest_results.information_coefficient:.3f}")
    print(f"Volatility: {backtest_results.volatility:.2f}%")
    print(f"Profit Factor: {backtest_results.profit_factor:.3f}")

if __name__ == "__main__":
    run_example()