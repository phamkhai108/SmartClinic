from openai import OpenAI


class LLMModel:
    def __init__(self, openai_api_url: str, openai_api_key: str, model_id: str) -> None:
        self.model_id = model_id

        self.client = OpenAI(
            base_url=openai_api_url,
            api_key=openai_api_key,
            timeout=40,
        )

    def embed(self, item: str) -> list[float]:
        result = self.client.embeddings.create(
            model=self.model_id,
            input=item,
        )
        return result.data[0].embedding

    def chat(self, messages: list[dict]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
        )
        return completion.choices[0].message.content


# ollama_nomic = LLMModel(
#     openai_api_url="http://localhost:11434/v1",
#     openai_api_key="111",
#     model_id="karuniaperjuangan/multilingual-e5-small:latest",
# )
# ollama_bge = LLMModel(
#     openai_api_url="http://localhost:11434/v1",
#     openai_api_key="111",
#     model_id="yxchia/multilingual-e5-base:Q8_0",
# )
