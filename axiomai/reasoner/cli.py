"""
CLI for AxiomAI Reasoner using Typer.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .engine import Reasoner

app = typer.Typer()
console = Console()
reasoner = Reasoner()


@app.command()
def add_fact(predicate: str, source: str = "cli"):
    """Add a fact: add-fact 'Human(Socrates)'"""
    fact = reasoner.add_fact(predicate, source=source)
    console.print(f"[green]✓[/green] Added: {fact}")


@app.command()
def add_rule(rule_str: str, priority: int = 1):
    """Add a rule: add-rule 'IF Human(x) THEN Mortal(x)'"""
    rule = reasoner.add_rule(rule_str, priority=priority)
    console.print(f"[green]✓[/green] Added: {rule}")


@app.command()
def facts():
    """List all facts."""
    items = reasoner.list_facts()
    table = Table(title="Knowledge Base — Facts")
    table.add_column("Predicate", style="cyan")
    table.add_column("Source", style="dim")
    table.add_column("Confidence", style="yellow")
    for f in items:
        table.add_row(str(f.predicate), f.source or "-", f.confidence_source)
    console.print(table)


@app.command()
def rules():
    """List all rules."""
    items = reasoner.list_rules()
    table = Table(title="Knowledge Base — Rules")
    table.add_column("Rule", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Domain", style="dim")
    for r in items:
        table.add_row(str(r), str(r.priority), r.domain or "-")
    console.print(table)


@app.command()
def ask(query: str, style: str = "medium"):
    """Ask a query: ask 'Mortal(Socrates)'"""
    result = reasoner.ask(query)
    console.print(f"\n[bold]Query:[/bold] {query}")
    console.print(f"[bold]Result:[/bold] {result.result}")
    console.print(f"[bold]Mode:[/bold] {result.reasoning_mode}")
    console.print(f"[bold]Duration:[/bold] {result.duration_ms:.2f}ms\n")
    console.print(result.explain(style))
    console.print()


@app.command()
def prove(query: str):
    """Prove a query with detailed proof trace."""
    result = reasoner.ask(query)
    console.print(result.proof.to_text())


@app.command()
def extract(text: str, load: bool = True):
    """Extract facts and rules from natural language."""
    result = reasoner.extract(text, load=load)
    console.print(f"[green]Extracted {len(result['facts'])} facts, {len(result['rules'])} rules[/green]")
    for f in result["facts"]:
        console.print(f"  fact: {f.predicate}")
    for r in result["rules"]:
        console.print(f"  rule: {r}")


@app.command()
def forward():
    """Run forward chaining and show all derived facts."""
    result = reasoner.derive_all()
    console.print("\n[bold]Forward Chaining Results[/bold]")
    console.print(f"New facts: {len(result.new_facts)}")
    console.print(f"Total derived: {len(result.all_derived)}")
    console.print(f"Duration: {result.duration_ms:.2f}ms\n")
    for f in result.all_derived:
        console.print(f"  • {f.predicate}")
    console.print()


@app.command()
def contradictions():
    """Check for contradictions."""
    reports = reasoner.check_consistency()
    if not reports:
        console.print("[green]✓ Knowledge base is consistent[/green]")
    else:
        console.print(f"[red]⚠ Found {len(reports)} contradictions:[/red]")
        for r in reports:
            console.print(f"  • {r.fact1} ↔ {r.fact2}")
            console.print(f"    {r.explanation}")


@app.command()
def reset():
    """Clear all knowledge."""
    reasoner.reset()
    console.print("[yellow]Knowledge base cleared[/yellow]")


@app.command()
def socrates():
    """Load Socrates example and prove mortality."""
    reasoner.load_socrates()
    console.print("[green]Loaded Socrates example[/green]")
    result = reasoner.ask("Mortal(Socrates)")
    console.print(result.proof.to_text())


@app.command()
def solve_sudoku():
    """Solve the default Sudoku."""
    from .engines.constraints import solve_sudoku
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    solution = solve_sudoku(puzzle)
    if solution:
        console.print("[green]Sudoku Solution:[/green]")
        for row in solution:
            console.print("  " + " ".join(str(c) for c in row))
    else:
        console.print("[red]No solution found[/red]")


def main():
    """Entry point for the axiomai console script."""
    app()


if __name__ == "__main__":
    main()
