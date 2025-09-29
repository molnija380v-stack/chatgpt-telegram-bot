import openai
import os

class OpenAIHelper:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        # Можешь поменять модель, если нужно
        self.model = "gpt-3.5-turbo"

    async def ask(self, messages):
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            return f"Ошибка OpenAI API: {str(e)}"
