const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
import * as dotenv from 'dotenv';

import authController from './controllers/auth.controller';
import portfolioController from './controllers/portfolio.controller';
import transactionController from './controllers/transaction.controller';
import aiController from './controllers/ai.controller';
import analyticsController from './controllers/analytics.controller';
import adminController from './controllers/admin.controller';
import userController from './controllers/user.controller';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8000;


// Security and Parsers Middleware
app.use(helmet({
  crossOriginResourcePolicy: false
}));
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
}));
app.use(express.json());

// Routes Setup
app.use('/api/auth', authController);
app.use('/api/portfolio', portfolioController);
app.use('/api/transactions', transactionController);
app.use('/api/ai', aiController);
app.use('/api/analytics', analyticsController);
app.use('/api/admin', adminController);
app.use('/api/user', userController);

// Server Diagnostics
app.get('/api/health', (req: any, res: any) => {
  res.json({
    status: 'healthy',
    timestamp: new Date(),
    service: 'PortfolioOS AI Core API Server'
  });
});


app.listen(PORT, () => {
  console.log(`🚀 PortfolioOS AI Backend Core API Server listening on port ${PORT}`);
});

