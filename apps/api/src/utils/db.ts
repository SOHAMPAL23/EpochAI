import { Pool } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config();

const connectionString = process.env.DATABASE_URL;

// Define Interface schemas
export interface User {
  id: string;
  fullName: string;
  username: string;
  email: string;
  passwordHash: string;
  avatarUrl?: string;
  bio?: string;
  role: string;
  isVerified: boolean;
  twoFactorEnabled: boolean;
  createdAt: Date;
}

export interface Portfolio {
  id: string;
  userId: string;
  title: string;
  description?: string;
  theme: string;
  slug: string;
  isPublic: boolean;
  views: number;
  likes: number;
  createdAt: Date;
}

export interface Project {
  id: string;
  portfolioId: string;
  title: string;
  description?: string;
  techStack: string;
  githubUrl?: string;
  liveUrl?: string;
  imageUrl?: string;
  featured: boolean;
  createdAt: Date;
}

export interface Transaction {
  id: string;
  userId: string;
  amount: number;
  type: 'INCOME' | 'EXPENSE';
  category: string;
  notes?: string;
  createdAt: Date;
}

export interface Skill {
  id: string;
  portfolioId: string;
  name: string;
  level: number;
}

export interface Experience {
  id: string;
  portfolioId: string;
  company: string;
  role: string;
  startDate: string;
  endDate?: string;
  description?: string;
}

export interface SocialLink {
  id: string;
  portfolioId: string;
  platform: string;
  url: string;
}

export interface Analytics {
  id: string;
  portfolioId: string;
  visitors: number;
  clicks: number;
  impressions: number;
  engagementRate: number;
  recordedDate: Date;
}

class DatabaseSandbox {
  users: User[] = [];
  portfolios: Portfolio[] = [];
  projects: Project[] = [];
  transactions: Transaction[] = [];
  skills: Skill[] = [];
  experiences: Experience[] = [];
  socialLinks: SocialLink[] = [];
  analytics: Analytics[] = [];

  private pool: Pool | null = null;
  private isInitialized = false;

  constructor() {
    if (connectionString) {
      console.log('🔌 Connecting to Neon PostgreSQL Cluster...');
      this.pool = new Pool({
        connectionString,
        ssl: {
          rejectUnauthorized: false
        }
      });
      this.initializePostgres();
    } else {
      console.warn('⚠️ No DATABASE_URL found in environment. Falling back to sandbox mode.');
      this.seedLocalFallback();
    }

    // High-performance background sync loop (every 500ms) to ensure in-memory adjustments are saved to PostgreSQL
    setInterval(() => {
      if (this.isInitialized && this.pool) {
        this.persistAllToPostgres();
      }
    }, 500);
  }

  private async initializePostgres() {
    try {
      if (!this.pool) return;

      // 1. Create Tables
      await this.pool.query(`
        CREATE TABLE IF NOT EXISTS users (
          id VARCHAR(255) PRIMARY KEY,
          "fullName" VARCHAR(255) NOT NULL,
          username VARCHAR(255) UNIQUE NOT NULL,
          email VARCHAR(255) UNIQUE NOT NULL,
          "passwordHash" VARCHAR(255) NOT NULL,
          "avatarUrl" TEXT,
          bio TEXT,
          role VARCHAR(255) NOT NULL,
          "isVerified" BOOLEAN NOT NULL DEFAULT FALSE,
          "twoFactorEnabled" BOOLEAN NOT NULL DEFAULT FALSE,
          "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS portfolios (
          id VARCHAR(255) PRIMARY KEY,
          "userId" VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          title VARCHAR(255) NOT NULL,
          description TEXT,
          theme VARCHAR(255) NOT NULL,
          slug VARCHAR(255) UNIQUE NOT NULL,
          "isPublic" BOOLEAN NOT NULL DEFAULT TRUE,
          views INTEGER NOT NULL DEFAULT 0,
          likes INTEGER NOT NULL DEFAULT 0,
          "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
          id VARCHAR(255) PRIMARY KEY,
          "portfolioId" VARCHAR(255) NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          title VARCHAR(255) NOT NULL,
          description TEXT,
          "techStack" VARCHAR(255) NOT NULL,
          "githubUrl" VARCHAR(255),
          "liveUrl" VARCHAR(255),
          "imageUrl" TEXT,
          featured BOOLEAN NOT NULL DEFAULT FALSE,
          "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
          id VARCHAR(255) PRIMARY KEY,
          "userId" VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          amount NUMERIC NOT NULL,
          type VARCHAR(50) NOT NULL,
          category VARCHAR(255) NOT NULL,
          notes TEXT,
          "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS skills (
          id VARCHAR(255) PRIMARY KEY,
          "portfolioId" VARCHAR(255) NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          name VARCHAR(255) NOT NULL,
          level INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS experiences (
          id VARCHAR(255) PRIMARY KEY,
          "portfolioId" VARCHAR(255) NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          company VARCHAR(255) NOT NULL,
          role VARCHAR(255) NOT NULL,
          "startDate" VARCHAR(255) NOT NULL,
          "endDate" VARCHAR(255),
          description TEXT
        );

        CREATE TABLE IF NOT EXISTS social_links (
          id VARCHAR(255) PRIMARY KEY,
          "portfolioId" VARCHAR(255) NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          platform VARCHAR(255) NOT NULL,
          url TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS analytics (
          id VARCHAR(255) PRIMARY KEY,
          "portfolioId" VARCHAR(255) NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
          visitors INTEGER NOT NULL,
          clicks INTEGER NOT NULL,
          impressions INTEGER NOT NULL,
          "engagementRate" NUMERIC NOT NULL,
          "recordedDate" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      `);

      // 2. Check if users are empty; if so, seed PostgreSQL
      const userCheck = await this.pool.query('SELECT COUNT(*) FROM users');
      const userCount = parseInt(userCheck.rows[0].count);

      if (userCount === 0) {
        console.log('🌱 Seeding Neon PostgreSQL Database with default records...');
        await this.seedPostgresDb();
      }

      // 3. Load all tables into memory for synchronous access compatibility
      await this.loadFromPostgres();
      this.isInitialized = true;
      console.log('✅ PostgreSQL connected, schemas created/synced successfully!');
    } catch (err: any) {
      console.error('❌ Failed to initialize PostgreSQL. Falling back to local arrays.', err);
      this.seedLocalFallback();
    }
  }

