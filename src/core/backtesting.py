import numpy as np
from typing import List, Dict
from models.ensemble_model import EnsembleForecaster
from utils.feature_engineering import MarketData, FeatureVector, BacktestResults

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
        returns = [d.returns for d in data if hasattr(d, 'returns') and d.returns is not None]
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
        prices_for_bb = [d.close for d in data[max(0, index-19):index+1]]
        bb_std = np.std(prices_for_bb) if len(prices_for_bb) > 1 else 0.01
        bb_upper = sma_20 + (2 * bb_std)
        bb_lower = sma_20 - (2 * bb_std)
        bb_position = 0.5 if bb_upper == bb_lower else (current.close - bb_lower) / (bb_upper - bb_lower)
        
        return FeatureVector(
            realized_vol_20d=getattr(current, 'realized_vol_20d', 0.2),
            momentum_5d=getattr(current, 'momentum_5d', 0.01),
            vix_zscore=getattr(current, 'vix_zscore', 0),
            sma_20=sma_20,
            sma_50=sma_50,
            rsi=rsi,
            macd=macd,
            bb_position=bb_position
        )
    
    def _calculate_ema(self, data: List[MarketData], index: int, period: int) -> float:
        if index < period:
            return data[index].close  # If not enough data, return current close
        
        multiplier = 2 / (period + 1)
        # Start with the closing price 'period' days ago or from the beginning
        start_idx = max(0, index - period)
        ema = data[start_idx].close  # Starting value
        
        for i in range(start_idx + 1, index + 1):
            ema = (data[i].close - ema) * multiplier + ema
        
        return ema
    
    def _calculate_position_size(
        self, 
        expected_return: float, 
        confidence: float, 
        volatility: float
    ) -> float:
        # Kelly criterion with practical constraints
        # Normalize inputs to avoid extreme positions
        
        # Ensure volatility is not zero
        vol = max(0.001, volatility)  # Minimum volatility to avoid division by zero
        
        # Use a more conservative approach based on confidence and expected return
        # Position size = confidence * expected_return / volatility (scaled)
        base_position = (confidence * expected_return / vol) if vol != 0 else 0
        
        # Cap position size to avoid over-leveraging
        position_size = max(-0.25, min(0.25, base_position))  # Cap at +/-25%
        
        return position_size
    
    def _calculate_metrics(self, results: List[Dict], equity: List[float]) -> BacktestResults:
        if not results:
            return BacktestResults(
                total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
                max_drawdown=0.0, hit_rate=0.0, information_coefficient=0.0,
                volatility=0.0, trades=0, win_rate=0.0, profit_factor=0.0
            )
        
        # Calculate returns
        if len(equity) < 2:
            return BacktestResults(
                total_return=0.0, annualized_return=0.0, sharpe_ratio=0.0,
                max_drawdown=0.0, hit_rate=0.0, information_coefficient=0.0,
                volatility=0.0, trades=0, win_rate=0.0, profit_factor=0.0
            )
        
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
        if len(set(forecasts)) > 1 and len(set(actuals)) > 1 and len(forecasts) > 1:  # Avoid correlation on constant arrays
            try:
                ic = np.corrcoef(forecasts, actuals)[0, 1] if len(forecasts) > 1 else 0.0
            except:
                ic = 0.0
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