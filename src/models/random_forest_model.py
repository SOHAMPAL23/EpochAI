import numpy as np
from typing import List, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from ..utils.hyperparameter_optimizer import HyperparameterOptimizer
from ..utils.feature_engineering import MarketData, FeatureVector

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
                getattr(data[i], 'realized_vol_20d', 0.2),
                getattr(data[i], 'momentum_5d', 0.01),
                getattr(data[i], 'vix_zscore', 0),
                getattr(data[i], 'rsi', 50),  # Use 50 as default RSI
                getattr(data[i], 'macd', 0),  # Use 0 as default MACD
                getattr(data[i], 'bb_position', 0.5),  # Use 0.5 as default BB position
                getattr(data[i], 'close', 10000),  # Use 10000 as default close
                getattr(data[i], 'volume', 1000000),  # Use 1000000 as default volume
                self.calculate_sma(data, i, 20),
                self.calculate_atr(data, i, 14),
                self.calculate_volume_ratio(data, i, 20)
            ]
            
            # Target is direction (1 for up, 0 for down)
            target = 1 if getattr(data[i + 1], 'returns', 0) > 0 else 0
            
            features.append(feat)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def calculate_sma(self, data: List[MarketData], index: int, period: int) -> float:
        start = max(0, index - period + 1)
        prices = [getattr(d, 'close', 0) for d in data[start:index+1]]
        return sum(prices) / len(prices) if prices else 10000  # Default to 10000
    
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