  private seedLocalFallback() {
    const userJohn: User = {
      id: 'usr_john',
      fullName: 'John Doe',
      username: 'john_doe',
      email: 'john@portfolioos.ai',
      passwordHash: '$2a$10$tQ20qR8d32uUqD/7Q3PaeO3kY2i.fHlKz6H1wXo8aQ3wDqL5n3D8i',
      avatarUrl: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150',
      bio: 'Senior Full-Stack Architect & AI Specialist crafting glassmorphic terminals.',
      role: 'PREMIUM_USER',
      isVerified: true,
      twoFactorEnabled: false,
      createdAt: new Date()
    };

    const userJane: User = {
      id: 'usr_jane',
      fullName: 'Jane Smith',
      username: 'jane_smith',
      email: 'jane@portfolioos.ai',
      passwordHash: '$2a$10$tQ20qR8d32uUqD/7Q3PaeO3kY2i.fHlKz6H1wXo8aQ3wDqL5n3D8i',
      avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
      bio: 'Creative Director & Brand Architect designing responsive digital aesthetics.',
      role: 'USER',
      isVerified: true,
      twoFactorEnabled: false,
      createdAt: new Date()
    };

    const userAdmin: User = {
      id: 'usr_admin',
      fullName: 'Admin Operations',
      username: 'admin_ops',
      email: 'admin@portfolioos.ai',
      passwordHash: '$2a$10$tQ20qR8d32uUqD/7Q3PaeO3kY2i.fHlKz6H1wXo8aQ3wDqL5n3D8i',
      bio: 'Global PortfolioOS System Operations Management Administrator.',
      role: 'ADMIN',
      isVerified: true,
      twoFactorEnabled: true,
      createdAt: new Date()
    };

    const userSoham: User = {
      id: 'usr_spall',
      fullName: 'Soham Pal',
      username: 'spall',
      email: 'soham@epoch.ai',
      passwordHash: '$2a$10$tQ20qR8d32uUqD/7Q3PaeO3kY2i.fHlKz6H1wXo8aQ3wDqL5n3D8i',
      bio: 'Custom SaaS business and project portfolio operating systems.',
      role: 'USER',
      isVerified: true,
      twoFactorEnabled: false,
      createdAt: new Date()
    };

    this.users.push(userJohn, userJane, userAdmin, userSoham);

    // Portfolios fallback
    this.portfolios.push(
      { id: 'port_john', userId: 'usr_john', title: 'John Doe | Senior Full-Stack Architect', description: 'Pioneering Web3 terminals.', theme: 'glassmorphism', slug: 'john_doe', isPublic: true, views: 1240, likes: 86, createdAt: new Date() },
      { id: 'port_jane', userId: 'usr_jane', title: 'Jane Smith | Creative Director', description: 'Responsive layouts.', theme: 'dark-cyber', slug: 'jane_smith', isPublic: true, views: 890, likes: 54, createdAt: new Date() },
      { id: 'port_spall', userId: 'usr_spall', title: 'Soham Pal | PortfolioOS Showcase', description: 'Custom SaaS portfolios.', theme: 'glassmorphism', slug: 'spall', isPublic: true, views: 6, likes: 0, createdAt: new Date() }
    );

    // Seed mock active holdings
    this.projects.push(
      { id: 'proj_1', portfolioId: 'port_john', title: 'AAPL', description: 'Core hardware and services position.', techStack: 'Stock', githubUrl: '145.20', liveUrl: '25', featured: true, createdAt: new Date() },
      { id: 'proj_2', portfolioId: 'port_john', title: 'BTC-USD', description: 'Decentralized scarce store of value.', techStack: 'Cryptocurrency', githubUrl: '58400.00', liveUrl: '0.15', featured: true, createdAt: new Date() },
      { id: 'proj_3', portfolioId: 'port_spall', title: 'AAPL', description: 'Core hardware and services position.', techStack: 'Stock', githubUrl: '145.20', liveUrl: '25', featured: true, createdAt: new Date() },
      { id: 'proj_4', portfolioId: 'port_spall', title: 'BTC-USD', description: 'Decentralized scarce store of value.', techStack: 'Cryptocurrency', githubUrl: '58400.00', liveUrl: '0.15', featured: true, createdAt: new Date() }
    );
  }

