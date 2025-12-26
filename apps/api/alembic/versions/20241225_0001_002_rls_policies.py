"""Add Row-Level Security policies for multi-tenancy.

Revision ID: 002
Revises: 001
Create Date: 2024-12-25 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable Row-Level Security on tenant-scoped tables
    tables = ["users", "connections", "queries", "query_executions", "audit_logs"]

    for table in tables:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

        # Create policy for tenant isolation
        op.execute(f"""
            CREATE POLICY tenant_isolation_policy ON {table}
            USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
        """)

        # Allow superusers to bypass RLS for admin operations
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # Create helper function to set tenant context
    op.execute("""
        CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id uuid)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_tenant_id', p_tenant_id::text, false);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Create helper function to get current tenant
    op.execute("""
        CREATE OR REPLACE FUNCTION get_current_tenant_id()
        RETURNS uuid AS $$
        BEGIN
            RETURN current_setting('app.current_tenant_id', true)::uuid;
        EXCEPTION
            WHEN OTHERS THEN
                RETURN NULL;
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)

    # Create trigger function to auto-set tenant_id on insert
    op.execute("""
        CREATE OR REPLACE FUNCTION set_tenant_id_on_insert()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.tenant_id IS NULL THEN
                NEW.tenant_id := get_current_tenant_id();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Add triggers to auto-set tenant_id
    for table in tables:
        op.execute(f"""
            CREATE TRIGGER trigger_set_tenant_id
            BEFORE INSERT ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION set_tenant_id_on_insert();
        """)


def downgrade() -> None:
    tables = ["users", "connections", "queries", "query_executions", "audit_logs"]

    # Remove triggers
    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS trigger_set_tenant_id ON {table}")

    # Drop helper functions
    op.execute("DROP FUNCTION IF EXISTS set_tenant_id_on_insert()")
    op.execute("DROP FUNCTION IF EXISTS get_current_tenant_id()")
    op.execute("DROP FUNCTION IF EXISTS set_tenant_context(uuid)")

    # Remove RLS policies and disable RLS
    for table in tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
