# SQL2.AI Development Setup Guide

This guide covers setting up the SQL2.AI platform for local development.

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)
- Docker (optional, for containerized development)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/dbbuilder-org/sql2ai.git
cd sql2ai

# Install dependencies
npm install

# Copy environment files
cp apps/app/.env.example apps/app/.env.local
cp apps/site/.env.example apps/site/.env.local
cp apps/api/.env.example apps/api/.env

# Start development servers
npm run dev:site  # Marketing site on :3001
npm run dev:app   # App on :3000
npm run dev:api   # API on :8000
```

## Service Configuration

### 1. Clerk Authentication

1. Create an account at [clerk.com](https://clerk.com)
2. Create a new application
3. Configure OAuth providers (Google, GitHub, etc.)
4. Copy the API keys:

```env
# apps/app/.env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# apps/api/.env
SQL2AI_CLERK_SECRET_KEY=sk_test_...
SQL2AI_CLERK_PUBLISHABLE_KEY=pk_test_...
```

5. Configure webhooks (optional):
   - URL: `https://your-api-domain/api/webhooks/clerk`
   - Events: `user.created`, `user.updated`, `user.deleted`, `organization.*`

### 2. Sentry Error Monitoring

1. Create an account at [sentry.io](https://sentry.io)
2. Create projects for:
   - `sql2ai-app` (Next.js)
   - `sql2ai-site` (Next.js)
   - `sql2ai-api` (Python)
3. Copy the DSN values:

```env
# apps/app/.env.local
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# apps/site/.env.local
NEXT_PUBLIC_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# apps/api/.env
SQL2AI_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 3. Stripe Payments

1. Create an account at [stripe.com](https://stripe.com)
2. Get API keys from the Dashboard
3. Configure products and prices for each tier:
   - Free (free)
   - Team ($49/month)
   - Professional ($149/month)
   - Enterprise (custom)

```env
# apps/api/.env
SQL2AI_STRIPE_SECRET_KEY=sk_test_...
SQL2AI_STRIPE_PUBLISHABLE_KEY=pk_test_...
SQL2AI_STRIPE_WEBHOOK_SECRET=whsec_...
```

4. Configure webhook:
   - URL: `https://your-api-domain/api/webhooks/stripe`
   - Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb sql2ai_dev

# Run migrations
cd apps/api
alembic upgrade head

# Seed sample data (optional)
python scripts/seed.py --env development
```

### 5. AI/LLM Providers

```env
# apps/api/.env
SQL2AI_OPENAI_API_KEY=sk-...
SQL2AI_ANTHROPIC_API_KEY=sk-ant-...
SQL2AI_DEFAULT_LLM_MODEL=gpt-4
```

### 6. Email (Resend)

1. Create an account at [resend.com](https://resend.com)
2. Verify your domain
3. Get API key:

```env
# apps/site/.env.local
RESEND_API_KEY=re_...

# apps/api/.env
SQL2AI_RESEND_API_KEY=re_...
SQL2AI_RESEND_FROM_EMAIL=noreply@sql2.ai
```

## Development Commands

```bash
# Start all services
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# View dependency graph
npm run graph
```

## Architecture

```
sql2ai/
├── apps/
│   ├── api/          # FastAPI backend
│   ├── app/          # Next.js dashboard
│   └── site/         # Next.js marketing site
├── libs/
│   ├── schema-engine/     # Database schema extraction
│   ├── sql-orchestrator/  # Monitoring and checks
│   ├── sql-migrator/      # Migration generation
│   ├── sql-optimize/      # Query optimization
│   ├── sql-compliance/    # Compliance scanning
│   ├── sql-writer/        # AI code generation
│   ├── sql-code-review/   # Code review
│   └── sql-version/       # Version control
├── docs/             # Documentation
└── packages/         # Shared packages
```

## Deployment

### Marketing Site (Render)

The marketing site auto-deploys to Render on push to `main`:
- URL: https://sql2.ai
- Build command: `npm install && bash apps/site/scripts/build.sh`
- Publish directory: `dist/apps/site/.next`

### App & API

Deploy to your preferred platform:
- Vercel (App)
- Render/Railway/Fly.io (API)
- AWS/GCP/Azure (both)

## Troubleshooting

### Common Issues

1. **Clerk authentication not working**
   - Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set
   - Check that the domain is added to Clerk's allowed origins

2. **API connection failed**
   - Verify `API_URL` in `.env.local`
   - Check that the API is running on port 8000

3. **Database connection issues**
   - Ensure PostgreSQL is running
   - Check `SQL2AI_DATABASE_URL` format

## Support

- GitHub Issues: https://github.com/dbbuilder-org/sql2ai/issues
- Documentation: https://sql2.ai/docs
- Email: support@sql2.ai
