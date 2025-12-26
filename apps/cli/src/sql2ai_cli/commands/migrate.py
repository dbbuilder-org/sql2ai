"""Migration commands for SQL2.AI CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from sql2ai_cli.utils.api import get_api_client

app = typer.Typer(help="Database migrations")
console = Console()


@app.command("list")
def list_migrations(
    connection: str = typer.Option(None, "--connection", "-c", help="Connection name or ID"),
):
    """List migrations for a database."""
    client = get_api_client()

    try:
        result = client.get(f"/api/migrator/migrations", params={"connection_id": connection})
        migrations = result.get("migrations", [])

        if not migrations:
            console.print("[yellow]No migrations found[/yellow]")
            return

        table = Table(title="Migrations")
        table.add_column("Version", style="cyan")
        table.add_column("Name")
        table.add_column("Applied At")
        table.add_column("Status")

        for migration in migrations:
            status = "[green]Applied[/green]" if migration.get("applied") else "[yellow]Pending[/yellow]"
            table.add_row(
                migration.get("version", "-"),
                migration.get("name", "-"),
                migration.get("applied_at", "-"),
                status,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def generate(
    connection: str = typer.Argument(help="Connection name or ID"),
    name: str = typer.Option(None, "--name", "-n", help="Migration name"),
    output: Path = typer.Option(Path("migrations"), "--output", "-o", help="Output directory"),
):
    """Generate a new migration from schema changes."""
    client = get_api_client()

    with console.status("Detecting schema changes..."):
        try:
            result = client.post(f"/api/migrator/generate", {
                "connection_id": connection,
                "name": name,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if not result.get("has_changes"):
        console.print("[yellow]No schema changes detected[/yellow]")
        return

    migration = result.get("migration", {})
    version = migration.get("version", "unknown")
    up_sql = migration.get("up_sql", "")
    down_sql = migration.get("down_sql", "")

    # Create output directory
    output.mkdir(parents=True, exist_ok=True)

    # Write migration files
    migration_name = name or f"migration_{version}"
    up_file = output / f"{version}_{migration_name}_up.sql"
    down_file = output / f"{version}_{migration_name}_down.sql"

    up_file.write_text(up_sql)
    down_file.write_text(down_sql)

    console.print(f"[green]✓[/green] Generated migration: {version}")
    console.print(f"  Up:   {up_file}")
    console.print(f"  Down: {down_file}")

    if result.get("breaking_changes"):
        console.print("\n[yellow]⚠ Breaking changes detected:[/yellow]")
        for change in result["breaking_changes"]:
            console.print(f"  - {change}")


@app.command()
def apply(
    connection: str = typer.Argument(help="Connection name or ID"),
    version: str = typer.Option(None, "--version", "-v", help="Specific version to apply"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be applied"),
):
    """Apply pending migrations."""
    client = get_api_client()

    with console.status("Applying migrations..."):
        try:
            result = client.post(f"/api/migrator/apply", {
                "connection_id": connection,
                "version": version,
                "dry_run": dry_run,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    applied = result.get("applied", [])

    if dry_run:
        console.print("[bold]Dry run - would apply:[/bold]")
    else:
        console.print("[bold]Applied migrations:[/bold]")

    for migration in applied:
        console.print(f"  [green]✓[/green] {migration['version']}: {migration['name']}")

    if not applied:
        console.print("[yellow]No migrations to apply[/yellow]")


@app.command()
def rollback(
    connection: str = typer.Argument(help="Connection name or ID"),
    steps: int = typer.Option(1, "--steps", "-s", help="Number of migrations to rollback"),
):
    """Rollback applied migrations."""
    client = get_api_client()

    with console.status("Rolling back migrations..."):
        try:
            result = client.post(f"/api/migrator/rollback", {
                "connection_id": connection,
                "steps": steps,
            })
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    rolled_back = result.get("rolled_back", [])

    console.print("[bold]Rolled back:[/bold]")
    for migration in rolled_back:
        console.print(f"  [yellow]↩[/yellow] {migration['version']}: {migration['name']}")

    if not rolled_back:
        console.print("[yellow]No migrations to rollback[/yellow]")
