"""Connection management commands for SQL2.AI CLI."""

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from sql2ai_cli.utils.api import get_api_client
from sql2ai_cli.utils.config import get_connection_password, save_connection_password

app = typer.Typer(help="Database connection management")
console = Console()


@app.command("list")
def list_connections():
    """List all database connections."""
    client = get_api_client()

    try:
        connections = client.list_connections()

        if not connections:
            console.print("[yellow]No connections found[/yellow]")
            console.print("\nRun [bold]sql2ai connections add[/bold] to add a connection")
            return

        table = Table(title="Database Connections")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Host")
        table.add_column("Database")
        table.add_column("Status")

        for conn in connections:
            status = "[green]●[/green]" if conn.get("is_active") else "[red]○[/red]"
            table.add_row(
                conn["name"],
                conn["db_type"],
                conn["host"],
                conn["database"],
                status,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def add(
    name: str = typer.Option(None, "--name", "-n", help="Connection name"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type: postgresql, sqlserver"),
    host: str = typer.Option(None, "--host", "-h", help="Database host"),
    port: int = typer.Option(None, "--port", "-p", help="Database port"),
    database: str = typer.Option(None, "--database", "-d", help="Database name"),
    username: str = typer.Option(None, "--username", "-u", help="Username"),
    password: str = typer.Option(None, "--password", help="Password (will prompt if not provided)"),
):
    """Add a new database connection."""
    console.print("\n[bold]Add Database Connection[/bold]\n")

    # Prompt for missing values
    if not name:
        name = Prompt.ask("Connection name")
    if not db_type:
        db_type = Prompt.ask("Database type", choices=["postgresql", "sqlserver"])
    if not host:
        host = Prompt.ask("Host", default="localhost")
    if not port:
        default_port = 5432 if db_type == "postgresql" else 1433
        port = int(Prompt.ask("Port", default=str(default_port)))
    if not database:
        database = Prompt.ask("Database name")
    if not username:
        username = Prompt.ask("Username")
    if not password:
        password = Prompt.ask("Password", password=True)

    client = get_api_client()

    try:
        result = client.create_connection({
            "name": name,
            "db_type": db_type,
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
        })

        console.print(f"\n[green]✓[/green] Connection '{name}' created successfully")
        console.print(f"  ID: {result['id']}")

        # Save password to keyring
        save_connection_password(name, password)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def test(
    connection: str = typer.Argument(help="Connection name or ID"),
):
    """Test a database connection."""
    client = get_api_client()

    with console.status(f"Testing connection '{connection}'..."):
        try:
            result = client.test_connection(connection)

            if result.get("success"):
                console.print(f"[green]✓[/green] Connection successful!")
                if result.get("server_version"):
                    console.print(f"  Server: {result['server_version']}")
                if result.get("latency_ms"):
                    console.print(f"  Latency: {result['latency_ms']}ms")
            else:
                console.print(f"[red]✗[/red] Connection failed: {result.get('message', 'Unknown error')}")
                raise typer.Exit(1)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)


@app.command()
def remove(
    connection: str = typer.Argument(help="Connection name or ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove a database connection."""
    if not force:
        if not Confirm.ask(f"Remove connection '{connection}'?"):
            console.print("Cancelled")
            return

    client = get_api_client()

    try:
        client.delete(f"/api/connections/{connection}")
        console.print(f"[green]✓[/green] Connection '{connection}' removed")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
