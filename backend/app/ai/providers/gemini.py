from typing import List, Dict, Any, Optional
import time
import json
import httpx
from .base import BaseAIProvider
from ..schemas import AIRequestMessage, AIResponse, AIResponseInfo, AIToolCall
from ..exceptions import (
    AINotConfiguredException,
    AIProviderException,
    AIAuthException,
    AIRateLimitException,
    AIInvalidRequestException
)
from ..config import ai_config

class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"
    default_model = "gemini-1.5-flash"

    def __init__(self):
        key = ai_config.GEMINI_API_KEY
        if not key or key.strip() == "" or key.startswith("your_") or "mock" in key.lower():
            raise AINotConfiguredException("Google Gemini API key is not configured or is a placeholder.")
        self.api_key = key.strip()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(
        self,
        messages: List[AIRequestMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        start_time = time.time()
        _ = metadata

        # Adapt model name if alien model passed
        if not model or model.startswith("gpt-") or model.startswith("mistral-") or model.startswith("llama-"):
            model = self.default_model

        system_instruction = None
        contents = []
        is_json_request = False

        for msg in messages:
            content_text = msg.content or ""
            if "json" in content_text.lower():
                is_json_request = True

            if msg.role == "system":
                system_instruction = {"parts": [{"text": content_text}]}
            elif msg.role in ["user", "human"]:
                contents.append({
                    "role": "user",
                    "parts": [{"text": content_text}]
                })
            elif msg.role in ["assistant", "model"]:
                contents.append({
                    "role": "model",
                    "parts": [{"text": content_text}]
                })

        generation_config: Dict[str, Any] = {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
        if is_json_request:
            generation_config["responseMimeType"] = "application/json"

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": generation_config
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        if tools:
            # Map standard OpenAI tool definitions to Gemini functionDeclarations if needed
            func_decls = []
            for t in tools:
                if t.get("type") == "function" and "function" in t:
                    func_decls.append(t["function"])
                elif "name" in t:
                    func_decls.append(t)
            if func_decls:
                payload["tools"] = [{"functionDeclarations": func_decls}]

        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json=payload, headers={"Content-Type": "application/json"})
        except httpx.TimeoutException:
            raise AIProviderException("Gemini API request timed out after 60s.")
        except Exception as e:
            raise AIProviderException(f"Network error connecting to Gemini API: {str(e)}")

        latency = (time.time() - start_time) * 1000

        if res.status_code == 400:
            raise AIInvalidRequestException(f"Gemini Invalid Request: {res.text}")
        elif res.status_code in [401, 403]:
            raise AIAuthException(f"Gemini Authentication Error: {res.text}")
        elif res.status_code == 429:
            raise AIRateLimitException(f"Gemini Rate Limit Exceeded: {res.text}")
        elif res.status_code >= 500:
            raise AIProviderException(f"Gemini Upstream Server Error ({res.status_code}): {res.text}")
        elif res.status_code != 200:
            raise AIProviderException(f"Gemini API returned unexpected status {res.status_code}: {res.text}")

        data = res.json()
        candidates = data.get("candidates", [])
        content_text = None
        finish_reason = None
        parsed_tool_calls = None

        if candidates:
            first_cand = candidates[0]
            finish_reason = first_cand.get("finishReason")
            parts = first_cand.get("content", {}).get("parts", [])
            text_chunks = []
            for p in parts:
                if "text" in p:
                    text_chunks.append(p["text"])
                if "functionCall" in p:
                    fc = p["functionCall"]
                    if parsed_tool_calls is None:
                        parsed_tool_calls = []
                    parsed_tool_calls.append(
                        AIToolCall(
                            id=f"call_{int(time.time() * 1000)}",
                            type="function",
                            function={
                                "name": fc.get("name", ""),
                                "arguments": json.dumps(fc.get("args", {}))
                            }
                        )
                    )
            if text_chunks:
                content_text = "".join(text_chunks)

        usage = data.get("usageMetadata", {})
        info = AIResponseInfo(
            provider="gemini",
            model=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            total_tokens=usage.get("totalTokenCount", 0),
            finish_reason=finish_reason,
            request_id=None,
            latency_ms=latency
        )

        return AIResponse(content=content_text, tool_calls=parsed_tool_calls, info=info)
