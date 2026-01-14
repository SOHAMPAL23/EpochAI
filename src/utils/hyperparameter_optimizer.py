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
import warnings
warnings.filterwarnings('ignore')
try:
    from xgboost import XGBRegressor
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor  # Fallback if xgboost not available

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
            
            model = XGBRegressor(**params, random_state=42)
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
            
            model = RandomForestRegressor(**params, random_state=42)
            model.fit(X_train, y_train)
            pred = model.predict(X_val)
            mse = mean_squared_error(y_val, pred)
            return mse  # Minimize MSE
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=100)
        return study.best_params