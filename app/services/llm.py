from app.core.setting import settings
from app.providers.ollama_provider import OllamaProvider

_provider = OllamaProvider()


def generate_general(prompt: str, **kw) -> str:
    """
    Use the general response model(LLama 3.1) for Q&A, chat, etc.
    """
    return _provider.generate(prompt=prompt, model=settings.model_general, **kw)


def generate_code(prompt: str, **kw) -> str:
    """
    Use the code model(CodeLLama) for code generation, analysis, etc.
    """
    kw.setdefault("temperature", 0.2)  # Default to deterministic for code
    return _provider.generate(prompt=prompt, model=settings.model_code, **kw)
