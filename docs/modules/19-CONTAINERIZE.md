# SQL Containerize

**Database Container Migration Platform**

## Overview

SQL Containerize automates the process of migrating SQL Server or PostgreSQL from running instances (on-premises or cloud VMs) to containerized environments. It supports Docker, Kubernetes, Azure Container Instances (ACI), AWS ECS/EKS, and Google Cloud Run/GKE.

## The Problem

### Current Containerization Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Complex migration | Manual Docker setup | Error-prone, slow |
| Data persistence | Ad-hoc volumes | Data loss |
| Configuration drift | Manual config | Environment differences |
| Kubernetes setup | Custom YAML | Misconfiguration |
| Zero downtime | Planned maintenance | Business disruption |
| Multi-cloud | Separate processes | Inconsistent deployments |

## SQL Containerize Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE DATABASE                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  SQL Server / PostgreSQL (On-Prem, Azure VM, AWS EC2, GCP)  ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL CONTAINERIZE ENGINE                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Analyze Source    - Schema, size, dependencies         │ │
│  │  2. Plan Migration    - Strategy, resources, timing        │ │
│  │  3. Generate Configs  - Dockerfile, K8s YAML, scripts      │ │
│  │  4. Prepare Target    - Create containers, volumes         │ │
│  │  5. Migrate Data      - Sync with minimal downtime         │ │
│  │  6. Cutover           - Switch traffic, verify             │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   Docker    │   │ Kubernetes  │   │ Cloud       │
   │   Compose   │   │ (AKS/EKS/   │   │ Containers  │
   │             │   │  GKE)       │   │ (ACI/ECS)   │
   └─────────────┘   └─────────────┘   └─────────────┘
```

## Target Platforms

### Docker & Docker Compose
```yaml
# Local development, small deployments
targets:
  - type: docker
  - type: docker-compose
```

### Kubernetes
```yaml
# Production-grade orchestration
targets:
  - type: kubernetes
    variants:
      - aks (Azure Kubernetes Service)
      - eks (Amazon EKS)
      - gke (Google GKE)
      - k3s (Lightweight K8s)
      - openshift
```

### Cloud Container Services
```yaml
# Managed container platforms
targets:
  - type: azure-container-instances
  - type: aws-ecs
  - type: aws-fargate
  - type: gcp-cloud-run
```

## Migration Workflow

### 1. Source Analysis

```bash
sql2ai containerize analyze --source "Server=prod-sql;Database=AppDB"
```

```
╔══════════════════════════════════════════════════════════════════╗
║              SOURCE DATABASE ANALYSIS                            ║
╠══════════════════════════════════════════════════════════════════╣
║ Database: AppDB                                                  ║
║ Engine: SQL Server 2019 (15.0.4153.1)                           ║
║ Current Host: prod-sql-01 (Windows Server 2019)                  ║
╠══════════════════════════════════════════════════════════════════╣
║ SIZE ANALYSIS                                                    ║
║ ─────────────────────────────────────────────────────────────── ║
║ Data Size:          45.2 GB                                      ║
║ Log Size:           12.1 GB                                      ║
║ Index Size:         8.7 GB                                       ║
║ Total:              66.0 GB                                      ║
╠══════════════════════════════════════════════════════════════════╣
║ CONFIGURATION                                                    ║
║ ─────────────────────────────────────────────────────────────── ║
║ Max Memory:         32 GB                                        ║
║ Max DOP:            4                                            ║
║ Collation:          SQL_Latin1_General_CP1_CI_AS                 ║
║ Compatibility:      150                                          ║
╠══════════════════════════════════════════════════════════════════╣
║ DEPENDENCIES                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Linked Servers:     2 (need migration strategy)                  ║
║ SQL Agent Jobs:     18 (convert to K8s CronJobs)                 ║
║ CLR Assemblies:     1 (StringUtils - need replacement)           ║
║ External Files:     /data/imports (mount required)               ║
╠══════════════════════════════════════════════════════════════════╣
║ RECOMMENDED CONTAINER RESOURCES                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ CPU:                4 cores (minimum), 8 cores (recommended)     ║
║ Memory:             16 GB (minimum), 32 GB (recommended)         ║
║ Storage:            100 GB SSD (with room for growth)            ║
║ IOPS:               3000+ recommended                            ║
╚══════════════════════════════════════════════════════════════════╝
```

### 2. Configuration Generation

**Docker Compose:**
```yaml
# Generated: docker-compose.yml
version: '3.8'

services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2019-latest
    container_name: appdb-sql
    environment:
      ACCEPT_EULA: "Y"
      SA_PASSWORD: "${SA_PASSWORD}"
      MSSQL_MEMORY_LIMIT_MB: 32768
    ports:
      - "1433:1433"
    volumes:
      - sqldata:/var/opt/mssql/data
      - sqllog:/var/opt/mssql/log
      - sqlbackup:/var/opt/mssql/backup
      - ./imports:/data/imports:ro
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 32G
        reservations:
          cpus: '4'
          memory: 16G
    healthcheck:
      test: /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "${SA_PASSWORD}" -Q "SELECT 1"
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 30s

volumes:
  sqldata:
    driver: local
  sqllog:
    driver: local
  sqlbackup:
    driver: local
```

**Kubernetes:**
```yaml
# Generated: kubernetes/sqlserver-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: sqlserver
  namespace: database
