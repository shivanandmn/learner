from crewai.llm import LLM
from litellm import completion
from typing import List, Dict, Any

class GeminiLLM(LLM):
    def __init__(self, model="gemini/gemini-1.5-flash", temperature=0.7, api_key=None):
        super().__init__(model)
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.stop = []
        self.model_name = model
        self.model_kwargs = {
            "temperature": temperature,
            "api_key": api_key
        }

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        try:
            response = completion(
                model=self.model,
                messages=[{"role": msg["role"], "content": msg["content"]} for msg in messages],
                temperature=self.temperature,
                api_key=self.api_key
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in GeminiLLM chat: {str(e)}")
            raise
