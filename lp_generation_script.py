#!/usr/bin/env python3
"""Script to run LP agent for FastAPI integration."""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path to enable imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console

from lp_agent.prompt import LP_GENERATION_PROMPT
from tools.agent import Agent
from utils.llm_client import get_client
from utils.workspace_manager import WorkspaceManager

MAX_OUTPUT_TOKENS_PER_TURN = 32768


class EventEmitter:
    """Emits events to events.jsonl file for FastAPI streaming."""

    def __init__(self, workspace_path: Path, request_id: str):
        self.workspace_path = workspace_path
        self.request_id = request_id
        self.events_file = workspace_path.parent / "events.jsonl"

    def emit_event(
        self,
        event_type: str,
        message: str,
        tool_name: str = None,
        tool_input: dict = None,
        tool_output: str = None,
        file_path: str = None,
        command: str = None,
        progress: int = 0,
    ):
        """Emit an event to the events file."""
        event = {
            "event_type": event_type,
            "request_id": self.request_id,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "tool_name": tool_name,
                "tool_input": tool_input or {},
                "tool_output": tool_output,
                "file_path": file_path,
                "command": command,
            },
        }

        try:
            with open(self.events_file, "a") as f:
                f.write(json.dumps(event) + "\n")
                f.flush()  # Ensure immediate write
        except Exception as e:
            print(f"Warning: Failed to emit event: {e}")


class EventAwareAgent:
    """Wrapper around the agent that emits events for tool calls."""

    def __init__(self, agent, event_emitter: EventEmitter):
        self.agent = agent
        self.event_emitter = event_emitter
        self.original_tools = agent.tools
        self._wrap_tools()

    def _wrap_tools(self):
        """Wrap only safe tools to emit events."""
        # Only wrap tools we know have simple schemas
        # Temporarily removing bash due to validation issues
        safe_tools_to_wrap = ["str_replace_editor"]

        for tool in self.agent.tools:
            print(f"Found tool: {tool.name}")

            # Only wrap tools in our safe list
            if tool.name not in safe_tools_to_wrap:
                print(f"Skipping tool wrapping for: {tool.name}")
                continue

            original_run = tool.run

            def create_wrapped_run(original_tool):
                def wrapped_run(tool_input, dialog_messages=None):
                    # Safely extract common fields that might exist
                    file_path = None
                    command = None

                    if isinstance(tool_input, dict):
                        file_path = tool_input.get("path") or tool_input.get(
                            "file_path"
                        )
                        command = tool_input.get("command")

                    # Emit tool start event
                    try:
                        self.event_emitter.emit_event(
                            event_type="tool_call_started",
                            message=f"Starting {original_tool.name}",
                            tool_name=original_tool.name,
                            tool_input=(
                                tool_input if isinstance(tool_input, dict) else {}
                            ),
                            file_path=file_path,
                            command=command,
                        )
                    except Exception as e:
                        print(
                            f"Warning: Failed to emit start event for {original_tool.name}: {e}"
                        )

                    # Run the original tool with original input (don't modify it)
                    try:
                        result = original_run(tool_input, dialog_messages)
                    except Exception as e:
                        # Emit error event and re-raise
                        try:
                            self.event_emitter.emit_event(
                                event_type="tool_call_completed",
                                message=f"Failed {original_tool.name}: {str(e)}",
                                tool_name=original_tool.name,
                                tool_input=(
                                    tool_input if isinstance(tool_input, dict) else {}
                                ),
                                tool_output=f"Error: {str(e)}",
                                file_path=file_path,
                                command=command,
                            )
                        except:
                            pass
                        raise e

                    # Emit tool completion event
                    try:
                        self.event_emitter.emit_event(
                            event_type="tool_call_completed",
                            message=f"Completed {original_tool.name}",
                            tool_name=original_tool.name,
                            tool_input=(
                                tool_input if isinstance(tool_input, dict) else {}
                            ),
                            tool_output=str(result)[:500],  # Truncate long output
                            file_path=file_path,
                            command=command,
                        )
                    except Exception as e:
                        print(
                            f"Warning: Failed to emit completion event for {original_tool.name}: {e}"
                        )

                    return result

                return wrapped_run

            tool.run = create_wrapped_run(tool)
            print(f"Wrapped tool: {tool.name}")

    def run_agent(self, *args, **kwargs):
        """Run the agent with event emission."""
        return self.agent.run_agent(*args, **kwargs)


