# SQL2.AI Project Notes

## Architecture

- **Monorepo:** NX workspace with npm workspaces
- **API:** FastAPI (Python 3.11) at `apps/api/`
- **App:** Next.js 14 at `apps/app/`
- **Shared:** Python utilities at `libs/shared/`

## Deployment (Render.com)

### Services
- **sql2ai-api:** Docker-based FastAPI service (https://sql2ai-api.onrender.com)
- **sql2ai-app:** Node.js Next.js service (https://sql2ai-app.onrender.com)
- **sql2ai-db:** PostgreSQL (basic-256mb plan, Oregon region)

### Environment Variables
- API uses `SQL2AI_` prefix for all env vars
- `SQL2AI_CORS_ORIGINS` must be JSON array format: `'["https://app.sql2.ai","https://sql2.ai","http://localhost:3000"]'`
  - Pydantic-settings expects JSON for List types, NOT comma-separated strings
- `SQL2AI_DATABASE_URL` is transformed at startup for asyncpg compatibility
- Secrets (sync: false in render.yaml) must be set manually in Render dashboard:
  - `SQL2AI_CLERK_SECRET_KEY`
  - `SQL2AI_CLERK_PUBLISHABLE_KEY`
  - `SQL2AI_OPENAI_API_KEY`
  - `SQL2AI_ANTHROPIC_API_KEY`
  - `SQL2AI_STRIPE_SECRET_KEY`
  - `SQL2AI_STRIPE_WEBHOOK_SECRET`
  - `SQL2AI_SENTRY_DSN`

### Build Commands
- API: Docker build from `apps/api/Dockerfile`
- App: `npm ci --include=dev && ./node_modules/.bin/nx build @sql2ai/app --configuration=production`
  - **Important:** `--include=dev` is required because NX is in devDependencies and Render sets NODE_ENV=production

### API Endpoints
- `/` - API info (public)
- `/health` - Health check with dependency status (public)
- `/ready` - Kubernetes readiness probe (public)
- `/api/billing/pricing` - Public pricing info
- All other `/api/*` routes require Clerk JWT authentication

## Deployment Issues & Fixes (December 2025)

### 1. Pydantic-Settings List Parsing
**Error:** `SettingsError: error parsing value for field "CORS_ORIGINS"`
**Fix:** Use JSON array format in render.yaml, not comma-separated strings

### 2. Database URL for asyncpg
**Error:** `The asyncio extension requires an async driver`
**Fix:** Transform URL in `start.sh`:
```bash
export SQL2AI_DATABASE_URL=$(echo "$SQL2AI_DATABASE_URL" | sed 's|^postgres://|postgresql+asyncpg://|')
```

### 3. SQLAlchemy Reserved Attribute
**Error:** `Attribute name 'metadata' is reserved when using the Declarative API`
**Fix:** Renamed `metadata` column to `extra_data` in `AuditLog` model

### 4. Alembic Async Migration URL
**Error:** `The loaded 'psycopg2' is not async`
**Fix:** Updated `alembic/env.py` to properly transform URL to use `postgresql+asyncpg://`

### 5. Missing External Libraries
**Error:** `ModuleNotFoundError: No module named 'models'` (orchestrator router)
**Fix:** Made external library routers optional in `routers/__init__.py` and `main.py`
- Optional routers: orchestrator, migrator, optimize, compliance, writer, codereview, version
- These depend on libs not copied to Docker container

### 6. Auth Middleware Parameter
**Error:** `create_auth_middleware() got an unexpected keyword argument 'excluded_paths'`
**Fix:** Removed unsupported parameter - excluded paths are hardcoded in middleware

### 7. ULID Package Compatibility
**Error:** `TypeError: MemoryView.__init__() missing 1 required positional argument`
**Fix:** Replaced `ulid-py` with built-in `uuid.uuid4()` for request IDs

### 8. Auth Middleware HTTPException
**Error:** 500 errors instead of 401 for unauthenticated requests
**Fix:** Return `JSONResponse` directly instead of raising `HTTPException` in middleware

### 9. NX Build - devDependencies
**Error:** `./node_modules/.bin/nx: No such file or directory`
**Fix:** Use `npm ci --include=dev` to install devDependencies (Render sets NODE_ENV=production)

### 10. Hatchling README Requirement
**Error:** `OSError: Readme file does not exist: README.md`
**Fix:** Create README.md in both `libs/shared/` and `apps/api/`, update Dockerfile to COPY README.md

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

### Testing API
```bash
# Health check
curl https://sql2ai-api.onrender.com/health

# Root
curl https://sql2ai-api.onrender.com/

# Authenticated endpoint (will return 401 without token)
curl https://sql2ai-api.onrender.com/api/schemas
```

## Git Commits (Deployment Session)

1. `234dc78` - Add PostgreSQL database to Render blueprint
2. `213b3fb` - Fix Render build failures (README.md, NX build command)
3. `274231b` - Fix API Docker build errors (PROJECT_ROOT, README)
4. `3db04dd` - Fix Dockerfile to copy README.md for hatchling build
5. `af67508` - Fix build configuration (workspace names, NX project name, devtools)
6. `58175ae` - Fix CORS_ORIGINS format for pydantic-settings
7. `a578cb1` - Transform DATABASE_URL for asyncpg compatibility
8. `a1b6cd5` - Rename metadata column to extra_data in AuditLog model
9. `ee95a1c` - Fix alembic async migrations to use asyncpg driver
10. `676140e` - Make external library routers optional for Docker deployment
11. `da82c87` - Fix auth middleware - remove unsupported excluded_paths param
12. `3beed13` - Replace ulid-py with uuid for request IDs
13. `b85c11f` - Fix auth middleware to return JSONResponse instead of HTTPException
