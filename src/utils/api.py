"""DeepSeek API 封装模块"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class DeepSeekClient:
    """DeepSeek API 客户端封装"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = (
            base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        ).rstrip("/")
        self.model = model or os.getenv("PERFFLOW_MODEL", "deepseek-chat")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """发送聊天请求并返回响应内容"""
        if not self.api_key:
            raise ValueError("未配置 DEEPSEEK_API_KEY，请在 .env 文件中设置")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def close(self):
        """关闭 HTTP 客户端"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
