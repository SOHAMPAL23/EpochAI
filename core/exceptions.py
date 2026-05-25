"""
Custom exceptions for EpochAI system
"""


class EpochAIException(Exception):
    """Base exception for EpochAI system"""
    pass


class InsufficientDataError(EpochAIException):
    """Raised when there is insufficient data for training or prediction"""
    
    def __init__(self, required: int, actual: int, message: str = None):
        self.required = required
        self.actual = actual
        if message is None:
            message = f"Insufficient data: required {required}, got {actual}"
        super().__init__(message)


class ModelNotTrainedError(EpochAIException):
    """Raised when trying to use an untrained model"""
    
    def __init__(self, model_name: str = "Model"):
        message = f"{model_name} has not been trained yet"
        super().__init__(message)


class InvalidDataError(EpochAIException):
    """Raised when data validation fails"""
    pass


class PredictionError(EpochAIException):
    """Raised when prediction fails"""
    pass


class ConfigurationError(EpochAIException):
    """Raised when configuration is invalid"""
    pass


class FeatureExtractionError(EpochAIException):
    """Raised when feature extraction fails"""
    pass