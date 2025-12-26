"""SQL2.AI CLI - Main entry point."""

import typer
from rich.console import Console

from sql2ai_cli import __version__
from sql2ai_cli.commands import (
    auth,
    connections,
    optimize,
    review,
    generate,
    migrate,
    schema,
)

app = typer.Typer(
    name="sql2ai",
    help="SQL2.AI - AI-powered database development from the command line",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# Register command groups
app.add_typer(auth.app, name="auth", help="Authentication and API key management")
app.add_typer(connections.app, name="connections", help="Database connection management")
app.add_typer(optimize.app, name="optimize", help="Query optimization and analysis")
app.add_typer(review.app, name="review", help="Code review and quality checks")
app.add_typer(generate.app, name="generate", help="AI-powered SQL generation")
app.add_typer(migrate.app, name="migrate", help="Database migrations")
app.add_typer(schema.app, name="schema", help="Schema management and extraction")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit"
    ),
):
    """SQL2.AI CLI - AI-powered database development."""
    if version:
        console.print(f"[bold blue]SQL2.AI CLI[/bold blue] version {__version__}")
        raise typer.Exit()


@app.command()
def init():
    """Initialize SQL2.AI in the current project."""
    from sql2ai_cli.utils.config import create_config_file

    config_path = create_config_file()
    console.print(f"[green]✓[/green] Created configuration file: {config_path}")
    console.print("\nNext steps:")
    console.print("  1. Run [bold]sql2ai auth login[/bold] to authenticate")
    console.print("  2. Run [bold]sql2ai connections add[/bold] to add a database")
    console.print("  3. Run [bold]sql2ai --help[/bold] to see all commands")


@app.command()
def status():
    """Show current status and configuration."""
    from sql2ai_cli.utils.config import get_config
    from sql2ai_cli.utils.api import get_api_client

    config = get_config()
    api = get_api_client()

    console.print("\n[bold]SQL2.AI Status[/bold]\n")

    # Authentication
    if api.is_authenticated:
        console.print("[green]✓[/green] Authenticated")
    else:
        console.print("[yellow]○[/yellow] Not authenticated - run [bold]sql2ai auth login[/bold]")

    # API connection
    try:
        if api.health_check():
            console.print(f"[green]✓[/green] Connected to {config.api_url}")
        else:
            console.print(f"[red]✗[/red] Cannot connect to {config.api_url}")
    except Exception as e:
        console.print(f"[red]✗[/red] API error: {e}")

    # Default database
    console.print(f"[blue]○[/blue] Default database: {config.default_database}")

    console.print()


if __name__ == "__main__":
    app()
