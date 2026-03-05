from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PROMPT_PATH = Path(__file__).with_name("prompts.yaml")


@dataclass(frozen=True)
class PromptBundle:
    system: str
    output_contract: str = ""
    safety: str = ""
    version: int | str | None = None


class PromptStore:
    def __init__(self, path: Path = DEFAULT_PROMPT_PATH):
        self.path = path
        self._data: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        if self._data is not None:
            return self._data

        if not self.path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.path}")

        with self.path.open("r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        return self._data

    def get(self, key: str) -> Any:
        """
        Retrieve a value using dot notation, e.g "assist.review_diff.system"
        """
        data = self.load()
        parts = key.split(".")
        cur: Any = data
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                raise KeyError(f"Prompt Key not found: {key}")
            cur = cur[p]
        return cur

    def bundle(self, base_key: str) -> PromptBundle:
        """
        Return a task bundle, e.g base_key="assist.review_diff"
        """
        node = self.get(base_key)
        if not isinstance(node, dict):
            raise TypeError(f"Prompt bundle at {base_key} must be a dict")

        system = str(node.get("system", "")).strip()
        if not system:
            raise ValueError(f"Missing required 'system' prompt at {base_key}")

        return PromptBundle(
            system=system,
            output_contract=str(node.get("output_contract", "")).strip(),
            safety=str(node.get("safety", "")).strip(),
            version=node.get("version"),
        )


# Singleton store you can import anywhere
prompts = PromptStore()