def run_lp_agent(
    workspace: Path,
    brand_identity: dict,
    creative_brief: str,
    max_turns: int,
    timeout_minutes: int,
    request_id: str,
    model_slug: str,
) -> bool:
    """Run the landing page agent with the provided configuration."""

    # Set up event emitter
    event_emitter = EventEmitter(workspace, request_id)

    # Emit generation started event
    event_emitter.emit_event(
        event_type="generation_started",
        message="Starting landing page generation",
        progress=0,
    )

    # Set up logging to suppress most output
    logs_path = workspace.parent / "agent_logs.txt"
    if logs_path.exists():
        logs_path.unlink()

    logger_for_agent_logs = logging.getLogger("agent_logs")
    logger_for_agent_logs.setLevel(logging.DEBUG)
    logger_for_agent_logs.addHandler(logging.FileHandler(logs_path))
    # Don't add StreamHandler to reduce output noise

    try:
        # Initialize console
        console = Console()
        provider, model = model_slug.split("/")
        kwargs = {
            "model_name": model,
        }
        if provider == "anthropic":
            kwargs["use_caching"] = True
        if model in ["gpt-4.1", "gpt-4o"]:
            kwargs["cot_model"] = False

        # Initialize LLM client
        client = get_client(
            provider + "-direct",
            **kwargs,
        )

        # Initialize workspace manager
        workspace_manager = WorkspaceManager(root=workspace)

        # Initialize agent
        agent = Agent(
            client=client,
            workspace_manager=workspace_manager,
            console=console,
            logger_for_agent_logs=logger_for_agent_logs,
            max_output_tokens_per_turn=MAX_OUTPUT_TOKENS_PER_TURN,
            max_turns=max_turns,
            ask_user_permission=False,  # Set to False for non-interactive use
        )

        # Wrap agent with event emitter
        event_aware_agent = EventAwareAgent(agent, event_emitter)

        # Create the landing page prompt with the provided parameters
        landing_page_prompt = LP_GENERATION_PROMPT.format(
            brand_identity=brand_identity or "Default brand identity",
            creative_brief=creative_brief,
        )

        logger_for_agent_logs.info(
            f"Starting LP generation with prompt: {landing_page_prompt[:200]}..."
        )

        # Run the agent with the landing page prompt
        result = event_aware_agent.run_agent(landing_page_prompt, resume=False)

        logger_for_agent_logs.info(f"Agent completed with result: {result}")

        # Check if generation was successful by looking for modified files
        # The agent should have created/modified files in the workspace
        generated_files = (
            list(workspace.rglob("*.tsx"))
            + list(workspace.rglob("*.ts"))
            + list(workspace.rglob("*.css"))
        )

        if generated_files:
            logger_for_agent_logs.info(f"Found {len(generated_files)} generated files")
            event_emitter.emit_event(
                event_type="generation_completed",
                message=f"Successfully generated {len(generated_files)} files",
                progress=100,
            )
            return True
        else:
            logger_for_agent_logs.error("No generated files found")
            event_emitter.emit_event(
                event_type="error", message="No generated files found", progress=100
            )
            return False

    except Exception as e:
        logger_for_agent_logs.error(f"Error running LP agent: {e}")
        event_emitter.emit_event(
            event_type="error",
            message=f"Error running LP agent: {str(e)}",
            progress=100,
        )
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate landing page using AI agent")
    parser.add_argument("--config", required=True, help="JSON config string")
    args = parser.parse_args()

    try:
        config = json.loads(args.config)
        workspace = Path(config["workspace"])

        # Ensure workspace exists
        if not workspace.exists():
            print(f"ERROR: Workspace does not exist: {workspace}")
            sys.exit(1)

        print(f"Starting landing page generation in workspace: {workspace}")

        # Run the agent
        result = run_lp_agent(
            workspace=workspace,
            brand_identity=config.get("brand_identity"),
            creative_brief=config["creative_brief"],
            max_turns=config.get("max_turns", 50),
            timeout_minutes=config.get("timeout_minutes", 15),
            request_id=config.get("request_id", "unknown"),
            model_slug=config.get("model_slug", "claude-sonnet-4-20250514"),
        )

        if result:
            print("SUCCESS: Landing page generated")
            sys.exit(0)
        else:
            print("ERROR: Failed to generate landing page")
            sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON config: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"ERROR: Missing required config key: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
