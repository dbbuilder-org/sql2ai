"""Schema management commands for SQL2.AI CLI."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from sql2ai_cli.utils.api import get_api_client

app = typer.Typer(help="Schema management and extraction")
console = Console()


@app.command()
def extract(
    connection: str = typer.Argument(help="Connection name or ID"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file (JSON)"),
    format: str = typer.Option("tree", "--format", "-f", help="Output format: tree, table, json"),
):
    """Extract database schema from a connection."""
    client = get_api_client()

    with console.status("Extracting schema..."):
        try:
            result = client.extract_schema(connection)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    schema = result.get("schema", {})

    if output:
        output.write_text(json.dumps(schema, indent=2))
        console.print(f"[green]✓[/green] Schema written to {output}")
        return

    if format == "json":
        console.print(json.dumps(schema, indent=2))
        return

    if format == "table":
        _display_schema_table(schema)
    else:
        _display_schema_tree(schema)


def _display_schema_tree(schema: dict):
    """Display schema as a tree."""
    tree = Tree("[bold]Database Schema[/bold]")

    # Tables
    tables = schema.get("tables", [])
    if tables:
        tables_branch = tree.add("[cyan]Tables[/cyan]")
        for table in tables:
            table_name = f"{table.get('schema', 'dbo')}.{table['name']}"
            table_branch = tables_branch.add(f"[green]{table_name}[/green]")

            for column in table.get("columns", []):
                col_info = f"{column['name']}: {column['data_type']}"
                if column.get("is_nullable") == False:
                    col_info += " NOT NULL"
                if column.get("is_primary_key"):
                    col_info += " [yellow]PK[/yellow]"
                table_branch.add(col_info)

    # Views
    views = schema.get("views", [])
    if views:
        views_branch = tree.add("[cyan]Views[/cyan]")
        for view in views:
            views_branch.add(f"[blue]{view.get('schema', 'dbo')}.{view['name']}[/blue]")

    # Procedures
    procedures = schema.get("procedures", [])
    if procedures:
        procs_branch = tree.add("[cyan]Stored Procedures[/cyan]")
        for proc in procedures:
            procs_branch.add(f"[magenta]{proc.get('schema', 'dbo')}.{proc['name']}[/magenta]")

    console.print(tree)


def _display_schema_table(schema: dict):
    """Display schema as tables."""
    tables = schema.get("tables", [])

    for table_info in tables:
        table_name = f"{table_info.get('schema', 'dbo')}.{table_info['name']}"

        table = Table(title=f"Table: {table_name}")
        table.add_column("Column", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Nullable")
        table.add_column("Key")

        for column in table_info.get("columns", []):
            nullable = "Yes" if column.get("is_nullable", True) else "No"
            key = "PK" if column.get("is_primary_key") else ""
            if column.get("is_foreign_key"):
                key = "FK"

            table.add_row(
                column["name"],
                column["data_type"],
                nullable,
                key,
            )

        console.print(table)
        console.print()


@app.command()
def compare(
    source: str = typer.Argument(help="Source connection or schema file"),
    target: str = typer.Argument(help="Target connection or schema file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output migration script"),
):
    """Compare two schemas and show differences."""
    client = get_api_client()

    with console.status("Comparing schemas..."):
        try:
            result = client.post("/api/schemas/compare", {
                "source": source,
                "target": target,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    diff = result.get("diff", {})

    if not diff.get("has_changes"):
        console.print("[green]✓[/green] Schemas are identical")
        return

    console.print("\n[bold]Schema Differences[/bold]\n")

    # Added objects
    added = diff.get("added", [])
    if added:
        console.print("[green]Added:[/green]")
        for obj in added:
            console.print(f"  + {obj['type']}: {obj['name']}")

    # Removed objects
    removed = diff.get("removed", [])
    if removed:
        console.print("[red]Removed:[/red]")
        for obj in removed:
            console.print(f"  - {obj['type']}: {obj['name']}")

    # Modified objects
    modified = diff.get("modified", [])
    if modified:
        console.print("[yellow]Modified:[/yellow]")
        for obj in modified:
            console.print(f"  ~ {obj['type']}: {obj['name']}")
            for change in obj.get("changes", []):
                console.print(f"      {change}")

    if output and diff.get("migration_sql"):
        output.write_text(diff["migration_sql"])
        console.print(f"\n[green]✓[/green] Migration script written to {output}")


@app.command()
def snapshot(
    connection: str = typer.Argument(help="Connection name or ID"),
    name: str = typer.Option(None, "--name", "-n", help="Snapshot name"),
    output: Path = typer.Option(Path("snapshots"), "--output", "-o", help="Output directory"),
):
    """Create a schema snapshot."""
    client = get_api_client()

    with console.status("Creating snapshot..."):
        try:
            result = client.post(f"/api/schemas/{connection}/snapshot", {
                "name": name,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    snapshot = result.get("snapshot", {})
    snapshot_id = snapshot.get("id", "unknown")

    output.mkdir(parents=True, exist_ok=True)
    snapshot_file = output / f"{snapshot_id}.json"
    snapshot_file.write_text(json.dumps(snapshot, indent=2))

    console.print(f"[green]✓[/green] Snapshot created: {snapshot_id}")
    console.print(f"  Saved to: {snapshot_file}")


@app.command()
def document(
    connection: str = typer.Argument(help="Connection name or ID"),
    output: Path = typer.Option(Path("docs/schema.md"), "--output", "-o", help="Output file"),
    format: str = typer.Option("markdown", "--format", "-f", help="Format: markdown, html"),
):
    """Generate documentation for a database schema."""
    client = get_api_client()

    with console.status("Generating documentation..."):
        try:
            result = client.post(f"/api/codereview/data-dictionary", {
                "connection_id": connection,
                "format": format,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    docs = result.get("documentation", "")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(docs)

    console.print(f"[green]✓[/green] Documentation generated: {output}")