spec:
  serviceName: sqlserver
  replicas: 1
  selector:
    matchLabels:
      app: sqlserver
  template:
    metadata:
      labels:
        app: sqlserver
    spec:
      containers:
      - name: sqlserver
        image: mcr.microsoft.com/mssql/server:2019-latest
        ports:
        - containerPort: 1433
        env:
        - name: ACCEPT_EULA
          value: "Y"
        - name: SA_PASSWORD
          valueFrom:
            secretKeyRef:
              name: sqlserver-secret
              key: sa-password
        - name: MSSQL_MEMORY_LIMIT_MB
          value: "32768"
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
          limits:
            memory: "32Gi"
            cpu: "8"
        volumeMounts:
        - name: sqldata
          mountPath: /var/opt/mssql/data
        - name: sqllog
          mountPath: /var/opt/mssql/log
        livenessProbe:
          exec:
            command:
            - /opt/mssql-tools/bin/sqlcmd
            - -S
            - localhost
            - -U
            - sa
            - -P
            - $(SA_PASSWORD)
            - -Q
            - SELECT 1
          initialDelaySeconds: 30
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: sqldata
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: premium-ssd
      resources:
        requests:
          storage: 100Gi
  - metadata:
      name: sqllog
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: premium-ssd
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: sqlserver
  namespace: database
spec:
  ports:
  - port: 1433
  selector:
    app: sqlserver
  type: ClusterIP
```

### 3. SQL Agent Jobs → Kubernetes CronJobs

```yaml
# Generated: kubernetes/cronjobs.yaml
# Converted from SQL Agent Job: DailyBackup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # 2:00 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: sql2ai/sql-tools:latest
            command:
            - /bin/bash
            - -c
            - |
              sqlcmd -S sqlserver -U sa -P $SA_PASSWORD \
                -Q "BACKUP DATABASE AppDB TO DISK='/backup/AppDB_$(date +%Y%m%d).bak'"
            env:
            - name: SA_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: sqlserver-secret
                  key: sa-password
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### 4. Data Migration

```
╔══════════════════════════════════════════════════════════════════╗
║              DATA MIGRATION PROGRESS                             ║
╠══════════════════════════════════════════════════════════════════╣
║ Phase 1: Initial Sync                                            ║
║ ─────────────────────────────────────────────────────────────── ║
║ Customers:        [████████████████████] 100%  (1.2M rows)       ║
║ Orders:           [████████████████████] 100%  (5.4M rows)       ║
║ Products:         [████████████████████] 100%  (45K rows)        ║
║ Transactions:     [████████████░░░░░░░░] 58%   (12.1M / 21M)    ║
╠══════════════════════════════════════════════════════════════════╣
║ Transfer Rate: 125 MB/s                                          ║
║ Elapsed: 8m 42s                                                  ║
║ Remaining: ~6m                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║ Phase 2: CDC Sync (after initial)                                ║
║ ─────────────────────────────────────────────────────────────── ║
║ Changes captured: 2,847 (since sync started)                     ║
║ Will apply after initial sync completes                          ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5. Zero-Downtime Cutover

```yaml
cutover:
  strategy: blue-green

  steps:
    - name: final_sync
      description: "Apply remaining CDC changes"
      max_duration: 5m

    - name: verify_sync
      description: "Verify row counts and checksums"
      tables: [Customers, Orders, Products]

    - name: redirect_traffic
      description: "Update DNS/connection strings"
      method: dns  # or load_balancer, app_config

    - name: monitor
      description: "Watch for errors"
      duration: 15m
      rollback_on_errors: true

    - name: decommission_source
      description: "Stop source after validation"
      delay: 24h  # Keep source running for 24h
```

## PostgreSQL Support

```yaml
# PostgreSQL to Kubernetes
source:
  type: postgresql
  connection: "postgresql://prod-pg/appdb"

target:
  type: kubernetes
  platform: eks

generated:
  - kubernetes/postgres-statefulset.yaml
  - kubernetes/postgres-service.yaml
  - kubernetes/postgres-secrets.yaml
  - kubernetes/pgbouncer-deployment.yaml  # Connection pooler
  - kubernetes/postgres-backup-cronjob.yaml
```

```yaml
# Generated: kubernetes/postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  serviceName: postgresql
  replicas: 1
  template:
    spec:
      containers:
      - name: postgresql
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
```

## Cloud-Specific Configurations

### Azure Container Instances
```yaml
target:
  type: azure-container-instances
  resource_group: database-rg
  location: eastus2

generated:
  - azure/aci-deployment.json
  - azure/storage-account.json
  - azure/file-share.json
```

### AWS ECS
```yaml
target:
  type: aws-ecs
  cluster: database-cluster
  region: us-east-1

generated:
  - aws/task-definition.json
  - aws/service.json
  - aws/efs-filesystem.tf
```

### GCP Cloud Run
```yaml
target:
  type: gcp-cloud-run
  project: my-project
  region: us-central1

generated:
  - gcp/cloud-run-service.yaml
  - gcp/persistent-disk.tf
```

## CLI Commands

```bash
# Analyze source database
sql2ai containerize analyze --source "..."

# Generate container configs
sql2ai containerize generate --target kubernetes --platform aks

# Deploy containers
sql2ai containerize deploy --config containerize.yaml

# Migrate data
sql2ai containerize migrate --strategy zero-downtime

# Cutover to container
sql2ai containerize cutover --verify

# Rollback if needed
sql2ai containerize rollback
```

## Integration Points

- **SQL Orchestrate**: Schedule container maintenance
- **SQL Monitor**: Container health dashboards
- **SQL Convert**: Migrate while containerizing
- **SQL Centralize**: Replicate to container clusters
