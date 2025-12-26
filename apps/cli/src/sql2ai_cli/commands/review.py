"""Code review commands for SQL2.AI CLI."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sql2ai_cli.utils.api import get_api_client
from sql2ai_cli.utils.config import get_config

app = typer.Typer(help="Code review and quality checks")
console = Console()


@app.command()
def code(
    sql: str = typer.Argument(None, help="SQL code to review"),
    file: Path = typer.Option(None, "--file", "-f", help="SQL file to review"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Review SQL code for issues and best practices."""
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

    with console.status("Reviewing code..."):
        try:
            result = client.review_code(sql, db_type)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if json_output:
        import json
        console.print(json.dumps(result, indent=2))
        return

    # Display results
    score = result.get("score", 0)
    score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

    console.print(f"\n[bold]Code Review Results[/bold] - Score: [{score_color}]{score}/100[/{score_color}]\n")

    if result.get("summary"):
        console.print(Panel(result["summary"], title="Summary"))

    issues = result.get("issues", [])
    if issues:
        table = Table(title="Issues Found")
        table.add_column("Severity", style="bold")
        table.add_column("Rule")
        table.add_column("Message")
        table.add_column("Line")

        for issue in issues:
            severity = issue.get("severity", "info")
            severity_style = {
                "error": "[red]ERROR[/red]",
                "warning": "[yellow]WARNING[/yellow]",
                "info": "[blue]INFO[/blue]",
            }.get(severity, severity)

            table.add_row(
                severity_style,
                issue.get("rule", "-"),
                issue.get("message", ""),
                str(issue.get("line", "-")),
            )

        console.print(table)
    else:
        console.print("[green]✓[/green] No issues found!")


@app.command("dir")
def review_directory(
    path: Path = typer.Argument(".", help="Directory to review"),
    pattern: str = typer.Option("*.sql", "--pattern", "-p", help="File pattern"),
    db_type: str = typer.Option(None, "--type", "-t", help="Database type"),
):
    """Review all SQL files in a directory."""
    if not path.exists():
        console.print(f"[red]Error:[/red] Directory not found: {path}")
        raise typer.Exit(1)

    sql_files = list(path.rglob(pattern))
    if not sql_files:
        console.print(f"[yellow]No SQL files found matching '{pattern}'[/yellow]")
        return

    console.print(f"\n[bold]Reviewing {len(sql_files)} SQL files...[/bold]\n")

    config = get_config()
    db_type = db_type or config.default_database
    client = get_api_client()

    total_issues = {"error": 0, "warning": 0, "info": 0}
    files_with_issues = []

    for sql_file in sql_files:
        try:
            sql = sql_file.read_text()
            result = client.review_code(sql, db_type)

            issues = result.get("issues", [])
            if issues:
                files_with_issues.append((sql_file, issues))
                for issue in issues:
                    severity = issue.get("severity", "info")
                    total_issues[severity] = total_issues.get(severity, 0) + 1

                console.print(f"[yellow]✗[/yellow] {sql_file.name}: {len(issues)} issues")
            else:
                console.print(f"[green]✓[/green] {sql_file.name}")

        except Exception as e:
            console.print(f"[red]✗[/red] {sql_file.name}: Error - {e}")

    # Summary
    console.print(f"\n[bold]Summary[/bold]")
    console.print(f"  Files reviewed: {len(sql_files)}")
    console.print(f"  Files with issues: {len(files_with_issues)}")
    console.print(f"  Errors: [red]{total_issues['error']}[/red]")
    console.print(f"  Warnings: [yellow]{total_issues['warning']}[/yellow]")
    console.print(f"  Info: [blue]{total_issues['info']}[/blue]")

    if total_issues["error"] > 0:
        raise typer.Exit(1)
