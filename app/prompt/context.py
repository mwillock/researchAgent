from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


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

    def to_dict(self) -> dict[str, Any]:
        return self._data

    def update(self, mapping: Mapping[str, Any]) -> None:
        for key, v in mapping.items():
            self.set(key, v)

    def get(self, key: str, default: Any = ...) -> Any:
        """
        Get value by dot-path
        Its default is not provided and the key is missing, raises ContextKeyError.
        """
        parts = self._split(key)
        cur: Any = self._data

        for part in parts:
            if not isinstance(cur, dict) or part not in cur:
                if default is ...:
                    raise ContextKeyError(f"Context key '{key}' not found.")
                return default
            cur = cur[part]
        return cur

    def set(self, key: str, value: Any) -> None:
        """
        Set value by dot-path, creating intermediate dicts as needed.
        """
        parts = self._split(key)
        if not parts:
            raise ValueError("Context key cannot be empty.")

        cur: Any = self._data
        for part in parts[:-1]:
            if part not in cur:
                cur[part] = {}
            elif not isinstance(cur[part], dict):
                # Prevent overwriting non-dict value with dict
                raise TypeError(
                    f"Cannot set '{key}': '{part}' is not a dict.(found {type(cur[part]).__name__})"
                )
            cur = cur[part]
        cur[parts[-1]] = value

    @staticmethod
    def _split(key: str) -> list[str]:
        key = key.strip()
        if not key:
            return []
        return [p for p in key.split(".") if p]
