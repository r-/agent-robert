"""R.O.B.E.R.T. CLI Entry Point"""

import asyncio
import typer
from robert.composition.startup import create_agent_service

app = typer.Typer(help="Agent R.O.B.E.R.T. CLI")

# Initialize agent via composition root
_agent = create_agent_service()

async def _chat_loop():
    typer.echo("Agent R.O.B.E.R.T. (Minimal Core) v0.1.0")
    typer.echo("-" * 40)
    
    session_key = "cli-default"
    
    while True:
        try:
            line = input("You: ")
            if line.lower() in ["exit", "quit"]:
                break
                
            response = await _agent.process(line, session_key)
            print(f"ROBERT: {response.content}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def chat():
    """Start an interactive chat session."""
    asyncio.run(_chat_loop())

@app.command()
def version():
    """Show version info."""
    typer.echo("Agent R.O.B.E.R.T. v0.1.0")

if __name__ == "__main__":
    app()
