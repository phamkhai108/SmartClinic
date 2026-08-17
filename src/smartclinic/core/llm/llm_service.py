from __future__ import annotations

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
        return self.embed_many([item])[0]

    def embed_many(self, items: list[str], batch_size: int = 32) -> list[list[float]]:
        if not items:
            return []
        vectors: list[list[float]] = []
        for start in range(0, len(items), batch_size):
            batch = items[start : start + batch_size]
            try:
                result = self.client.embeddings.create(
                    model=self.model_id,
                    input=batch,
                )
                ordered = sorted(result.data, key=lambda row: row.index)
                vectors.extend(list(row.embedding) for row in ordered)
            except Exception:
                # Some local OpenAI-compatible servers reject list input.
                for text in batch:
                    result = self.client.embeddings.create(
                        model=self.model_id,
                        input=text,
                    )
                    vectors.append(list(result.data[0].embedding))
        if len(vectors) != len(items):
            raise RuntimeError(
                f"Embedding count mismatch: got {len(vectors)}, expected {len(items)}"
            )
        return vectors

    def chat(self, messages: list[dict]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
        )
        return completion.choices[0].message.content
