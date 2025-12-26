#!/usr/bin/env python3
"""
Database seed script for SQL2.AI platform.

This script seeds the database with initial data for development and testing.
Usage: python scripts/seed.py [--env development|staging|production]
"""

import asyncio
import argparse
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4
import hashlib
import secrets

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


# ============================================================================
# Configuration
# ============================================================================

ENVIRONMENTS = {
    "development": {
        "users": 10,
        "tenants": 3,
        "connections_per_tenant": 5,
        "queries_per_connection": 20,
    },
    "staging": {
        "users": 50,
        "tenants": 10,
        "connections_per_tenant": 10,
        "queries_per_connection": 50,
    },
    "production": {
        "users": 0,  # No seed data in production
        "tenants": 0,
        "connections_per_tenant": 0,
        "queries_per_connection": 0,
    },
}


# ============================================================================
# Sample Data
# ============================================================================

SAMPLE_USERS = [
    {
        "email": "admin@sql2ai.dev",
        "name": "Admin User",
        "role": "owner",
    },
    {
        "email": "dba@sql2ai.dev",
        "name": "Database Admin",
        "role": "dba",
    },
    {
        "email": "developer@sql2ai.dev",
        "name": "Developer User",
        "role": "developer",
    },
    {
        "email": "viewer@sql2ai.dev",
        "name": "Viewer User",
        "role": "viewer",
    },
]

SAMPLE_TENANTS = [
    {
        "name": "Acme Corporation",
        "slug": "acme-corp",
        "plan": "professional",
    },
    {
        "name": "TechStart Inc",
        "slug": "techstart",
        "plan": "team",
    },
    {
        "name": "DataFlow Labs",
        "slug": "dataflow",
        "plan": "free",
    },
]

SAMPLE_CONNECTIONS = [
    {
        "name": "Production SQL Server",
        "dialect": "sqlserver",
        "host": "prod-db.example.com",
        "port": 1433,
        "database": "MainDB",
        "environment": "production",
    },
    {
        "name": "Staging PostgreSQL",
        "dialect": "postgresql",
        "host": "staging-db.example.com",
        "port": 5432,
        "database": "staging_db",
        "environment": "staging",
    },
    {
        "name": "Development Database",
        "dialect": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "dev_db",
        "environment": "development",
    },
    {
        "name": "Azure SQL Database",
        "dialect": "sqlserver",
        "host": "sql2ai-demo.database.windows.net",
        "port": 1433,
        "database": "DemoDB",
        "environment": "production",
    },
    {
        "name": "Analytics Warehouse",
        "dialect": "postgresql",
        "host": "analytics.example.com",
        "port": 5432,
        "database": "warehouse",
        "environment": "production",
    },
]

SAMPLE_QUERIES = [
    {
        "name": "Get Active Customers",
        "sql": "SELECT * FROM Customers WHERE IsActive = 1 ORDER BY CreatedAt DESC",
        "description": "Retrieves all active customers",
    },
    {
        "name": "Monthly Revenue Report",
        "sql": """
            SELECT
                YEAR(OrderDate) AS Year,
                MONTH(OrderDate) AS Month,
                SUM(TotalAmount) AS Revenue,
                COUNT(*) AS OrderCount
            FROM Orders
            WHERE OrderDate >= DATEADD(MONTH, -12, GETDATE())
            GROUP BY YEAR(OrderDate), MONTH(OrderDate)
            ORDER BY Year, Month
        """,
        "description": "Monthly revenue aggregation for last 12 months",
    },
    {
        "name": "Top Products by Sales",
        "sql": """
            SELECT TOP 10
                p.ProductName,
                SUM(od.Quantity) AS TotalQuantity,
                SUM(od.Quantity * od.UnitPrice) AS TotalRevenue
            FROM Products p
            JOIN OrderDetails od ON p.ProductId = od.ProductId
            GROUP BY p.ProductName
            ORDER BY TotalRevenue DESC
        """,
        "description": "Top 10 best-selling products",
    },
    {
        "name": "Customer Order History",
        "sql": """
            SELECT
                c.CustomerName,
                c.Email,
                o.OrderId,
                o.OrderDate,
                o.TotalAmount,
                o.Status
            FROM Customers c
            LEFT JOIN Orders o ON c.CustomerId = o.CustomerId
            WHERE c.CustomerId = @CustomerId
            ORDER BY o.OrderDate DESC
        """,
        "description": "Get complete order history for a customer",
    },
    {
        "name": "Inventory Alert",
        "sql": """
            SELECT
                ProductName,
                StockQuantity,
                ReorderLevel,
                (ReorderLevel - StockQuantity) AS ShortageAmount
            FROM Products
            WHERE StockQuantity < ReorderLevel
            ORDER BY ShortageAmount DESC
        """,
        "description": "Products that need reordering",
    },
]

