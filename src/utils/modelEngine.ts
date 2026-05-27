import { MarketData, FeatureVector, ForecastOutput, RiskMetrics, ModelConfig } from '../types';

// Mock models that simulate real ML models
class XGBoostModel {
  private params = { max_depth: 6, learning_rate: 0.05, n_estimators: 500 };
  
  async train(data: MarketData[]) {
    console.log(`Training XGBoost model with ${data.length} data points`);
    // In a real implementation, this would train an actual XGBoost model
    return this.params;
  }
  
  predict(features: FeatureVector): number {
    // Simulate a prediction based on features
    // This is a simplified model that gives higher returns for positive momentum
    // and adjusts based on volatility and sentiment
    let prediction = 0.001; // Base return
    
    // Adjust based on momentum
    prediction += features.momentum_5d * 0.5;
    
    // Adjust based on volatility (higher volatility reduces expected return)
    prediction -= features.realized_vol_20d * 0.1;
    
    // Adjust based on RSI (overbought/oversold conditions)
    if (features.rsi > 70) prediction -= 0.002; // Overbought
    if (features.rsi < 30) prediction += 0.002; // Oversold
    
    // Add some randomness to make it more realistic
    prediction += (Math.random() - 0.5) * 0.005;
    
    return Math.max(-0.05, Math.min(0.05, prediction)); // Cap between -5% and 5%
  }
}

class RandomForestModel {
  private params = { n_estimators: 300, max_depth: 15 };
  
  async train(data: MarketData[]) {
    console.log(`Training Random Forest model with ${data.length} data points`);
    // In a real implementation, this would train an actual Random Forest model
    return this.params;
  }
  
  predict(features: FeatureVector): { direction: number; confidence: number } {
    // Simulate a binary classification prediction
    // Calculate a score based on features
    let score = 0;
    
    // Positive factors
    score += features.momentum_5d * 10;
    score += features.rsi > 50 ? 1 : -1; // Above 50 is bullish
    score += features.bb_position < 0.5 ? 1 : -1; // Below middle band is bullish
    
    // Negative factors
    score -= features.realized_vol_20d * 5;
    
    // Add some randomness
    score += (Math.random() - 0.5) * 2;
    
    const direction = score > 0 ? 1 : -1; // 1 for UP, -1 for DOWN
    const confidence = Math.min(1.0, Math.abs(score) / 5); // Normalize confidence
    
    return { direction, confidence: Math.max(0.5, confidence) }; // Minimum 50% confidence
  }
}

class LSTMModel {
  private architecture = { layers: [128, 64], outputs: 3 }; // 3 outputs for P10, P50, P90
  
  async train(data: MarketData[]) {
    console.log(`Training LSTM model with ${data.length} data points`);
    // In a real implementation, this would train an actual LSTM model
    return this.architecture;
  }
  
  predict(sequence: MarketData[]): { p10: number; p50: number; p90: number } {
    // Simulate quantile predictions
    // In a real LSTM, this would return actual quantile predictions
    const baseReturn = sequence[sequence.length - 1].returns || 0;
    
    // Add some volatility around the base return
    const volatility = sequence.reduce((sum, d) => sum + Math.abs(d.returns || 0), 0) / sequence.length;
    
    return {
      p10: baseReturn - volatility * 2, // 10th percentile (worst case)
      p50: baseReturn, // 50th percentile (median)
      p90: baseReturn + volatility * 2  // 90th percentile (best case)
    };
  }
}

class HMMModel {
  private states = 6; // 6 regime states
  private transitionMatrix: number[][] = [];
  private emissionParams: any = {};
  
