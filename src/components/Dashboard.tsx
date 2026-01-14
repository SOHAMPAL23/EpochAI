import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ForecastCard from './ForecastCard';
import ReturnDistributionChart from './charts/ReturnDistributionChart';
import RegimeChart from './charts/RegimeChart';
import RiskMetrics from './RiskMetrics';
import ExplainabilityTabs from './ExplainabilityTabs';
import HistoricalPerformance from './HistoricalPerformance';
import { generateSyntheticData } from '../utils/dataGenerator';
import { trainModels, makePrediction } from '../utils/modelEngine';
import { ForecastOutput } from '../types';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [forecast, setForecast] = useState<ForecastOutput | null>(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [selectedAsset, setSelectedAsset] = useState('NIFTY50');
  const [horizon, setHorizon] = useState('1D');
  const [sentimentEnabled, setSentimentEnabled] = useState(true);
  const [regimeEnabled, setRegimeEnabled] = useState(true);
  const [explanationsEnabled, setExplanationsEnabled] = useState(true);

  useEffect(() => {
    // Initialize the dashboard with synthetic data
    initializeDashboard();
  }, []);

  const initializeDashboard = async () => {
    try {
      setLoading(true);
      
      // Generate synthetic market data
      const data = generateSyntheticData(756); // 3 years of data
      setHistoricalData(data);
      
      // Train models
      await trainModels(data);
      
      // Make initial prediction
      const prediction = makePrediction(data.slice(-30), {
        sentimentEnabled,
        regimeEnabled,
        explanationsEnabled
      });
      
      setForecast(prediction);
    } catch (error) {
      console.error('Error initializing dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateForecast = async () => {
    try {
      setLoading(true);
      
      // Make new prediction with current settings
      const prediction = makePrediction(historicalData.slice(-30), {
        sentimentEnabled,
        regimeEnabled,
        explanationsEnabled
      });
      
      setForecast(prediction);
    } catch (error) {
      console.error('Error generating forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Initializing forecasting engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <Sidebar
            selectedAsset={selectedAsset}
            setSelectedAsset={setSelectedAsset}
            horizon={horizon}
            setHorizon={setHorizon}
            sentimentEnabled={sentimentEnabled}
            setSentimentEnabled={setSentimentEnabled}
            regimeEnabled={regimeEnabled}
            setRegimeEnabled={setRegimeEnabled}
            explanationsEnabled={explanationsEnabled}
            setExplanationsEnabled={setExplanationsEnabled}
            onGenerateForecast={handleGenerateForecast}
            loading={loading}
          />

          {/* Main Content */}
          <div className="flex-1 space-y-6">
            {/* Forecast Card */}
            {forecast && <ForecastCard forecast={forecast} />}

            {/* Charts Row */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <ReturnDistributionChart forecast={forecast} />
              <RegimeChart forecast={forecast} />
            </div>

            {/* Risk Metrics */}
            {forecast && <RiskMetrics riskMetrics={forecast.risk_metrics} />}

            {/* Explainability Tabs */}
            {forecast && <ExplainabilityTabs forecast={forecast} />}

            {/* Historical Performance */}
            <HistoricalPerformance data={historicalData.slice(-90)} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;