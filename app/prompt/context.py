from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ContextKeyError(KeyError):
    """
    Raised when required context keys are missing.
    """


@dataclass
class PromptContext:
    """
    Share runtime state across prompt orch steps.

    Supports dot-path r/w:
       - set ("git.diff", "...") -> {git: {diff: "..."}}
       - get ("git.diff") -> "..."
    """

    _data: dict[str, Any] = field(default_factory=dict)
