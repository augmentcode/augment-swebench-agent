#!/usr/bin/env python3
"""
Script to run the Landing Page Agent.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console

from lp_agent.prompt import LP_GENERATION_PROMPT
from tools.agent import Agent
from utils.llm_client import get_client
from utils.workspace_manager import WorkspaceManager

MAX_OUTPUT_TOKENS_PER_TURN = 32768
MAX_TURNS = 200

# Define the prompt for the landing page generation
brand_identity = "color = green"
brief_path = "data/dose/brief.md"
with open(brief_path, "r") as file:
    creative_brief = file.read()
LANDING_PAGE_PROMPT = LP_GENERATION_PROMPT.format(
    brand_identity=brand_identity, creative_brief=creative_brief
)


def run_lp_agent(
    workspace: Path,
    brand_identity: dict,
    creative_brief: str,
    max_turns: int,
) -> bool:
    """Run the Landing Page Agent."""
    logs_path = "lp_agent_logs.txt"
    if os.path.exists(logs_path):
        os.remove(logs_path)
    logger_for_agent_logs = logging.getLogger("agent_logs")
    logger_for_agent_logs.setLevel(logging.DEBUG)
    logger_for_agent_logs.addHandler(logging.FileHandler(logs_path))
    logger_for_agent_logs.addHandler(logging.StreamHandler())

    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it to your Anthropic API key.")
        sys.exit(1)

    # Initialize console
    console = Console()

    logger_for_agent_logs.info("Landing Page Agent started.")

    # Initialize LLM client
    # client = get_client(
    #     "anthropic-direct",
    #     # model_name="claude-sonnet-4-20250514",
    #     model_name="claude-3-5-haiku-latest",
    #     use_caching=True,
    # )

    client = get_client(
        "openai-direct",
        model_name="gpt-4.1",
        cot_model=False,
    )

    # Initialize workspace manager
    workspace_manager = WorkspaceManager(
        root=workspace,
    )

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

    instruction = LP_GENERATION_PROMPT.format(
        brand_identity=brand_identity, creative_brief=creative_brief
    )

    logger_for_agent_logs.info(f"User instruction:\n{instruction}\n-------------")

    # Run the agent with the user input
    logger_for_agent_logs.info("\nAgent is thinking...")
    try:
        result = agent.run_agent(instruction, resume=False)  # Start a new session
        logger_for_agent_logs.info(f"Agent: {result}")
    except Exception as e:
        logger_for_agent_logs.info(f"Error: {str(e)}")

    logger_for_agent_logs.info("\n" + "-" * 40 + "\n")
    console.print("[bold]Landing page generation complete.[/bold]")


if __name__ == "__main__":
    run_lp_agent(
        workspace=Path("my-landing").resolve(),
        brand_identity=brand_identity,
        creative_brief=creative_brief,
        max_turns=MAX_TURNS,
    )
