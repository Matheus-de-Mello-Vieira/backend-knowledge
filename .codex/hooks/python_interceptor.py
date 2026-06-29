#!/usr/bin/env python3
"""Hook to enforce pyenv usage for Python commands in this project."""
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Constants
HOOK_EVENT = "PreToolUse"
TOOL_BASH = "Bash"
PYENV_CMD = "pyenv"
PYENV_EXEC_PREFIX = "pyenv exec python"
PYTHON_VERSION_FILE = ".python-version"
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
        if needs_pyenv_wrapper(command):
            validate_and_rewrite_python_command(command)

    # Allow command to proceed unchanged
    send_response(create_response("allow"))


def needs_pyenv_wrapper(command: str) -> bool:
    """Check if command uses Python and isn't already wrapped."""
    return bool(PYTHON_COMMAND_PATTERN.search(command)) and PYENV_EXEC_PREFIX not in command


def validate_and_rewrite_python_command(command: str) -> None:
    """Validate environment and rewrite Python commands to use pyenv."""
    if not is_pyenv_installed():
        hard_fail("pyenv is not installed. Please install pyenv to manage Python environments.")

    venv_name = read_virtualenv_name()
    if not venv_name:
        send_response(create_response(
            "deny",
            f"{PYTHON_VERSION_FILE} file not found in project root."
        ))

    if not ensure_virtualenv_exists(venv_name):
        send_response(create_response(
            "deny",
            f"Failed to create pyenv virtualenv '{venv_name}'. "
            f"Please create it manually: pyenv virtualenv <version> {venv_name}"
        ))

    updated_command = rewrite_python_command(command)
    send_response(create_response("allow", updated_command=updated_command))


def is_pyenv_installed() -> bool:
    """Check if pyenv is available in PATH."""
    try:
        subprocess.run([PYENV_CMD, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def hard_fail(error_message: str) -> None:
    """Hard fail with error message - stops Codex execution completely."""
    sys.stderr.write(f"ERROR: {error_message}\n")
    sys.exit(2)


def read_virtualenv_name() -> Optional[str]:
    """Read virtualenv name from .python-version file."""
    version_file = Path.cwd() / PYTHON_VERSION_FILE
    if not version_file.exists():
        return None
    return version_file.read_text().strip()


def ensure_virtualenv_exists(venv_name: str) -> bool:
    """Ensure virtualenv exists, creating it if necessary."""
    return virtualenv_exists(venv_name) or create_virtualenv(venv_name)


def virtualenv_exists(name: str) -> bool:
    """Check if a pyenv virtualenv with given name exists."""
    try:
        result = subprocess.run(
            [PYENV_CMD, 'virtualenvs', '--bare'],
            capture_output=True,
            text=True,
            check=True
        )
        return name in result.stdout
    except subprocess.CalledProcessError:
        return False


def create_virtualenv(venv_name: str) -> bool:
    """Create a pyenv virtualenv with the given name."""
    version_prefix = extract_python_version(venv_name)
    if not version_prefix:
        return False

    full_version = find_matching_python_version(version_prefix)
    if not full_version:
        return False

    try:
        subprocess.run(
            [PYENV_CMD, 'virtualenv', full_version, venv_name],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def extract_python_version(venv_name: str) -> Optional[str]:
    """Extract Python version from virtualenv name (e.g., 'codex-tools-3.13' -> '3.13')."""
    parts = venv_name.rsplit('-', 1)
    return parts[1] if len(parts) == 2 else None


def find_matching_python_version(version_prefix: str) -> Optional[str]:
    """Find installed Python version matching the prefix (e.g., '3.13' -> '3.13.11')."""
    try:
        result = subprocess.run(
            [PYENV_CMD, 'versions', '--bare'],
            capture_output=True,
            text=True,
            check=True
        )
        versions = result.stdout.strip().split('\n')
        matching = [v for v in versions if v.startswith(f"{version_prefix}.")]
        return matching[0] if matching else None
    except subprocess.CalledProcessError:
        return None


def rewrite_python_command(command: str) -> str:
    """Replace any Python interpreter command token with pyenv exec python."""
    return PYTHON_COMMAND_PATTERN.sub(
        lambda match: f"{match.group('prefix')}{PYENV_EXEC_PREFIX}",
        command,
        count=1,
    )


def create_response(decision: str, reason: str = None, updated_command: str = None) -> dict:
    """Build a hook response."""
    output = {"hookEventName": HOOK_EVENT}

    if decision == "deny":
        output["permissionDecision"] = "deny"
        output["permissionDecisionReason"] = reason
    elif decision == "allow":
        output["permissionDecision"] = "allow"
        if updated_command:
            output["updatedInput"] = {"command": updated_command}

    return {"hookSpecificOutput": output}


def send_response(response: dict) -> None:
    """Send response and exit."""
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
