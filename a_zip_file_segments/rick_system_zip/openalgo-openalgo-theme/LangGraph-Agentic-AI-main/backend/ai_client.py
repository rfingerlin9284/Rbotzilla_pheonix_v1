import os
import google.generativeai as genai
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIModelClient:
    def __init__(self, api_key: str = None, base_url: str = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url # Not directly used by genai, but kept for consistency if other APIs are added
        self.model_name = model_name

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided or found in environment variables.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"AIModelClient initialized with model: {self.model_name}")

    async def chat_completion(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.model.generate_content_async(prompt, **kwargs)
            return response.text
        except Exception as e:
            logger.error(f"Error during AI chat completion: {e}")
            raise