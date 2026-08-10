#!/usr/bin/env python3
"""Hook to enforce uv usage for Python commands in this project."""
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

# Constants
HOOK_EVENT = "PreToolUse"
TOOL_BASH = "Bash"
UV_CMD = "uv"
UV_RUN_PREFIX = "uv run python"
PYTHON_COMMAND_PATTERN = re.compile(
    r'(?P<prefix>^\s*|[;|&()]\s*)'
    r'(?P<command>(?:[^\s;|&()]+/)?python\d*(\.\d+)?)\b'
)


def main() -> None:
    """Main entry point for the hook."""
    hook_input = json.loads(sys.stdin.read())
    tool_name = hook_input.get("tool_name")

    if tool_name == TOOL_BASH:
        command = hook_input.get("tool_input", {}).get("command", "")
        if needs_uv_wrapper(command):
            validate_and_rewrite_python_command(command)

    # Command doesn't need modification - exit silently
    sys.exit(0)


def needs_uv_wrapper(command: str) -> bool:
    """Check if command uses Python and isn't already wrapped."""
    return bool(PYTHON_COMMAND_PATTERN.search(command)) and UV_RUN_PREFIX not in command


def validate_and_rewrite_python_command(command: str) -> None:
    """Validate environment and rewrite Python commands to use uv."""
    if not is_uv_installed():
        hard_fail("uv is not installed. Please install uv to manage Python environments.")

    ensure_venv_exists()
    updated_command = rewrite_python_command(command)
    send_response("allow", updated_command=updated_command)


def is_uv_installed() -> bool:
    """Check if uv is available in PATH."""
    try:
        subprocess.run([UV_CMD, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def ensure_venv_exists() -> None:
    """Ensure .venv exists, creating it via uv sync if necessary."""
    venv_path = Path.cwd() / ".venv"
    if not venv_path.exists():
        try:
            subprocess.run([UV_CMD, "sync"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            hard_fail("Failed to create virtual environment. Please run 'uv sync' manually.")


def hard_fail(error_message: str) -> None:
    """Hard fail with error message - stops Codex execution completely."""
    sys.stderr.write(f"ERROR: {error_message}\n")
    sys.exit(2)


def rewrite_python_command(command: str) -> str:
    """Replace any Python interpreter command token with uv run python."""
    return PYTHON_COMMAND_PATTERN.sub(
        lambda match: f"{match.group('prefix')}{UV_RUN_PREFIX}",
        command,
        count=1,
    )


def send_response(decision: Literal["allow", "deny"], reason: str = None, updated_command: str = None) -> None:
    """Build and send hook response, then exit."""
    assert decision in ("allow", "deny"), f"Invalid decision: {decision}"

    # If allow without modification, exit silently
    if decision == "allow" and not updated_command:
        sys.exit(0)

    # Build response
    output = {"hookEventName": HOOK_EVENT, "permissionDecision": decision}

    if decision == "deny":
        output["permissionDecisionReason"] = reason
    else:  # decision == "allow" with updated_command
        output["updatedInput"] = {"command": updated_command}

    response = {"hookSpecificOutput": output}
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