  async train(data: MarketData[]) {
    console.log(`Training HMM model with ${data.length} data points`);
    
    // Initialize transition matrix with reasonable defaults
    this.transitionMatrix = Array(6).fill(null).map(() => Array(6).fill(0.1));
    for (let i = 0; i < 6; i++) {
      this.transitionMatrix[i][i] = 0.8; // Higher probability of staying in same state
    }
    
    // Initialize emission parameters for each regime
    this.emissionParams = {
      'Low Vol Bull': { vol_mean: 0.008, vol_std: 0.002, ret_mean: 0.0008, ret_std: 0.001 },
      'High Vol Bull': { vol_mean: 0.015, vol_std: 0.005, ret_mean: 0.0005, ret_std: 0.002 },
      'Consolidation': { vol_mean: 0.007, vol_std: 0.001, ret_mean: 0.0002, ret_std: 0.001 },
      'Bear': { vol_mean: 0.018, vol_std: 0.008, ret_mean: -0.0006, ret_std: 0.003 },
      'Crisis': { vol_mean: 0.035, vol_std: 0.015, ret_mean: -0.0015, ret_std: 0.008 },
      'Recovery': { vol_mean: 0.022, vol_std: 0.006, ret_mean: 0.0012, ret_std: 0.004 }
    };
    
    return { states: this.states, transitionMatrix: this.transitionMatrix };
  }
  
  detect(currentState: { volatility: number; returns: number; vix: number }): { regime: string; probabilities: Record<string, number> } {
    // Calculate probability of current state belonging to each regime
    const regimes = ['Low Vol Bull', 'High Vol Bull', 'Consolidation', 'Bear', 'Crisis', 'Recovery'];
    const probabilities: Record<string, number> = {};
    
    for (const regime of regimes) {
      const params = this.emissionParams[regime];
      
      // Calculate Gaussian probability for each parameter
      const volProb = this.gaussianPDF(currentState.volatility, params.vol_mean, params.vol_std);
      const retProb = this.gaussianPDF(currentState.returns, params.ret_mean, params.ret_std);
      
      // Combine probabilities (simplified)
      probabilities[regime] = volProb * retProb;
    }
    
    // Normalize probabilities
    const total = Object.values(probabilities).reduce((sum, p) => sum + p, 0);
    for (const regime of regimes) {
      probabilities[regime] = probabilities[regime] / total;
    }
    
    // Find most likely regime
    const mostLikely = Object.entries(probabilities).reduce((max, current) => 
      current[1] > max[1] ? current : max
    )[0];
    
    return { regime: mostLikely, probabilities };
  }
  
  private gaussianPDF(x: number, mean: number, std: number): number {
    const coefficient = 1 / (std * Math.sqrt(2 * Math.PI));
    const exponent = -Math.pow(x - mean, 2) / (2 * Math.pow(std, 2));
    return coefficient * Math.exp(exponent);
  }
}

class GARCHModel {
  private params = { omega: 0.000001, alpha: 0.1, beta: 0.85 };
  
  async train(returns: number[]) {
    console.log(`Training GARCH model with ${returns.length} return observations`);
    // In a real implementation, this would estimate GARCH parameters using MLE
    return this.params;
  }
  
  forecast(returns: number[], horizon: number): number[] {
    // GARCH(1,1) forecast: σ²(t) = ω + α·ε²(t-1) + β·σ²(t-1)
    const forecasts: number[] = [];
    let currentVariance = this.params.omega / (1 - this.params.alpha - this.params.beta); // Long-run variance
    
    // Initialize with recent variance
    if (returns.length > 0) {
      const recentReturns = returns.slice(-10);
      const meanReturn = recentReturns.reduce((a, b) => a + b, 0) / recentReturns.length;
      currentVariance = recentReturns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / recentReturns.length;
    }
    
    for (let h = 0; h < horizon; h++) {
      // Forecast variance for period h+1
      const nextVariance = this.params.omega + 
                          this.params.alpha * Math.pow(returns[returns.length - 1] || 0, 2) + 
                          this.params.beta * currentVariance;
      
      forecasts.push(Math.sqrt(nextVariance) * Math.sqrt(252)); // Annualized volatility
      currentVariance = nextVariance;
    }
    
    return forecasts;
  }
}

