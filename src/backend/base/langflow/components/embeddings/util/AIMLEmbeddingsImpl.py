import concurrent.futures
import json
from typing import List

import httpx
from langchain_core.pydantic_v1 import BaseModel, SecretStr
from loguru import logger

from langflow.field_typing import Embeddings


class AIMLEmbeddingsImpl(BaseModel, Embeddings):
    embeddings_completion_url: str = "https://api.aimlapi.com/v1/embeddings"

    api_key: SecretStr
    model: str

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = [None] * len(texts)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
        }

        with httpx.Client() as client:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for i, text in enumerate(texts):
                    futures.append((i, executor.submit(self._embed_text, client, headers, text)))

                for index, future in futures:
                    try:
                        result_data = future.result()
                        assert len(result_data["data"]) == 1, "Expected one embedding"
                        embeddings[index] = result_data["data"][0]["embedding"]
                    except (
                        httpx.HTTPStatusError,
                        httpx.RequestError,
                        json.JSONDecodeError,
                        KeyError,
                    ) as e:
                        logger.error(f"Error occurred: {e}")
                        raise

        return embeddings  # type: ignore

    def _embed_text(self, client: httpx.Client, headers: dict, text: str) -> dict:
        payload = {
            "model": self.model,
            "input": text,
        }
        response = client.post(
            self.embeddings_completion_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        result_data = response.json()
        return result_data

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]