SAMPLE_SCHEMAS = [
    {
        "name": "Customers",
        "type": "table",
        "columns": [
            {"name": "CustomerId", "type": "INT", "nullable": False, "is_pk": True},
            {"name": "CustomerName", "type": "NVARCHAR(100)", "nullable": False},
            {"name": "Email", "type": "NVARCHAR(255)", "nullable": False},
            {"name": "Phone", "type": "VARCHAR(20)", "nullable": True},
            {"name": "Address", "type": "NVARCHAR(500)", "nullable": True},
            {"name": "CreatedAt", "type": "DATETIME2", "nullable": False},
            {"name": "IsActive", "type": "BIT", "nullable": False},
        ],
    },
    {
        "name": "Orders",
        "type": "table",
        "columns": [
            {"name": "OrderId", "type": "INT", "nullable": False, "is_pk": True},
            {"name": "CustomerId", "type": "INT", "nullable": False, "is_fk": True},
            {"name": "OrderDate", "type": "DATETIME2", "nullable": False},
            {"name": "TotalAmount", "type": "DECIMAL(18,2)", "nullable": False},
            {"name": "Status", "type": "VARCHAR(20)", "nullable": False},
            {"name": "ShippedDate", "type": "DATETIME2", "nullable": True},
        ],
    },
    {
        "name": "Products",
        "type": "table",
        "columns": [
            {"name": "ProductId", "type": "INT", "nullable": False, "is_pk": True},
            {"name": "ProductName", "type": "NVARCHAR(100)", "nullable": False},
            {"name": "Category", "type": "VARCHAR(50)", "nullable": False},
            {"name": "UnitPrice", "type": "DECIMAL(18,2)", "nullable": False},
            {"name": "StockQuantity", "type": "INT", "nullable": False},
            {"name": "ReorderLevel", "type": "INT", "nullable": False},
        ],
    },
]


# ============================================================================
# Seeding Functions
# ============================================================================

def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


def hash_password(password: str) -> str:
    """Hash a password (for demo purposes only)."""
    return hashlib.sha256(password.encode()).hexdigest()


async def seed_tenants(session: AsyncSession, config: dict) -> list:
    """Seed tenant data."""
    tenants = []
    for i, tenant_data in enumerate(SAMPLE_TENANTS[:config["tenants"]]):
        tenant = {
            "id": generate_id(),
            "name": tenant_data["name"],
            "slug": tenant_data["slug"],
            "plan": tenant_data["plan"],
            "created_at": datetime.utcnow() - timedelta(days=30 * (i + 1)),
            "settings": {
                "timezone": "UTC",
                "notifications_enabled": True,
            },
        }
        tenants.append(tenant)
        print(f"  Created tenant: {tenant['name']}")

    # In a real implementation, you would insert into the database:
    # await session.execute(insert(Tenant).values(tenants))
    return tenants


async def seed_users(session: AsyncSession, tenants: list, config: dict) -> list:
    """Seed user data."""
    users = []
    for i, user_data in enumerate(SAMPLE_USERS[:config["users"]]):
        # Assign users to tenants round-robin
        tenant = tenants[i % len(tenants)] if tenants else None

        user = {
            "id": generate_id(),
            "clerk_id": f"user_{generate_id()[:8]}",
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
            "tenant_id": tenant["id"] if tenant else None,
            "created_at": datetime.utcnow() - timedelta(days=i * 7),
            "last_login": datetime.utcnow() - timedelta(hours=i * 2),
        }
        users.append(user)
        print(f"  Created user: {user['email']} ({user['role']})")

    return users


async def seed_connections(
    session: AsyncSession, tenants: list, config: dict
) -> list:
    """Seed database connection data."""
    connections = []
    for tenant in tenants:
        for i, conn_data in enumerate(
            SAMPLE_CONNECTIONS[: config["connections_per_tenant"]]
        ):
            # Generate encrypted credentials (mock)
            encrypted_credentials = {
                "username": f"user_{secrets.token_hex(4)}",
                "password_encrypted": secrets.token_hex(32),
                "encryption_key_id": f"key_{generate_id()[:8]}",
            }

            connection = {
                "id": generate_id(),
                "tenant_id": tenant["id"],
                "name": f"{tenant['name']} - {conn_data['name']}",
                "dialect": conn_data["dialect"],
                "host": conn_data["host"],
                "port": conn_data["port"],
                "database": conn_data["database"],
                "environment": conn_data["environment"],
                "encrypted_credentials": encrypted_credentials,
                "is_active": True,
                "last_connected_at": datetime.utcnow() - timedelta(hours=i),
                "created_at": datetime.utcnow() - timedelta(days=i * 3),
            }
            connections.append(connection)
            print(f"  Created connection: {connection['name']}")

    return connections