// Initialize models
const xgboost = new XGBoostModel();
const randomForest = new RandomForestModel();
const lstm = new LSTMModel();
const hmm = new HMMModel();
const garch = new GARCHModel();

export async function trainModels(data: MarketData[]) {
  console.log('Starting model training...');
  
  await Promise.all([
    xgboost.train(data),
    randomForest.train(data),
    lstm.train(data),
    hmm.train(data),
    garch.train(data.map(d => d.returns || 0).filter(r => !isNaN(r)))
  ]);
  
  console.log('All models trained successfully!');
}

export function makePrediction(recentData: MarketData[], config: ModelConfig): ForecastOutput {
  // Extract features from recent data
  const features = extractFeatures(recentData);
  
  // Get predictions from individual models
  const xgbPrediction = xgboost.predict(features);
  const rfResult = randomForest.predict(features);
  const lstmResult = lstm.predict(recentData);
  const hmmResult = hmm.detect({
    volatility: features.realized_vol_20d,
    returns: features.momentum_5d,
    vix: features.vix_zscore
  });
  const garchForecasts = garch.forecast(
    recentData.map(d => d.returns || 0).filter(r => !isNaN(r)), 
    5
  );
  
  // Ensemble prediction with regime-adaptive weighting
  const regimeWeights = getRegimeWeights(hmmResult.regime);
  
  const finalReturn = (
    regimeWeights.xgboost * xgbPrediction +
    regimeWeights.lstm * lstmResult.p50 +
    regimeWeights.direction * (rfResult.direction === 1 ? 0.005 : -0.005)
  );
  
  // Calculate risk metrics
  const riskMetrics = calculateRiskMetrics(lstmResult, garchForecasts[0]);
  
  // Generate explanations
  const explanations = generateExplanations(features, hmmResult.regime);
  
  return {
    direction: rfResult.direction === 1 ? 'UP' : 'DOWN',
    expected_return: finalReturn * 100, // Convert to percentage
    confidence: rfResult.confidence,
    quantiles: {
      p10: lstmResult.p10 * 100,
      p50: lstmResult.p50 * 100,
      p90: lstmResult.p90 * 100
    },
    regime: {
      current: hmmResult.regime,
      probabilities: hmmResult.probabilities
    },
    risk_metrics: riskMetrics,
    explainability: explanations
  };
}

function extractFeatures(data: MarketData[]): FeatureVector {
  const latest = data[data.length - 1];
  
  // Calculate technical indicators
  const sma_20 = data.slice(-20).reduce((sum, d) => sum + d.close, 0) / 20;
  const sma_50 = data.slice(-50).reduce((sum, d) => sum + d.close, 0) / 50;
  
  // Calculate RSI (14-period)
  let rsi = 50; // Default neutral
  if (data.length >= 14) {
    const recentData = data.slice(-14);
    let gains = 0;
    let losses = 0;
    
    for (let i = 1; i < recentData.length; i++) {
      const change = recentData[i].close - recentData[i-1].close;
      if (change > 0) {
        gains += change;
      } else {
        losses += Math.abs(change);
      }
    }
    
    const avgGain = gains / 14;
    const avgLoss = losses / 14;
    
    if (avgLoss !== 0) {
      const rs = avgGain / avgLoss;
      rsi = 100 - (100 / (1 + rs));
    }
  }
  
  // Calculate MACD (simplified)
  const ema12 = calculateEMA(data, 12);
  const ema26 = calculateEMA(data, 26);
  const macd = ema12 - ema26;
  
  // Calculate Bollinger Band position
  const bbUpper = sma_20 + (2 * calculateStdDev(data.slice(-20).map(d => d.close)));
  const bbLower = sma_20 - (2 * calculateStdDev(data.slice(-20).map(d => d.close)));
  const bbPosition = bbUpper !== bbLower ? (latest.close - bbLower) / (bbUpper - bbLower) : 0.5;
  
  return {
    realized_vol_20d: latest.realized_vol_20d || 0.18,
    momentum_5d: latest.momentum_5d || 0.001,
    vix_zscore: latest.vix_zscore || 0,
    sma_20,
    sma_50,
    rsi,
    macd,
    bb_position: bbPosition
  };
}

