import { Router, Request, Response } from 'express';
import { db, Project, Skill, Experience, SocialLink } from '../utils/db';
import { authenticateJWT, AuthenticatedRequest } from '../middlewares/auth';

const router = Router();

// GET /api/portfolio/me - Retrieve authenticated user's complete portfolio setup
router.get('/me', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const portfolio = db.portfolios.find(p => p.userId === userId);

    if (!portfolio) {
      return res.status(404).json({ error: 'Portfolio workspace not found' });
    }

    const projects = db.projects.filter(p => p.portfolioId === portfolio.id);
    const skills = db.skills.filter(s => s.portfolioId === portfolio.id);
    const experiences = db.experiences.filter(e => e.portfolioId === portfolio.id);
    const socialLinks = db.socialLinks.filter(sl => sl.portfolioId === portfolio.id);

    return res.json({
      portfolio,
      projects,
      skills,
      experiences,
      socialLinks
    });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to retrieve portfolio assets: ' + error.message });
  }
});

// PATCH /api/portfolio/update - Modify portfolio metadata or UI themes
router.patch('/update', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const portfolio = db.portfolios.find(p => p.userId === userId);

    if (!portfolio) {
      return res.status(404).json({ error: 'Portfolio workspace not found' });
    }

    const { title, description, theme, isPublic } = req.body;

    if (title !== undefined) portfolio.title = title;
    if (description !== undefined) portfolio.description = description;
    if (theme !== undefined) portfolio.theme = theme;
    if (isPublic !== undefined) portfolio.isPublic = isPublic;

    return res.json({ status: 'success', portfolio });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to update portfolio credentials: ' + error.message });
  }
});

// POST /api/portfolio/projects - Add a showcase project
router.post('/projects', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const portfolio = db.portfolios.find(p => p.userId === userId);

    if (!portfolio) {
      return res.status(404).json({ error: 'Portfolio workspace not found' });
    }

    const { title, description, techStack, githubUrl, liveUrl, imageUrl, featured } = req.body;

    if (!title) {
      return res.status(400).json({ error: 'Project title is mandatory' });
    }

    const newProject: Project = {
      id: 'proj_' + Math.random().toString(36).substr(2, 9),
      portfolioId: portfolio.id,
      title,
      description: description || '',
      techStack: techStack || '',
      githubUrl: githubUrl || '',
      liveUrl: liveUrl || '',
      imageUrl: imageUrl || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400',
      featured: !!featured,
      createdAt: new Date()
    };

    db.projects.push(newProject);
    return res.status(201).json({ status: 'success', project: newProject });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to insert project: ' + error.message });
  }
});

// DELETE /api/portfolio/projects/:id - Remove a project
router.delete('/projects/:id', authenticateJWT as any, (req: AuthenticatedRequest, res: Response) => {
  try {
    const userId = req.user!.id;
    const portfolio = db.portfolios.find(p => p.userId === userId);

    if (!portfolio) {
      return res.status(404).json({ error: 'Portfolio workspace not found' });
    }

    const projectId = req.params.id;
    const index = db.projects.findIndex(p => p.id === projectId && p.portfolioId === portfolio.id);

    if (index === -1) {
      return res.status(404).json({ error: 'Project not found in your portfolio' });
    }

    db.projects.splice(index, 1);
    return res.json({ status: 'success', message: 'Project removed successfully' });
  } catch (error: any) {
    return res.status(500).json({ error: 'Failed to delete project: ' + error.message });
  }
});

// GET /api/portfolio/public/:slug - Exposed Public View Route (View Count Tracking)
router.get('/public/:slug', (req: Request, res: Response) => {
  try {
    const slug = req.params.slug.trim().toLowerCase();
    const portfolio = db.portfolios.find(p => p.slug === slug);

    if (!portfolio || !portfolio.isPublic) {
      return res.status(404).json({ error: 'Public portfolio slug not found or restricted' });
    }

    // Dynamic analytics increment
    portfolio.views += 1;

    const user = db.users.find(u => u.id === portfolio.userId);
    const projects = db.projects.filter(p => p.portfolioId === portfolio.id);
    const skills = db.skills.filter(s => s.portfolioId === portfolio.id);
    const experiences = db.experiences.filter(e => e.portfolioId === portfolio.id);
    const socialLinks = db.socialLinks.filter(sl => sl.portfolioId === portfolio.id);

    return res.json({
      portfolio,
      user: user ? { fullName: user.fullName, bio: user.bio, avatarUrl: user.avatarUrl } : null,
      projects,
      skills,
      experiences,
      socialLinks
    });
  } catch (error: any) {
    return res.status(500).json({ error: 'Error pulling public portfolio: ' + error.message });
  }
});

export default router;

