import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import PublicPortfolio from './components/Dashboard/PublicPortfolio';
import './App.css';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App min-h-screen bg-[#060913] text-slate-100 font-sans antialiased overflow-x-hidden">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/p/:username" element={<PublicPortfolio />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;