function calculateEMA(data: MarketData[], period: number): number {
  if (data.length < period) return data[data.length - 1].close;
  
  const multiplier = 2 / (period + 1);
  let ema = data.slice(-period)[0].close; // First value
  
  for (let i = 1; i < period; i++) {
    ema = (data[data.length - period + i].close - ema) * multiplier + ema;
  }
  
  return ema;
}

function calculateStdDev(values: number[]): number {
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
  const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
  const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
  return Math.sqrt(variance);
}

function getRegimeWeights(regime: string): Record<string, number> {
  const weights: Record<string, Record<string, number>> = {
    'Low Vol Bull': { xgboost: 0.5, lstm: 0.3, direction: 0.2 },
    'High Vol Bull': { xgboost: 0.4, lstm: 0.4, direction: 0.2 },
    'Bear': { xgboost: 0.4, lstm: 0.3, direction: 0.3 },
    'Crisis': { xgboost: 0.3, lstm: 0.5, direction: 0.2 }, // Higher weight to LSTM in crisis
    'Recovery': { xgboost: 0.45, lstm: 0.35, direction: 0.2 },
    'Consolidation': { xgboost: 0.5, lstm: 0.3, direction: 0.2 }
  };
  
  return weights[regime] || weights['Consolidation'];
}

function calculateRiskMetrics(quantiles: { p10: number; p50: number; p90: number }, volatility: number): RiskMetrics {
  // VaR 95% (absolute value of 10th percentile)
  const var95 = Math.abs(quantiles.p10) * 100;
  
  // CVaR 95% (expected shortfall beyond VaR)
  const cvar95 = var95 * 1.2; // Simplified approximation
  
  // Max Drawdown (estimated based on volatility and return)
  const maxDrawdown = Math.min(-2, -Math.abs(quantiles.p10) * 150); // Conservative estimate
  
  // Tail Risk Score (probability of >3% loss)
  // Assuming normal distribution between quantiles
  const mean = quantiles.p50;
  const std = (quantiles.p90 - quantiles.p10) / 2.56; // Approx from 90th-10th percentiles
  
  // Calculate probability of >3% loss
  const zScore = (0.03 - Math.abs(mean)) / std;
  const tailRiskScore = Math.max(0, Math.min(1, 0.5 * (1 - Math.erf(zScore / Math.sqrt(2)))));
  
  return {
    var95,
    cvar95,
    max_drawdown: maxDrawdown,
    tail_risk_score: tailRiskScore,
    volatility_forecast: volatility
  };
}

function generateExplanations(features: FeatureVector, regime: string): string[] {
  const explanations: string[] = [];
  
  if (features.realized_vol_20d > 0.25) {
    explanations.push("High volatility detected, indicating increased market uncertainty");
  } else if (features.realized_vol_20d < 0.15) {
    explanations.push("Low volatility detected, suggesting stable market conditions");
  }
  
  if (features.momentum_5d > 0.03) {
    explanations.push("Strong positive momentum observed, suggesting upward trend continuation");
  } else if (features.momentum_5d < -0.03) {
    explanations.push("Strong negative momentum observed, suggesting downward trend continuation");
  }
  
  if (features.rsi > 70) {
    explanations.push("RSI indicates overbought conditions, potential reversal downside");
  } else if (features.rsi < 30) {
    explanations.push("RSI indicates oversold conditions, potential reversal upside");
  }
  
  explanations.push(`Current market regime: ${regime}`);
  
  return explanations;
}