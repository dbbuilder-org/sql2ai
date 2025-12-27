# SQL2.AI Project Notes

## Architecture

- **Monorepo:** NX workspace with npm workspaces
- **API:** FastAPI (Python 3.11) at `apps/api/`
- **App:** Next.js 14 at `apps/app/`
- **Shared:** Python utilities at `libs/shared/`

## Deployment (Render.com)

### Services
- **sql2ai-api:** Docker-based FastAPI service
- **sql2ai-app:** Node.js Next.js service
- **sql2ai-db:** PostgreSQL (basic-256mb plan)

### Environment Variables
- API uses `SQL2AI_` prefix for all env vars
- `SQL2AI_CORS_ORIGINS` must be JSON array format: `'["https://app.sql2.ai"]'`
- `SQL2AI_DATABASE_URL` is transformed at startup for asyncpg compatibility

### Build Commands
- API: Docker build from `apps/api/Dockerfile`
- App: `npm ci --include=dev && ./node_modules/.bin/nx build @sql2ai/app --configuration=production`
  - **Important:** `--include=dev` is required because NX is in devDependencies and Render sets NODE_ENV=production

### Known Issues
- NX project names are scoped: use `@sql2ai/app` not `app`
- Hatchling (Python build) requires README.md files in each package directory
- Dockerfile must explicitly COPY README.md for hatchling builds

## Development

### Running Locally
```bash
# API
cd apps/api && uvicorn sql2ai_api.main:app --reload

# App
npx nx serve @sql2ai/app
```

### Testing Builds Locally
```bash
# App
npm ci && ./node_modules/.bin/nx build @sql2ai/app --configuration=production

# API Docker
docker build -f apps/api/Dockerfile -t sql2ai-api .
```