async def seed_queries(
    session: AsyncSession, connections: list, users: list, config: dict
) -> list:
    """Seed saved query data."""
    queries = []
    for connection in connections:
        for i, query_data in enumerate(
            SAMPLE_QUERIES[: config["queries_per_connection"]]
        ):
            # Assign to a random user
            user = users[i % len(users)] if users else None

            query = {
                "id": generate_id(),
                "connection_id": connection["id"],
                "user_id": user["id"] if user else None,
                "name": query_data["name"],
                "sql": query_data["sql"].strip(),
                "description": query_data["description"],
                "is_favorite": i < 2,  # First 2 are favorites
                "execution_count": (10 - i) * 5,
                "avg_execution_time_ms": 100 + (i * 50),
                "last_executed_at": datetime.utcnow() - timedelta(hours=i * 4),
                "created_at": datetime.utcnow() - timedelta(days=i * 2),
            }
            queries.append(query)

    print(f"  Created {len(queries)} saved queries")
    return queries


async def seed_schema_snapshots(
    session: AsyncSession, connections: list
) -> list:
    """Seed schema snapshot data."""
    snapshots = []
    for connection in connections:
        snapshot = {
            "id": generate_id(),
            "connection_id": connection["id"],
            "version": 1,
            "tables": SAMPLE_SCHEMAS,
            "views": [],
            "procedures": [
                {
                    "name": "sp_GetCustomerOrders",
                    "definition": "CREATE PROCEDURE sp_GetCustomerOrders @CustomerId INT AS ...",
                },
            ],
            "captured_at": datetime.utcnow(),
            "created_by": "system",
        }
        snapshots.append(snapshot)

    print(f"  Created {len(snapshots)} schema snapshots")
    return snapshots


async def seed_audit_logs(
    session: AsyncSession, users: list, config: dict
) -> list:
    """Seed audit log data."""
    logs = []
    actions = [
        ("connection.create", "Created database connection"),
        ("query.execute", "Executed SQL query"),
        ("schema.export", "Exported schema"),
        ("user.login", "User logged in"),
        ("settings.update", "Updated settings"),
    ]

    for user in users[:5]:
        for i, (action, description) in enumerate(actions):
            log = {
                "id": generate_id(),
                "user_id": user["id"],
                "tenant_id": user.get("tenant_id"),
                "action": action,
                "description": description,
                "ip_address": f"192.168.1.{10 + i}",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "metadata": {"browser": "Chrome", "os": "Windows"},
                "created_at": datetime.utcnow() - timedelta(hours=i),
            }
            logs.append(log)

    print(f"  Created {len(logs)} audit log entries")
    return logs


# ============================================================================
# Main Seeding Logic
# ============================================================================

async def seed_database(env: str = "development"):
    """Main seeding function."""
    config = ENVIRONMENTS.get(env, ENVIRONMENTS["development"])

    if env == "production":
        print("Warning: Skipping seed for production environment")
        return

    print(f"\n{'='*60}")
    print(f"Seeding database for {env} environment")
    print(f"{'='*60}\n")

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sql2ai_dev"
    )

    print(f"Database: {database_url.split('@')[-1]}\n")

    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("Seeding tenants...")
            tenants = await seed_tenants(session, config)

            print("\nSeeding users...")
            users = await seed_users(session, tenants, config)

            print("\nSeeding connections...")
            connections = await seed_connections(session, tenants, config)

            print("\nSeeding queries...")
            queries = await seed_queries(session, connections, users, config)

            print("\nSeeding schema snapshots...")
            snapshots = await seed_schema_snapshots(session, connections)

            print("\nSeeding audit logs...")
            audit_logs = await seed_audit_logs(session, users, config)

            # Commit all changes
            await session.commit()

            print(f"\n{'='*60}")
            print("Seeding completed successfully!")
            print(f"{'='*60}")
            print(f"\nSummary:")
            print(f"  - Tenants: {len(tenants)}")
            print(f"  - Users: {len(users)}")
            print(f"  - Connections: {len(connections)}")
            print(f"  - Queries: {len(queries)}")
            print(f"  - Schema Snapshots: {len(snapshots)}")
            print(f"  - Audit Logs: {len(audit_logs)}")

        except Exception as e:
            await session.rollback()
            print(f"\nError during seeding: {e}")
            raise

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Seed the SQL2.AI database")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Target environment",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing data before seeding",
    )

    args = parser.parse_args()

    if args.reset:
        print("Warning: --reset will clear existing data!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Aborted.")
            return

    asyncio.run(seed_database(args.env))


if __name__ == "__main__":
    main()
