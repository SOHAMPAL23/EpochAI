import { Request, Response, NextFunction } from 'express';
import * as jwt from 'jsonwebtoken';

export const JWT_SECRET = process.env.JWT_SECRET || 'portfolio_super_secret_key_2026_agent';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    fullName: string;
    username: string;
    email: string;
    role: string;
  };
}

export function authenticateJWT(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.split(' ')[1];

    jwt.verify(token, JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.status(403).json({ error: 'Forbidden: Invalid or expired token' });
      }

      req.user = decoded as AuthenticatedRequest['user'];
      next();
    });
  } else {
    res.status(401).json({ error: 'Unauthorized: Missing auth credentials' });
  }
}

export function authorize(allowedRoles: string[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized: Authentication required' });
    }

    if (!allowedRoles.includes(req.user.role) && req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: You do not have permission to execute this scope' });
    }

    next();
  };
}
