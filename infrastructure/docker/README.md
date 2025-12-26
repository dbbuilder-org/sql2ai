# SQL2.AI Local Development Stack

## Prerequisites

- [OrbStack](https://orbstack.dev/) (recommended for macOS) or Docker Desktop
- API keys for services (see `.env.example`)

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
vim .env

# Start core services (Postgres, Redis, API)
orb compose up -d

# Or with docker compose
docker compose up -d
```

## Service Profiles

The stack uses Docker Compose profiles for optional services:

```bash
# Core only (default)
orb compose up -d

# With admin tools (pgAdmin, Redis Commander)
orb compose --profile tools up -d

# With observability (Jaeger, Prometheus, Grafana)
orb compose --profile observability up -d

# With test databases (SQL Server, PostgreSQL)
orb compose --profile testing up -d

# Everything
orb compose --profile tools --profile observability --profile testing up -d
```

## Services

| Service | Port | URL | Credentials |
|---------|------|-----|-------------|
| **API** | 8000 | http://localhost:8000 | - |
| **PostgreSQL** | 5432 | - | postgres/postgres |
| **Redis** | 6379 | - | - |
| **pgAdmin** | 5050 | http://localhost:5050 | admin@sql2.ai/admin |
| **Redis Commander** | 8081 | http://localhost:8081 | - |
| **Jaeger UI** | 16686 | http://localhost:16686 | - |
| **Prometheus** | 9090 | http://localhost:9090 | - |
| **Grafana** | 3001 | http://localhost:3001 | admin/admin |
| **SQL Server** | 1433 | - | sa/Sql2AI_Dev123! |

## Commands

```bash
# View logs
orb compose logs -f api

# Restart API
orb compose restart api

# Stop everything
orb compose down

# Stop and remove volumes
orb compose down -v

# Rebuild API container
orb compose build api
orb compose up -d api
```

## Connecting Test Databases

### SQL Server (with SSMS or Azure Data Studio)
```
Server: localhost,1433
User: sa
Password: Sql2AI_Dev123!
```

### PostgreSQL (platform database)
```
Host: localhost
Port: 5432
Database: sql2ai
User: postgres
Password: postgres
```

### PostgreSQL (test database)
```
Host: localhost
Port: 5433
Database: testdb
User: postgres
Password: postgres
```

## Troubleshooting

### Port already in use
```bash
# Find process using port
lsof -i :8000

# Or use different ports in .env
```

### OrbStack vs Docker
OrbStack is a drop-in replacement for Docker Desktop on macOS. It uses the same CLI:
- `orb compose` = `docker compose`
- `orb run` = `docker run`
- `orb build` = `docker build`
