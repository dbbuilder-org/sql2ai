"""Initial schema with core tables.

Revision ID: 001
Revises:
Create Date: 2024-12-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tenants table
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column(
            "tier",
            sa.Enum("free", "pro", "enterprise", name="tenanttier"),
            nullable=False,
            server_default="free",
        ),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("max_connections", sa.Integer, nullable=False, server_default="1"),
        sa.Column("max_queries_per_day", sa.Integer, nullable=False, server_default="100"),
        sa.Column("max_users", sa.Integer, nullable=False, server_default="1"),
        sa.Column("queries_today", sa.Integer, nullable=False, server_default="0"),
        sa.Column("queries_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("clerk_id", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "dba", "developer", "viewer", name="userrole"),
            nullable=False,
            server_default="developer",
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferences", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_clerk_id", "users", ["clerk_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # Create connections table
    op.create_table(
        "connections",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "db_type",
            sa.Enum("sqlserver", "postgresql", "mysql", "mariadb", name="databasetype"),
            nullable=False,
        ),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.Integer, nullable=False),
        sa.Column("database", sa.String(255), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("password_secret_id", sa.String(255), nullable=True),
        sa.Column("trust_server_certificate", sa.Boolean, server_default="false"),
        sa.Column("encrypt", sa.Boolean, server_default="true"),
        sa.Column("application_name", sa.String(255), server_default="SQL2.AI"),
        sa.Column("ssl_mode", sa.String(50), nullable=True),
        sa.Column("ssl_ca_cert_id", sa.String(255), nullable=True),
        sa.Column("pool_size", sa.Integer, server_default="5"),
        sa.Column("max_overflow", sa.Integer, server_default="10"),
        sa.Column("environment", sa.String(50), server_default="development"),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_connections_tenant_id", "connections", ["tenant_id"])

    # Create queries table
    op.create_table(
        "queries",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sql", sa.Text, nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("is_ai_generated", sa.Boolean, server_default="false"),
        sa.Column("ai_prompt", sa.Text, nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("is_shared", sa.Boolean, server_default="false"),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["connection_id"], ["connections.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_queries_tenant_id", "queries", ["tenant_id"])

    # Create query_executions table
    op.create_table(
        "query_executions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("query_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("connection_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("sql", sa.Text, nullable=False),
        sa.Column("sql_hash", sa.String(64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "running", "completed", "failed", "cancelled", "timeout",
                name="querystatus"
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Float, nullable=True),
        sa.Column("rows_affected", sa.Integer, nullable=True),
        sa.Column("bytes_scanned", sa.Integer, nullable=True),
        sa.Column("result_preview", postgresql.JSONB, nullable=True),
        sa.Column("result_row_count", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("ai_explanation", sa.Text, nullable=True),
        sa.Column("ai_optimization_suggestions", postgresql.JSONB, nullable=True),
        sa.Column("executed_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("client_user_agent", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["query_id"], ["queries.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connection_id"], ["connections.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_query_executions_tenant_id", "query_executions", ["tenant_id"])
    op.create_index("ix_query_executions_sql_hash", "query_executions", ["sql_hash"])

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "login", "logout", "login_failed",
                "create", "read", "update", "delete",
                "query_execute", "query_save",
                "connection_test", "connection_activate", "connection_deactivate",
                "ai_query_generate", "ai_query_approve", "ai_query_reject",
                "compliance_scan", "compliance_report",
                "user_invite", "user_remove", "role_change", "settings_update",
                "subscription_create", "subscription_update", "subscription_cancel",
                name="auditaction"
            ),
            nullable=False,
        ),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("old_values", postgresql.JSONB, nullable=True),
        sa.Column("new_values", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("previous_hash", sa.String(64), nullable=True),
        sa.Column("entry_hash", sa.String(64), nullable=False),
        sa.Column("compliance_frameworks", postgresql.JSONB, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_entry_hash", "audit_logs", ["entry_hash"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("query_executions")
    op.drop_table("queries")
    op.drop_table("connections")
    op.drop_table("users")
    op.drop_table("tenants")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS auditaction")
    op.execute("DROP TYPE IF EXISTS querystatus")
    op.execute("DROP TYPE IF EXISTS databasetype")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS tenanttier")
