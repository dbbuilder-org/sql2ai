"""Authentication commands for SQL2.AI CLI."""

import typer
from rich.console import Console
from rich.prompt import Prompt

from sql2ai_cli.utils.config import delete_api_key, get_api_key, save_api_key
from sql2ai_cli.utils.api import get_api_client

app = typer.Typer(help="Authentication and API key management")
console = Console()


@app.command()
def login(
    api_key: str = typer.Option(
        None,
        "--api-key",
        "-k",
        help="API key (will prompt if not provided)",
    ),
):
    """Login to SQL2.AI with your API key."""
    if not api_key:
        console.print("\n[bold]SQL2.AI Login[/bold]\n")
        console.print("Get your API key from: [link=https://app.sql2.ai/settings/api]app.sql2.ai/settings/api[/link]\n")
        api_key = Prompt.ask("Enter your API key", password=True)

    if not api_key:
        console.print("[red]Error:[/red] API key is required")
        raise typer.Exit(1)

    # Test the API key
    client = get_api_client()
    client.api_key = api_key

    try:
        if client.health_check():
            save_api_key(api_key)
            console.print("[green]✓[/green] Successfully authenticated!")
            console.print("\nYou can now use SQL2.AI commands.")
        else:
            console.print("[red]✗[/red] Could not connect to SQL2.AI API")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def logout():
    """Logout and remove stored API key."""
    delete_api_key()
    console.print("[green]✓[/green] Logged out successfully")


@app.command()
def status():
    """Check authentication status."""
    api_key = get_api_key()

    if api_key:
        # Mask the API key
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        console.print(f"[green]✓[/green] Authenticated with API key: {masked}")

        # Test connection
        client = get_api_client()
        if client.health_check():
            console.print("[green]✓[/green] API connection verified")
        else:
            console.print("[yellow]![/yellow] Cannot reach API server")
    else:
        console.print("[yellow]○[/yellow] Not authenticated")
        console.print("\nRun [bold]sql2ai auth login[/bold] to authenticate")


@app.command()
def whoami():
    """Show current user information."""
    client = get_api_client()

    if not client.is_authenticated:
        console.print("[yellow]Not authenticated[/yellow]")
        console.print("Run [bold]sql2ai auth login[/bold] to authenticate")
        raise typer.Exit(1)

    try:
        # This would call a /me endpoint if available
        console.print("[green]Authenticated user[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
