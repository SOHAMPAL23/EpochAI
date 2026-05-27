import { Router, Request, Response } from 'express';
import * as bcrypt from 'bcryptjs';
import * as jwt from 'jsonwebtoken';
import { db, User } from '../utils/db';
import { JWT_SECRET, authenticateJWT, AuthenticatedRequest } from '../middlewares/auth';

const router = Router();

// POST /api/auth/register
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { fullName, username, email, password } = req.body;

    if (!fullName || !username || !email || !password) {
      return res.status(400).json({ error: 'Missing mandatory registration fields' });
    }

    const trimmedUsername = username.trim().toLowerCase();
    const trimmedEmail = email.trim().toLowerCase();

    // Check availability
    const exists = db.users.find(u => u.username === trimmedUsername || u.email === trimmedEmail);
    if (exists) {
      return res.status(409).json({ error: 'Username or Email is already registered' });
    }

    // Cryptography
    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(password, salt);

    const newUser: User = {
      id: 'usr_' + Math.random().toString(36).substr(2, 9),
      fullName,
      username: trimmedUsername,
      email: trimmedEmail,
      passwordHash,
      role: 'USER',
      isVerified: false,
      twoFactorEnabled: false,
      createdAt: new Date()
    };

    db.users.push(newUser);

    // Dynamic Default Portfolio Initialization
    const defaultPortfolio = {
      id: 'port_' + Math.random().toString(36).substr(2, 9),
      userId: newUser.id,
      title: `${newUser.fullName} | PortfolioOS Showcase`,
      description: 'Custom SaaS business and project portfolio operating systems.',
      theme: 'glassmorphism',
      slug: trimmedUsername,
      isPublic: true,
      views: 0,
      likes: 0,
      createdAt: new Date()
    };

    db.portfolios.push(defaultPortfolio);

    // Issue JWT
    const token = jwt.sign(
      {
        id: newUser.id,
        fullName: newUser.fullName,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role
      },
      JWT_SECRET,
      { expiresIn: '1d' }
    );

    return res.status(201).json({
      status: 'success',
      token,
      user: {
        id: newUser.id,
        fullName: newUser.fullName,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role
      }
    });

  } catch (error: any) {
    return res.status(500).json({ error: 'Internal Server Error: ' + error.message });
  }
});

// POST /api/auth/login
router.post('/login', async (req: Request, res: Response) => {

  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Missing mandatory email or password parameters' });
    }

    const trimmedEmail = email.trim().toLowerCase();
    const user = db.users.find(u => u.email === trimmedEmail);

    if (!user) {
      return res.status(401).json({ error: 'Unauthorized: Invalid email or password credentials' });
    }

    const validPassword = await bcrypt.compare(password, user.passwordHash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Unauthorized: Invalid email or password credentials' });
    }

    // Issue JWT
    const token = jwt.sign(
      {
        id: user.id,
        fullName: user.fullName,
        username: user.username,
        email: user.email,
        role: user.role
      },
      JWT_SECRET,
      { expiresIn: '1d' }
    );

    return res.json({
      status: 'success',
      token,
      user: {
        id: user.id,
        fullName: user.fullName,
        username: user.username,
        email: user.email,
        role: user.role,
        bio: user.bio,
        avatarUrl: user.avatarUrl
      }
    });

  } catch (error: any) {
    return res.status(500).json({ error: 'Internal Server Error: ' + error.message });
  }
});

// GET /api/auth/me
router.get('/me', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  return res.json({ user: req.user });
});

export default router;
