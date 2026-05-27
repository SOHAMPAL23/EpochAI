"""
Technical indicators for financial analysis
"""

import numpy as np
from typing import List, Tuple, Optional
from core.data_models import MarketData
from config.logging_config import get_logger

logger = get_logger('features')


class TechnicalIndicators:
    """Collection of technical analysis indicators"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(prices) < period:
            return [np.mean(prices[:i+1]) for i in range(len(prices))]
        
        sma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                sma_values.append(np.mean(prices[:i+1]))
            else:
                sma_values.append(np.mean(prices[i-period+1:i+1]))
        
        return sma_values
    
    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if not prices:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = [prices[0]]  # Start with first price
        
        for i in range(1, len(prices)):
            ema_value = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema_value)
        
        return ema_values
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        """Relative Strength Index"""
        if len(prices) < period + 1:
            return [50.0] * len(prices)  # Default RSI
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        rsi_values = [50.0]  # First value is default
        
        # Calculate initial average gain and loss
        initial_gains = [change for change in changes[:period] if change > 0]
        initial_losses = [-change for change in changes[:period] if change < 0]
        
        avg_gain = np.mean(initial_gains) if initial_gains else 0.001
        avg_loss = np.mean(initial_losses) if initial_losses else 0.001
        
        # Calculate RSI for remaining periods
        for i in range(period, len(changes)):
            change = changes[i]
            
            if change > 0:
                avg_gain = ((avg_gain * (period - 1)) + change) / period
                avg_loss = (avg_loss * (period - 1)) / period
            else:
                avg_gain = (avg_gain * (period - 1)) / period
                avg_loss = ((avg_loss * (period - 1)) + (-change)) / period
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(max(0, min(100, rsi)))
        
        return rsi_values
    
    @staticmethod
    def macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[List[float], List[float], List[float]]:
        """MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow_period:
            zeros = [0.0] * len(prices)
            return zeros, zeros, zeros
        
        # Calculate EMAs
        fast_ema = TechnicalIndicators.ema(prices, fast_period)
        slow_ema = TechnicalIndicators.ema(prices, slow_period)
        
        # Calculate MACD line
        macd_line = [fast_ema[i] - slow_ema[i] for i in range(len(prices))]
        
        # Calculate signal line (EMA of MACD line)
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        
        # Calculate histogram
        histogram = [macd_line[i] - signal_line[i] for i in range(len(macd_line))]
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[List[float], List[float], List[float]]:
        """Bollinger Bands"""
        if len(prices) < period:
            # Return flat bands for insufficient data
            avg_price = np.mean(prices) if prices else 100.0
            return [avg_price] * len(prices), [avg_price] * len(prices), [avg_price] * len(prices)
        
        sma_values = TechnicalIndicators.sma(prices, period)
        upper_bands = []
        lower_bands = []
        
        for i in range(len(prices)):
            if i < period - 1:
                # Use available data for early periods
                period_prices = prices[:i+1]
            else:
                period_prices = prices[i-period+1:i+1]
            
            std = np.std(period_prices)
            upper_bands.append(sma_values[i] + (std_dev * std))
            lower_bands.append(sma_values[i] - (std_dev * std))
        
        return upper_bands, sma_values, lower_bands
    
    @staticmethod
    def stochastic(data: List[MarketData], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Stochastic Oscillator"""
        if len(data) < k_period:
            default_k = [50.0] * len(data)
            default_d = [50.0] * len(data)
            return default_k, default_d
        
        k_values = []
        
        for i in range(len(data)):
            if i < k_period - 1:
                # Use available data for early periods
                period_data = data[:i+1]
            else:
                period_data = data[i-k_period+1:i+1]
            
            highest_high = max(d.high for d in period_data)
            lowest_low = min(d.low for d in period_data)
            current_close = data[i].close
            
            if highest_high == lowest_low:
                k_value = 50.0
            else:
                k_value = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
            
            k_values.append(max(0, min(100, k_value)))
        
        # Calculate %D (SMA of %K)
        d_values = TechnicalIndicators.sma(k_values, d_period)
        
        return k_values, d_values
    
    @staticmethod
    def williams_r(data: List[MarketData], period: int = 14) -> List[float]:
        """Williams %R"""
        if len(data) < period:
            return [-50.0] * len(data)  # Default middle value
        
        williams_r_values = []
        
        for i in range(len(data)):
            if i < period - 1:
                period_data = data[:i+1]
            else:
                period_data = data[i-period+1:i+1]
            
            highest_high = max(d.high for d in period_data)
            lowest_low = min(d.low for d in period_data)
            current_close = data[i].close
            
            if highest_high == lowest_low:
                williams_r = -50.0
            else:
                williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
            
            williams_r_values.append(max(-100, min(0, williams_r)))
        
        return williams_r_values
    
    @staticmethod
    def atr(data: List[MarketData], period: int = 14) -> List[float]:
        """Average True Range"""
        if len(data) < 2:
            return [0.01] * len(data)  # Default ATR
        
        true_ranges = [data[0].high - data[0].low]  # First TR is just high - low
        
        # Calculate True Range for each period
        for i in range(1, len(data)):
            current = data[i]
            previous = data[i-1]
            
            tr1 = current.high - current.low
            tr2 = abs(current.high - previous.close)
            tr3 = abs(current.low - previous.close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # Calculate ATR using SMA of True Ranges
        atr_values = TechnicalIndicators.sma(true_ranges, period)
        
        return atr_values
    
    @staticmethod
    def momentum(prices: List[float], period: int = 10) -> List[float]:
        """Price Momentum"""
        if len(prices) < period + 1:
            return [0.0] * len(prices)
        
        momentum_values = [0.0] * period  # First 'period' values are zero
        
        for i in range(period, len(prices)):
            if prices[i - period] != 0:
                momentum = (prices[i] - prices[i - period]) / prices[i - period]
            else:
                momentum = 0.0
            momentum_values.append(momentum)
        
        return momentum_values
    
    @staticmethod
    def roc(prices: List[float], period: int = 12) -> List[float]:
        """Rate of Change"""
        if len(prices) < period + 1:
            return [0.0] * len(prices)
        
        roc_values = [0.0] * period
        
        for i in range(period, len(prices)):
            if prices[i - period] != 0:
                roc = ((prices[i] - prices[i - period]) / prices[i - period]) * 100
            else:
                roc = 0.0
            roc_values.append(roc)
        
        return roc_values
    
    @staticmethod
    def cci(data: List[MarketData], period: int = 20) -> List[float]:
        """Commodity Channel Index"""
        if len(data) < period:
            return [0.0] * len(data)
        
        # Calculate Typical Price
        typical_prices = [(d.high + d.low + d.close) / 3 for d in data]
        
        cci_values = []
        
        for i in range(len(data)):
            if i < period - 1:
                cci_values.append(0.0)
                continue
            
            # Calculate SMA of typical prices
            period_prices = typical_prices[i-period+1:i+1]
            sma_tp = np.mean(period_prices)
            
            # Calculate Mean Deviation
            mean_deviation = np.mean([abs(tp - sma_tp) for tp in period_prices])
            
            if mean_deviation == 0:
                cci = 0.0
            else:
                cci = (typical_prices[i] - sma_tp) / (0.015 * mean_deviation)
            
            cci_values.append(cci)
        
        return cci_values
    
    @staticmethod
    def obv(data: List[MarketData]) -> List[float]:
        """On-Balance Volume"""
        if not data:
            return []
        
        obv_values = [data[0].volume]  # Start with first volume
        
        for i in range(1, len(data)):
            current_close = data[i].close
            previous_close = data[i-1].close
            current_volume = data[i].volume
            
            if current_close > previous_close:
                obv = obv_values[-1] + current_volume
            elif current_close < previous_close:
                obv = obv_values[-1] - current_volume
            else:
                obv = obv_values[-1]  # No change
            
            obv_values.append(obv)
        
        return obv_values