  private async seedPostgresDb() {
    if (!this.pool) return;
    
    // Create local fallbacks in memory, then persist
    this.seedLocalFallback();

    // Insert Users
    for (const u of this.users) {
      await this.pool.query(
        'INSERT INTO users (id, "fullName", username, email, "passwordHash", "avatarUrl", bio, role, "isVerified", "twoFactorEnabled", "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) ON CONFLICT (id) DO NOTHING',
        [u.id, u.fullName, u.username, u.email, u.passwordHash, u.avatarUrl || null, u.bio || null, u.role, u.isVerified, u.twoFactorEnabled, u.createdAt]
      );
    }

    // Insert Portfolios
    for (const p of this.portfolios) {
      await this.pool.query(
        'INSERT INTO portfolios (id, "userId", title, description, theme, slug, "isPublic", views, likes, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) ON CONFLICT (id) DO NOTHING',
        [p.id, p.userId, p.title, p.description || null, p.theme, p.slug, p.isPublic, p.views, p.likes, p.createdAt]
      );
    }

    // Insert Projects
    for (const prj of this.projects) {
      await this.pool.query(
        'INSERT INTO projects (id, "portfolioId", title, description, "techStack", "githubUrl", "liveUrl", "imageUrl", featured, "createdAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) ON CONFLICT (id) DO NOTHING',
        [prj.id, prj.portfolioId, prj.title, prj.description || null, prj.techStack, prj.githubUrl || null, prj.liveUrl || null, prj.imageUrl || null, prj.featured, prj.createdAt]
      );
    }
  }

  private async loadFromPostgres() {
    if (!this.pool) return;

    const uRes = await this.pool.query('SELECT * FROM users');
    this.users = uRes.rows.map(r => ({
      id: r.id,
      fullName: r.fullName,
      username: r.username,
      email: r.email,
      passwordHash: r.passwordHash,
      avatarUrl: r.avatarUrl,
      bio: r.bio,
      role: r.role,
      isVerified: r.isVerified,
      twoFactorEnabled: r.twoFactorEnabled,
      createdAt: new Date(r.createdAt)
    }));

    const pRes = await this.pool.query('SELECT * FROM portfolios');
    this.portfolios = pRes.rows.map(r => ({
      id: r.id,
      userId: r.userId,
      title: r.title,
      description: r.description,
      theme: r.theme,
      slug: r.slug,
      isPublic: r.isPublic,
      views: r.views,
      likes: r.likes,
      createdAt: new Date(r.createdAt)
    }));

    const projRes = await this.pool.query('SELECT * FROM projects');
    this.projects = projRes.rows.map(r => ({
      id: r.id,
      portfolioId: r.portfolioId,
      title: r.title,
      description: r.description,
      techStack: r.techStack,
      githubUrl: r.githubUrl,
      liveUrl: r.liveUrl,
      imageUrl: r.imageUrl,
      featured: r.featured,
      createdAt: new Date(r.createdAt)
    }));

    const txRes = await this.pool.query('SELECT * FROM transactions');
    this.transactions = txRes.rows.map(r => ({
      id: r.id,
      userId: r.userId,
      amount: parseFloat(r.amount),
      type: r.type,
      category: r.category,
      notes: r.notes,
      createdAt: new Date(r.createdAt)
    }));
  }

