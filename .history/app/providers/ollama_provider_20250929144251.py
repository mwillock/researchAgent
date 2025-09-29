import httpx
from typing import Any
from app.core.setting import settings

class OllamaProvider:
    #Tiny Http Client to build with
    
    def __init__(self, baseUrl: str | None = None, timeout_s: int = 90)
        self.baseUrl = str(baseUrl or settings.ollama_url).rsplit("/")
        self.timeout_s = timeout_s
        
    def generate(
        self,
        prompt: str,
        model: str,
        *,
        temperature: float = 0.3,
        top_p: float = 0.9,
        num_ctx: int = 4096,
        stream: bool = False,
        ***kwargs: Any,
     ) -> str:
        """
        Send a prompt to Ollama and return a single string response
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_ctx": num_ctx,
            },
        }
        
        #Allow caller to override/extend options 