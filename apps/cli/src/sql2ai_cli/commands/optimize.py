"""Query optimization commands for SQL2.AI CLI."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

from sql2ai_cli.utils.api import get_api_client
from sql2ai_cli.utils.config import get_config

app = typer.Typer(help="Query optimization and analysis")
console = Console()


@app.command()
def query(
    sql: str = typer.Argument(None, help="SQL query to optimize (or use --file)"),
    file: Path = typer.Option(None, "--file", "-f", help="SQL file to optimize"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type: postgresql, sqlserver"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file for optimized query"),
):
    """Optimize a SQL query with AI suggestions."""
    # Get SQL from file or argument
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        sql = file.read_text()
    elif not sql:
        # Read from stdin if no argument
        if not sys.stdin.isatty():
            sql = sys.stdin.read()
        else:
            console.print("[red]Error:[/red] No SQL provided. Use argument, --file, or pipe from stdin")
            raise typer.Exit(1)

    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    with console.status("Optimizing query..."):
        try:
            result = client.optimize_query(sql, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Display results
    console.print("\n[bold]Query Optimization Results[/bold]\n")

    if result.get("suggestions"):
        console.print(Panel("[bold]Suggestions[/bold]"))
        for i, suggestion in enumerate(result["suggestions"], 1):
            console.print(f"  {i}. {suggestion}")
        console.print()

    if result.get("estimated_improvement"):
        console.print(f"[green]Estimated Improvement:[/green] {result['estimated_improvement']}\n")

    optimized_sql = result.get("optimized_query", sql)

    console.print(Panel("[bold]Optimized Query[/bold]"))
    syntax = Syntax(optimized_sql, "sql", theme="monokai", line_numbers=True)
    console.print(syntax)

    # Write to output file if specified
    if output:
        output.write_text(optimized_sql)
        console.print(f"\n[green]✓[/green] Written to {output}")


@app.command()
def explain(
    sql: str = typer.Argument(None, help="SQL query to explain"),
    file: Path = typer.Option(None, "--file", "-f", help="SQL file to explain"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
):
    """Get a plain-English explanation of a SQL query."""
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        sql = file.read_text()
    elif not sql:
        if not sys.stdin.isatty():
            sql = sys.stdin.read()
        else:
            console.print("[red]Error:[/red] No SQL provided")
            raise typer.Exit(1)

    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    with console.status("Analyzing query..."):
        try:
            result = client.explain_query(sql, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print("\n[bold]Query Explanation[/bold]\n")
    console.print(Markdown(result.get("explanation", "No explanation available")))

    if result.get("steps"):
        console.print("\n[bold]Execution Steps:[/bold]")
        for i, step in enumerate(result["steps"], 1):
            console.print(f"  {i}. {step}")

    if result.get("complexity"):
        console.print(f"\n[bold]Complexity:[/bold] {result['complexity']}")


@app.command()
def plan(
    plan_text: str = typer.Argument(None, help="Execution plan to analyze"),
    file: Path = typer.Option(None, "--file", "-f", help="File containing execution plan"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
):
    """Analyze a query execution plan."""
    if file:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        plan_text = file.read_text()
    elif not plan_text:
        if not sys.stdin.isatty():
            plan_text = sys.stdin.read()
        else:
            console.print("[red]Error:[/red] No execution plan provided")
            raise typer.Exit(1)

    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    with console.status("Analyzing execution plan..."):
        try:
            result = client.post(
                "/api/optimize/plan",
                {"execution_plan": plan_text, "db_type": db_type}
            )
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    console.print("\n[bold]Execution Plan Analysis[/bold]\n")
    console.print(Markdown(result.get("explanation", "No analysis available")))

    if result.get("steps"):
        console.print("\n[bold]Recommendations:[/bold]")
        for i, step in enumerate(result["steps"], 1):
            console.print(f"  {i}. {step}")
