"""
MY AI - Main Entry Point
Private Personal AI Assistant & Companion
Runs with: python -m app.main
"""
import sys
import os
import argparse
from typing import Optional
from app.config import config
from app.logging_config import logger

BANNER = r"""
===================================================================
   __  ____   __     _    ___ 
  /  |/  /\ \ / /    / \  |_ _|
 / /|_/ /  \ V /    / _ \  | | 
/ /  / /    | |    / ___ \ | | 
\/  /_/     |_|   /_/   \_|___|
                               
  MY AI — Private Local-First Personal Assistant & Companion
  100% In-House AI Models & Deterministic Systems • Zero Cloud LLMs
===================================================================
"""

def print_status() -> None:
    print(BANNER)
    print(f"System Version : {config.version}")
    print(f"Base Directory : {config.base_dir}")
    print(f"Database Path  : {config.db_path}")
    print(f"Local Storage  : {config.data_dir}")
    print(f"Privacy Mode   : LOCAL-FIRST STRICT (External APIs = Disabled)")
    print(f"Foundation     : Ready")
    print("===================================================================\n")

def run_cli_interactive() -> None:
    print(BANNER)
    print("Type your message or 'exit' / 'quit' to end session.")
    print("Tip: You can ask questions, manage tasks, set reminders, or talk.")
    print("-------------------------------------------------------------------")
    
    # Lazy import agent orchestration so foundation tests don't require full pipeline immediately
    try:
        from app.brain.reasoning import AgentOrchestrator
        orchestrator = AgentOrchestrator()
    except Exception as e:
        logger.warning(f"Starting in foundation fallback mode: {e}")
        orchestrator = None

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nMY AI: Goodbye! Your local session is safely stored.\n")
                break
                
            if orchestrator:
                response = orchestrator.process(user_input)
                print(f"MY AI > {response.text}")
            else:
                print(f"MY AI (Foundation) > Received: '{user_input}'. Core pipeline ready.")
        except (KeyboardInterrupt, EOFError):
            print("\nMY AI: Session closed.")
            break
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            print(f"MY AI > An error occurred: {e}")

def main(args_list: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="MY AI: Private Personal AI Assistant and Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {config.version}")
    parser.add_argument("--status", action="store_true", help="Print system status and paths")
    parser.add_argument("--message", "-m", type=str, help="Process a single message and exit")
    parser.add_argument("--json", action="store_true", help="Output JSON formatted response")
    
    args = parser.parse_args(args_list)

    config.ensure_directories()
    
    if args.status:
        print_status()
        return 0
        
    if args.message:
        try:
            from app.brain.reasoning import AgentOrchestrator
            import json
            orchestrator = AgentOrchestrator()
            res = orchestrator.process(args.message)
            if args.json:
                print(json.dumps(res.to_dict(), indent=2))
            else:
                print(res.text)
            return 0
        except Exception as e:
            logger.error(f"Error executing message command: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
            
    # Default: Interactive CLI
    run_cli_interactive()
    return 0

if __name__ == "__main__":
    sys.exit(main())
