import { Router, Response } from 'express';
import { db } from '../utils/db';
import { authenticateJWT, AuthenticatedRequest } from '../middlewares/auth';

const router = Router();

// Middleware: Strictly User-Only (reject ADMINs)
const userOnly = (req: AuthenticatedRequest, res: Response, next: any) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized: Authentication required' });
  }
  
  const allowedRoles = ['USER', 'PREMIUM_USER'];
  if (!allowedRoles.includes(req.user.role)) {
    return res.status(403).json({ error: 'Forbidden: Standard or Premium User scope required. Admins restricted.' });
  }
  next();
};

// GET /api/user/profile - User profile info access
router.get('/profile', authenticateJWT as any, userOnly, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const user = db.users.find(u => u.id === req.user!.id);
    if (!user) {
      return res.status(404).json({ error: 'User profile not found' });
    }

    return res.json({
      status: 'success',
      profile: {
        id: user.id,
        fullName: user.fullName,
        username: user.username,
        email: user.email,
        bio: user.bio,
        role: user.role,
        isVerified: user.isVerified
      }
    });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to fetch profile settings: ' + error.message });
  }
});

export default router;