  // Persists the complete local state to PostgreSQL (updates existings, inserts new, deletes removed)
  private async persistAllToPostgres() {
    if (!this.pool) return;
    try {
      // 1. Sync Users
      for (const u of this.users) {
        await this.pool.query(
          `INSERT INTO users (id, "fullName", username, email, "passwordHash", "avatarUrl", bio, role, "isVerified", "twoFactorEnabled", "createdAt")
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
           ON CONFLICT (id) DO UPDATE SET
             "fullName" = EXCLUDED."fullName",
             username = EXCLUDED.username,
             email = EXCLUDED.email,
             "passwordHash" = EXCLUDED."passwordHash",
             "avatarUrl" = EXCLUDED."avatarUrl",
             bio = EXCLUDED.bio,
             role = EXCLUDED.role,
             "isVerified" = EXCLUDED."isVerified",
             "twoFactorEnabled" = EXCLUDED."twoFactorEnabled"`,
          [u.id, u.fullName, u.username, u.email, u.passwordHash, u.avatarUrl || null, u.bio || null, u.role, u.isVerified, u.twoFactorEnabled, u.createdAt]
        );
      }

      // 2. Sync Portfolios
      for (const p of this.portfolios) {
        await this.pool.query(
          `INSERT INTO portfolios (id, "userId", title, description, theme, slug, "isPublic", views, likes, "createdAt")
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
           ON CONFLICT (id) DO UPDATE SET
             title = EXCLUDED.title,
             description = EXCLUDED.description,
             theme = EXCLUDED.theme,
             slug = EXCLUDED.slug,
             "isPublic" = EXCLUDED."isPublic",
             views = EXCLUDED.views,
             likes = EXCLUDED.likes`,
          [p.id, p.userId, p.title, p.description || null, p.theme, p.slug, p.isPublic, p.views, p.likes, p.createdAt]
        );
      }

      // 3. Sync Projects
      // Delete any project in postgres not in local memory
      const localProjectIds = this.projects.map(p => p.id);
      if (localProjectIds.length > 0) {
        await this.pool.query('DELETE FROM projects WHERE id NOT IN (' + localProjectIds.map((_, i) => `$${i + 1}`).join(',') + ')', localProjectIds);
      } else {
        await this.pool.query('DELETE FROM projects');
      }

      for (const prj of this.projects) {
        await this.pool.query(
          `INSERT INTO projects (id, "portfolioId", title, description, "techStack", "githubUrl", "liveUrl", "imageUrl", featured, "createdAt")
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
           ON CONFLICT (id) DO UPDATE SET
             title = EXCLUDED.title,
             description = EXCLUDED.description,
             "techStack" = EXCLUDED."techStack",
             "githubUrl" = EXCLUDED."githubUrl",
             "liveUrl" = EXCLUDED."liveUrl",
             "imageUrl" = EXCLUDED."imageUrl",
             featured = EXCLUDED.featured`,
          [prj.id, prj.portfolioId, prj.title, prj.description || null, prj.techStack, prj.githubUrl || null, prj.liveUrl || null, prj.imageUrl || null, prj.featured, prj.createdAt]
        );
      }

      // 4. Sync Transactions
      const localTxIds = this.transactions.map(t => t.id);
      if (localTxIds.length > 0) {
        await this.pool.query('DELETE FROM transactions WHERE id NOT IN (' + localTxIds.map((_, i) => `$${i + 1}`).join(',') + ')', localTxIds);
      } else {
        await this.pool.query('DELETE FROM transactions');
      }

      for (const tx of this.transactions) {
        await this.pool.query(
          `INSERT INTO transactions (id, "userId", amount, type, category, notes, "createdAt")
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           ON CONFLICT (id) DO UPDATE SET
             amount = EXCLUDED.amount,
             type = EXCLUDED.type,
             category = EXCLUDED.category,
             notes = EXCLUDED.notes`,
          [tx.id, tx.userId, tx.amount, tx.type, tx.category, tx.notes || null, tx.createdAt]
        );
      }

    } catch (err) {
      console.error('⚠️ Background PostgreSQL sync failed:', err);
    }
  }

  // Explicit sync helpers called by mutations
  async syncUser(user: User) {
    if (!this.pool) return;
    await this.pool.query(
      'UPDATE users SET "fullName"=$1, username=$2, email=$3, role=$4, "isVerified"=$5, "twoFactorEnabled"=$6 WHERE id=$7',
      [user.fullName, user.username, user.email, user.role, user.isVerified, user.twoFactorEnabled, user.id]
    );
  }
}

export const db = new DatabaseSandbox();
