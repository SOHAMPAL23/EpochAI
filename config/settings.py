"""
Configuration settings for EpochAI system
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ModelConfig:
    """Configuration for prediction models"""
    max_training_samples: int = 5000
    min_training_samples: int = 30
    prediction_interval: float = 1.0  # seconds
    confidence_threshold: float = 0.5
    ensemble_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.ensemble_weights is None:
            self.ensemble_weights = {
                'xgboost': 0.4,
                'random_forest': 0.3,
                'lstm': 0.3
            }


@dataclass
class WebConfig:
    """Configuration for web applications"""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False
    secret_key: str = 'dev-key-change-in-production'
    cors_enabled: bool = True
    rate_limit: str = "100 per minute"
    
    def __post_init__(self):
        # Override with environment variables if available
        self.host = os.getenv('FLASK_HOST', self.host)
        self.port = int(os.getenv('FLASK_PORT', self.port))
        self.debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        self.secret_key = os.getenv('SECRET_KEY', self.secret_key)


@dataclass
class DataConfig:
    """Configuration for data handling"""
    max_buffer_size: int = 1000
    data_validation_enabled: bool = True
    synthetic_data_points: int = 252  # 1 year of trading days
    cache_size: int = 100


@dataclass
class RiskConfig:
    """Configuration for risk management"""
    var_confidence: float = 0.95
    max_drawdown_threshold: float = -20.0  # percentage
    volatility_threshold: float = 0.05
    position_size_limit: float = 0.1  # 10% max position size


class Settings:
    """Main settings class containing all configuration"""
    
    def __init__(self):
        self.model = ModelConfig()
        self.web = WebConfig()
        self.data = DataConfig()
        self.risk = RiskConfig()
        
        # Environment-specific settings
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        if self.environment == 'production':
            self.web.debug = False
            self.web.secret_key = os.getenv('SECRET_KEY', 'CHANGE-ME-IN-PRODUCTION')
            self.log_level = 'WARNING'
        elif self.environment == 'testing':
            self.data.max_buffer_size = 100
            self.model.min_training_samples = 10
            self.log_level = 'DEBUG'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'model': self.model.__dict__,
            'web': self.web.__dict__,
            'data': self.data.__dict__,
            'risk': self.risk.__dict__,
            'environment': self.environment,
            'log_level': self.log_level
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Settings':
        """Create settings from dictionary"""
        settings = cls()
        
        if 'model' in config_dict:
            for key, value in config_dict['model'].items():
                if hasattr(settings.model, key):
                    setattr(settings.model, key, value)
        
        if 'web' in config_dict:
            for key, value in config_dict['web'].items():
                if hasattr(settings.web, key):
                    setattr(settings.web, key, value)
        
        if 'data' in config_dict:
            for key, value in config_dict['data'].items():
                if hasattr(settings.data, key):
                    setattr(settings.data, key, value)
        
        if 'risk' in config_dict:
            for key, value in config_dict['risk'].items():
                if hasattr(settings.risk, key):
                    setattr(settings.risk, key, value)
        
        return settings


# Global settings instance
settings = Settings()