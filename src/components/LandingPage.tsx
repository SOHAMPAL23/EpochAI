import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Zap, Brain, Eye } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 flex flex-col items-center justify-center p-4">
      <div className="max-w-4xl w-full text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
            Multi-Modal
          </span>{' '}
          <span className="text-white">Forecasting Engine</span>
        </h1>
        
        <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
          Advanced AI-powered financial forecasting with real-time market analysis, 
          sentiment processing, and explainable AI insights.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <TrendingUp className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-white font-semibold mb-2">Transformer Models</h3>
            <p className="text-gray-400 text-sm">Temporal Fusion Transformers for sequence prediction</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Brain className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-white font-semibold mb-2">Hidden Markov</h3>
            <p className="text-gray-400 text-sm">Regime detection with 85%+ accuracy</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Zap className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-white font-semibold mb-2">NLP Processing</h3>
            <p className="text-gray-400 text-sm">Real-time news sentiment analysis</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <Eye className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-white font-semibold mb-2">Explainable AI</h3>
            <p className="text-gray-400 text-sm">SHAP values and attention heatmaps</p>
          </div>
        </div>
        
        <Link 
          to="/dashboard"
          className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl hover:from-cyan-600 hover:to-blue-700 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-cyan-500/25"
        >
          Launch Dashboard
          <svg xmlns="http://www.w3.org/2000/svg" className="ml-2 h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </Link>
      </div>
    </div>
  );
};

export default LandingPage;