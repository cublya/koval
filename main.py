import typer
import yaml
from pathlib import Path
from apps.cli.app import run_cli
# from apps.swarm import run_swarm # Will add later when ready

app = typer.Typer()

@app.command()
def cli():
    """
    Start the Single Player interactive mode (UI).
    """
    typer.echo("Starting Koval CLI...")
    run_cli()

@app.command()
def swarm(task: str):
    """
    Start the Multi-Agent Swarm for a complex task.
    """
    typer.echo(f"Starting Swarm for task: {task}")
    # run_swarm(task)
    typer.echo("Swarm mode not yet implemented.")

if __name__ == "__main__":
    app()
