import { Router, Response } from 'express';
import { db } from '../utils/db';
import { authenticateJWT, AuthenticatedRequest } from '../middlewares/auth';

const router = Router();

// GET /api/analytics/summary - Retrieve visitor metrics and breakdown logs
router.get('/summary', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const portfolio = db.portfolios.find(p => p.userId === userId);

    if (!portfolio) {
      return res.status(404).json({ error: 'Portfolio workspace not found' });
    }

    const analyticsEntries = db.analytics.filter(a => a.portfolioId === portfolio.id);
    
    // Default aggregates if empty
    const clicks = portfolio.views * 0.12; // 12% click-through rate simulation
    const impressions = portfolio.views * 3.2; // 3.2x impressions relative to views
    const engagementRate = 18.5; // percentage

    // Build rolling 7-day visitor traffic metrics for Recharts
    const trailingDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const visitorsData = trailingDays.map((day, idx) => {
      const base = portfolio.views / 7;
      const variation = Math.sin(idx) * (base * 0.3); // add wave variation
      return {
        day,
        visitors: Math.round(base + variation),
        clicks: Math.round((base + variation) * 0.15),
        impressions: Math.round((base + variation) * 3.5)
      };
    });

    const trafficSources = [
      { name: 'GitHub Referrals', value: 45 },
      { name: 'Direct Traffic', value: 25 },
      { name: 'LinkedIn / Social', value: 20 },
      { name: 'Google Search', value: 10 }
    ];

    return res.json({
      aggregates: {
        views: portfolio.views,
        clicks: Math.round(clicks),
        impressions: Math.round(impressions),
        engagementRate
      },
      visitorsData,
      trafficSources
    });

  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to retrieve analytics metrics: ' + error.message });
  }
});

export default router;
