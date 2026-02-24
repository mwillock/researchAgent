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
