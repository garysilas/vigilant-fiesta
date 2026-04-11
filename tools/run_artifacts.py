import json
import os
from dataclasses import asdict
from typing import Any


def _get_runs_dir() -> str:
    """Get the base runs directory path."""
    return os.path.join("data", "runs")


def create_run_dir(run_id: str) -> str:
    """Create the run directory structure for a given run_id.

    Args:
        run_id: Unique identifier for the run

    Returns:
        Path to the created run directory
    """
    run_dir = os.path.join(_get_runs_dir(), run_id)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def save_json(path: str, data: Any) -> None:
    """Save data as JSON to the specified path.

    Args:
        path: Full file path to save to
        data: Data to serialize (dataclass, dict, list, etc.)
    """
    # Convert dataclass to dict if needed
    if hasattr(data, "__dataclass_fields__"):
        data = asdict(data)
    # Handle lists of dataclasses
    elif isinstance(data, list) and data and hasattr(data[0], "__dataclass_fields__"):
        data = [asdict(item) for item in data]

    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_text(path: str, text: str) -> None:
    """Save text to the specified path.

    Args:
        path: Full file path to save to
        text: Text content to write
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_json(path: str) -> Any:
    """Load JSON data from the specified path.

    Args:
        path: Full file path to load from

    Returns:
        Parsed JSON data
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    """Load text from the specified path.

    Args:
        path: Full file path to load from

    Returns:
        File contents as string
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
