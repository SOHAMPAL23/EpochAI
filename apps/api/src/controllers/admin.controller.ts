import { Router, Response } from 'express';
import { db } from '../utils/db';
import { authenticateJWT, AuthenticatedRequest } from '../middlewares/auth';

const router = Router();

// Middleware: Strictly Admin-Only
const adminOnly = (req: AuthenticatedRequest, res: Response, next: any) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized: Authentication required' });
  }
  if (req.user.role !== 'ADMIN') {
    return res.status(403).json({ error: 'Forbidden: Admin privilege required' });
  }
  next();
};

// GET /api/admin/stats - Admin Dashboard Metrics
router.get('/stats', authenticateJWT as any, adminOnly, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const totalUsers = db.users.length;
    const totalPortfolios = db.portfolios.length;
    const totalPositions = db.projects.length;
    const totalTransactions = db.transactions.length;
    const transactionVolume = db.transactions.reduce((acc, tx) => acc + tx.amount, 0);

    return res.json({
      totalUsers,
      totalPortfolios,
      totalPositions,
      totalTransactions,
      transactionVolume
    });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to retrieve admin stats: ' + error.message });
  }
});

// GET /api/admin/users - List all users in system
router.get('/users', authenticateJWT as any, adminOnly, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const usersList = db.users.map(u => ({
      id: u.id,
      fullName: u.fullName,
      username: u.username,
      email: u.email,
      role: u.role,
      isVerified: u.isVerified,
      createdAt: u.createdAt
    }));

    return res.json({ users: usersList });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to retrieve system users: ' + error.message });
  }
});

// POST /api/admin/users/:id/toggle-verify - Admin toggle verification
router.post('/users/:id/toggle-verify', authenticateJWT as any, adminOnly, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.params.id;
    const user = db.users.find(u => u.id === userId);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    user.isVerified = !user.isVerified;
    
    // Sync DB triggers
    if (typeof (db as any).syncUser === 'function') {
      await (db as any).syncUser(user);
    }

    return res.json({ status: 'success', message: `User verification toggled to ${user.isVerified}`, isVerified: user.isVerified });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to toggle verification: ' + error.message });
  }
});

// POST /api/admin/users/:id/role - Admin change user role
router.post('/users/:id/role', authenticateJWT as any, adminOnly, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.params.id;
    const { role } = req.body;

    if (!role || !['USER', 'PREMIUM_USER', 'ADMIN'].includes(role)) {
      return res.status(400).json({ error: 'Invalid or missing role parameter' });
    }

    const user = db.users.find(u => u.id === userId);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    user.role = role;

    // Sync DB triggers
    if (typeof (db as any).syncUser === 'function') {
      await (db as any).syncUser(user);
    }

    return res.json({ status: 'success', message: `User role modified to ${user.role}`, role: user.role });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to alter user role: ' + error.message });
  }
});

export default router;
