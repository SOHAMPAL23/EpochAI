import numpy as np
from typing import List
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
try:
    from xgboost import XGBRegressor
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor  # Fallback if xgboost not available
from ..utils.hyperparameter_optimizer import HyperparameterOptimizer
from ..utils.feature_engineering import MarketData, FeatureVector

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
                getattr(data[i], 'realized_vol_20d', 0.2),
                getattr(data[i], 'momentum_5d', 0.01),
                getattr(data[i], 'vix_zscore', 0),
                getattr(data[i], 'close', 10000),  # Price level
                getattr(data[i], 'volume', 1000000),  # Volume
                self.calculate_sma(data, i, 20),
                self.calculate_sma(data, i, 50),
                self.calculate_rsi(data, i, 14),
                self.calculate_macd(data, i),
                self.calculate_bb_position(data, i, 20),
                self.calculate_atr(data, i, 14),
                self.calculate_volume_ratio(data, i, 20)
            ]
            
            # Target is next period return
            target = getattr(data[i + 1], 'returns', 0)
            
            features.append(feat)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def calculate_sma(self, data: List[MarketData], index: int, period: int) -> float:
        start = max(0, index - period + 1)
        prices = [getattr(d, 'close', 0) for d in data[start:index+1]]
        return sum(prices) / len(prices) if prices else 10000  # Default to 10000
    
    def calculate_rsi(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 50  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(max(0, index - period + 1), index + 1):
            if i == 0:
                continue
            
            change = getattr(data[i], 'close', 0) - getattr(data[i-1], 'close', 0)
            
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
        if index < period:
            return getattr(data[index], 'close', 10000)  # If not enough data, return current close
        
        multiplier = 2 / (period + 1)
        # Start with the closing price 'period' days ago or from the beginning
        start_idx = max(0, index - period)
        ema = getattr(data[start_idx], 'close', 10000)  # Starting value
        
        for i in range(start_idx + 1, index + 1):
            ema = (getattr(data[i], 'close', ema) - ema) * multiplier + ema
        
        return ema
    
    def calculate_bb_position(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 0.5  # Middle of bands
        
        sma = self.calculate_sma(data, index, period)
        prices = [getattr(d, 'close', 0) for d in data[max(0, index - period + 1):index + 1]]
        price_std = np.std(prices) if len(prices) > 1 else 0.01
        
        upper_band = sma + (2 * price_std)
        lower_band = sma - (2 * price_std)
        
        if upper_band == lower_band:
            return 0.5  # Avoid division by zero
        
        return (getattr(data[index], 'close', sma) - lower_band) / (upper_band - lower_band)
    
    def calculate_atr(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 0.01  # Default small value
        
        tr_values = []
        for i in range(max(0, index - period + 1), index + 1):
            high = getattr(data[i], 'high', 0)
            low = getattr(data[i], 'low', 0)
            prev_close = getattr(data[i-1], 'close', high) if i > 0 else getattr(data[i], 'close', high)
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)
        
        return sum(tr_values) / len(tr_values) if tr_values else 0.01
    
    def calculate_volume_ratio(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return 1.0  # Default ratio
        
        current_vol = getattr(data[index], 'volume', 1000000)
        avg_vol = sum([getattr(d, 'volume', 1000000) for d in data[max(0, index - period + 1):index + 1]]) / period
        
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
            self.model = XGBRegressor(**best_params, random_state=42)
        else:
            # Use default parameters
            self.model = XGBRegressor(
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