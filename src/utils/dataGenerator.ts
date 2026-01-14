import { MarketData } from '../types';

// Regime definitions
const REGIMES = [
  { name: 'Low Vol Bull', mu: 0.0008, sigma: 0.008, prob: 0.35 }, // 35% of time
  { name: 'High Vol Bull', mu: 0.0005, sigma: 0.015, prob: 0.20 }, // 20% of time
  { name: 'Consolidation', mu: 0.0002, sigma: 0.007, prob: 0.20 }, // 20% of time
  { name: 'Bear', mu: -0.0006, sigma: 0.018, prob: 0.15 }, // 15% of time
  { name: 'Crisis', mu: -0.0015, sigma: 0.035, prob: 0.05 }, // 5% of time
  { name: 'Recovery', mu: 0.0012, sigma: 0.022, prob: 0.05 }  // 5% of time
];

export const generateSyntheticData = (days: number): MarketData[] => {
  const data: MarketData[] = [];
  let currentPrice = 10000; // Starting price for NIFTY-like index
  let currentRegime = REGIMES[0]; // Start in Low Vol Bull

  for (let i = 0; i < days; i++) {
    // Determine if regime should change based on transition probabilities
    const rand = Math.random();
    let cumulativeProb = 0;
    for (const regime of REGIMES) {
      cumulativeProb += regime.prob;
      if (rand < cumulativeProb) {
        currentRegime = regime;
        break;
      }
    }

    // Generate return with regime characteristics
    // Adding some autocorrelation (AR(1) = 0.05)
    const prevReturn = i > 0 ? data[i-1].returns || 0 : 0;
    const autoCorrelation = 0.05 * prevReturn;
    
    // Generate base return with regime characteristics
    const baseReturn = currentRegime.mu + currentRegime.sigma * sampleNormal();
    
    // Add autocorrelation and some fat-tail effect
    let dailyReturn = baseReturn + autoCorrelation;
    
    // Add occasional jumps for more realistic fat tails
    if (Math.random() < 0.02) { // 2% chance of jump
      dailyReturn += (Math.random() - 0.5) * 0.05; // Large move
    }

    // Update price
    currentPrice = currentPrice * (1 + dailyReturn);
    
    // Generate OHLCV with some randomness
    const open = i > 0 ? data[i-1].close : currentPrice;
    const high = open * (1 + Math.abs(dailyReturn) * (0.7 + Math.random() * 0.3));
    const low = open * (1 - Math.abs(dailyReturn) * (0.7 + Math.random() * 0.3));
    const close = currentPrice;
    const volume = Math.floor(100000000 + Math.random() * 200000000); // Volume in crores

    data.push({
      date: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      open,
      high,
      low,
      close,
      volume,
      returns: dailyReturn,
      realized_vol_20d: undefined, // Will calculate later
      momentum_5d: undefined, // Will calculate later
      vix_zscore: undefined // Will calculate later
    });
  }

  // Calculate rolling statistics after generating all data
  for (let i = 0; i < data.length; i++) {
    // Calculate realized volatility (20-day)
    if (i >= 19) {
      const returns = data.slice(i-19, i+1).map(d => d.returns || 0);
      const meanReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
      const variance = returns.reduce((a, b) => a + Math.pow(b - meanReturn, 2), 0) / returns.length;
      data[i].realized_vol_20d = Math.sqrt(variance) * Math.sqrt(252); // Annualized
    }

    // Calculate momentum (5-day)
    if (i >= 4) {
      const startPrice = data[i-4].close;
      const endPrice = data[i].close;
      data[i].momentum_5d = (endPrice - startPrice) / startPrice;
    }

    // Calculate VIX-like measure (just as a proxy)
    if (i >= 19) {
      data[i].vix_zscore = (data[i].realized_vol_20d! - 0.18) / 0.05; // Normalize to z-score
    }
  }

  return data;
};

// Helper function to sample from normal distribution
function sampleNormal(): number {
  // Box-Muller transformation
  const u1 = Math.random();
  const u2 = Math.random();
  return Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
}

// Function to generate news sentiment data
export const generateNewsData = (days: number): any[] => {
  const news: any[] = [];
  
  for (let i = 0; i < days; i++) {
    const date = new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000);
    
    // Generate 2-5 news items per day
    const numNewsItems = Math.floor(Math.random() * 4) + 2;
    
    for (let j = 0; j < numNewsItems; j++) {
      const hour = 9 + Math.floor(Math.random() * 4); // Between 9 AM and 1 PM
      const minute = Math.floor(Math.random() * 60);
      
      news.push({
        date: new Date(date.getFullYear(), date.getMonth(), date.getDate(), hour, minute).toISOString(),
        headline: generateRandomHeadline(),
        sentiment: (Math.random() * 2) - 1, // -1 to +1
        category: getRandomCategory()
      });
    }
  }
  
  return news;
};

// Helper function to generate random headlines
function generateRandomHeadline(): string {
  const subjects = ['Markets', 'Economy', 'Policy', 'Inflation', 'Interest Rates', 'Global Markets', 'Corporate Earnings', 'Banking', 'Tech Stocks', 'Crude Oil'];
  const verbs = ['Surge', 'Plunge', 'Rally', 'Decline', 'Hold Steady', 'Fluctuate', 'Soar', 'Tumble', 'Stabilize', 'Remain Volatile'];
  const objects = ['on Strong GDP', 'on Weak Data', 'on Policy Changes', 'on Global Concerns', 'on Inflation Worries', 'on Corporate Results', 'on Fed Signals', 'on Oil Prices', 'on Currency Moves', 'on Sector Rotation'];
  
  const subject = subjects[Math.floor(Math.random() * subjects.length)];
  const verb = verbs[Math.floor(Math.random() * verbs.length)];
  const object = objects[Math.floor(Math.random() * objects.length)];
  
  return `${subject} ${verb} ${object}`;
}

// Helper function to get random category
function getRandomCategory(): string {
  const categories = ['Economic', 'Policy', 'Corporate', 'Global', 'Sectoral', 'Commodity'];
  return categories[Math.floor(Math.random() * categories.length)];
}

// Function to generate macro data
export const generateMacroData = (days: number): any[] => {
  const macro: any[] = [];
  let currentVIX = 18 + Math.random() * 5; // Start VIX between 18-23
  let currentRate = 6 + Math.random() * 1; // Interest rate around 6-7%
  let currentFX = 82 + Math.random() * 2; // USD/INR around 82-84
  let currentOil = 75 + Math.random() * 10; // Oil price around 75-85
  
  for (let i = 0; i < days; i++) {
    // Mean-reverting processes for macro variables
    currentVIX = Math.max(12, Math.min(35, currentVIX + (Math.random() - 0.5) * 2 + (18 - currentVIX) * 0.1));
    currentRate = Math.max(5, Math.min(8, currentRate + (Math.random() - 0.5) * 0.1 + (6.5 - currentRate) * 0.05));
    currentFX = Math.max(78, Math.min(86, currentFX + (Math.random() - 0.5) * 0.2 + (82 - currentFX) * 0.02));
    currentOil = Math.max(60, Math.min(90, currentOil + (Math.random() - 0.5) * 1 + (75 - currentOil) * 0.03));
    
    macro.push({
      date: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      vix: currentVIX,
      interest_rate: currentRate,
      usd_inr: currentFX,
      crude_oil: currentOil,
      fii_flows: (Math.random() - 0.5) * 1000 // FII flows in crores
    });
  }
  
  return macro;
};