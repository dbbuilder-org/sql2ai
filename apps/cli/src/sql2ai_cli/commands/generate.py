"""SQL generation commands for SQL2.AI CLI."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from sql2ai_cli.utils.api import get_api_client
from sql2ai_cli.utils.config import get_config

app = typer.Typer(help="AI-powered SQL generation")
console = Console()


@app.command()
def sql(
    prompt: str = typer.Argument(help="Natural language description of what you want"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
    context: Path = typer.Option(None, "--context", "-c", help="File with schema context"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate SQL from a natural language prompt."""
    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    context_text = None
    if context:
        if not context.exists():
            console.print(f"[red]Error:[/red] Context file not found: {context}")
            raise typer.Exit(1)
        context_text = context.read_text()

    with console.status("Generating SQL..."):
        try:
            result = client.generate_sql(prompt, db_type, context_text)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    generated_sql = result.get("sql", "")

    if output:
        output.write_text(generated_sql)
        console.print(f"[green]✓[/green] Written to {output}")
    else:
        console.print("\n[bold]Generated SQL[/bold]\n")
        syntax = Syntax(generated_sql, "sql", theme="monokai", line_numbers=True)
        console.print(syntax)

        if result.get("explanation"):
            console.print(f"\n[bold]Explanation:[/bold] {result['explanation']}")


@app.command()
def crud(
    table: str = typer.Argument(help="Table name"),
    schema: str = typer.Option("dbo", "--schema", "-s", help="Schema name"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate CRUD stored procedures for a table."""
    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    with console.status(f"Generating CRUD procedures for {schema}.{table}..."):
        try:
            result = client.generate_crud(table, schema, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    generated_sql = result.get("sql", "")

    if output:
        output.write_text(generated_sql)
        console.print(f"[green]✓[/green] Written to {output}")
    else:
        console.print(f"\n[bold]CRUD Procedures for {schema}.{table}[/bold]\n")
        syntax = Syntax(generated_sql, "sql", theme="monokai", line_numbers=True)
        console.print(syntax)


@app.command()
def table(
    name: str = typer.Argument(help="Table name"),
    columns: str = typer.Argument(help="Column definitions (comma-separated)"),
    schema: str = typer.Option("dbo", "--schema", "-s", help="Schema name"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
):
    """Generate CREATE TABLE statement."""
    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    prompt = f"Create a table named {schema}.{name} with columns: {columns}"

    with console.status("Generating table..."):
        try:
            result = client.generate_sql(prompt, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print(f"\n[bold]CREATE TABLE {schema}.{name}[/bold]\n")
    syntax = Syntax(result.get("sql", ""), "sql", theme="monokai", line_numbers=True)
    console.print(syntax)


@app.command()
def index(
    table: str = typer.Argument(help="Table name"),
    columns: str = typer.Argument(help="Columns to index (comma-separated)"),
    name: str = typer.Option(None, "--name", "-n", help="Index name"),
    unique: bool = typer.Option(False, "--unique", "-u", help="Create unique index"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
):
    """Generate CREATE INDEX statement."""
    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    index_type = "unique index" if unique else "index"
    prompt = f"Create a {index_type} on table {table} for columns: {columns}"
    if name:
        prompt += f" named {name}"

    with console.status("Generating index..."):
        try:
            result = client.generate_sql(prompt, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print("\n[bold]CREATE INDEX[/bold]\n")
    syntax = Syntax(result.get("sql", ""), "sql", theme="monokai", line_numbers=True)
    console.print(syntax)
