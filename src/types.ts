export interface MarketData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  returns?: number;
  realized_vol_20d?: number;
  momentum_5d?: number;
  vix_zscore?: number;
}

export interface FeatureVector {
  realized_vol_20d: number;
  momentum_5d: number;
  vix_zscore: number;
  sma_20: number;
  sma_50: number;
  rsi: number;
  macd: number;
  bb_position: number;
}

export interface ForecastOutput {
  direction: 'UP' | 'DOWN';
  expected_return: number;
  confidence: number;
  quantiles: {
    p10: number;
    p50: number;
    p90: number;
  };
  regime: {
    current: string;
    probabilities: Record<string, number>;
  };
  risk_metrics: RiskMetrics;
  explainability: string[];
}

export interface RiskMetrics {
  var95: number;
  cvar95: number;
  max_drawdown: number;
  tail_risk_score: number;
  volatility_forecast: number;
}

export interface BacktestResults {
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  hit_rate: number;
  information_coefficient: number;
  volatility: number;
  trades: number;
  win_rate: number;
  profit_factor: number;
}

export interface ModelConfig {
  sentimentEnabled: boolean;
  regimeEnabled: boolean;
  explanationsEnabled: boolean;
}