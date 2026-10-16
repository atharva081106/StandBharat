from typing import List, Dict, Any, Optional
import time
from .base import BaseAIProvider
from ..schemas import AIRequestMessage, AIResponse, AIResponseInfo
from ..exceptions import AINotConfiguredException, AIProviderException, AIAuthException, AIRateLimitException, AIInvalidRequestException
from ..config import ai_config
import openai

class MistralProvider(BaseAIProvider):
    provider_name = "mistral"
    default_model = "open-mistral-7b"

    def __init__(self):
        key = ai_config.MISTRAL_API_KEY
        if not key or key.strip() == "" or key.startswith("your_") or key.startswith("mstrl_dummy") or "mock" in key.lower():
            raise AINotConfiguredException("Mistral API key is not configured or is a placeholder.")
        self.client = openai.OpenAI(api_key=key, base_url="https://api.mistral.ai/v1")

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
        
        # If passed an openai default model like "gpt-4o", adapt to mistral model
        if not model or model.startswith("gpt-"):
            if ai_config.DEFAULT_MODEL and not ai_config.DEFAULT_MODEL.startswith("gpt-"):
                model = ai_config.DEFAULT_MODEL
            else:
                model = self.default_model

        oai_messages = []
        is_json_request = False
        for msg in messages:
            oai_msg = {"role": msg.role}
            if msg.content is not None:
                oai_msg["content"] = msg.content
                if "json" in msg.content.lower():
                    is_json_request = True
            if msg.tool_calls:
                oai_msg["tool_calls"] = [
                    {"id": tc.id, "type": tc.type, "function": tc.function}
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                oai_msg["tool_call_id"] = msg.tool_call_id
            oai_messages.append(oai_msg)
        
        # Ensure sufficient tokens for JSON strategy documents
        if is_json_request and max_tokens < 2048:
            max_tokens = 2048

        try:
            kwargs = {
                "model": model,
                "messages": oai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if tools:
                kwargs["tools"] = tools
            elif is_json_request:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
        except openai.AuthenticationError:
            # Never expose secrets in logs or exception messages
            raise AIAuthException("Mistral Authentication Error: Invalid or missing API key.")
        except openai.RateLimitError as e:
            raise AIRateLimitException(f"Mistral Rate Limit Error: {str(e)}")
        except openai.BadRequestError as e:
            raise AIInvalidRequestException(f"Mistral Invalid Request: {str(e)}")
        except Exception as e:
            raise AIProviderException(f"Mistral error: {str(e)}")
            
        latency = (time.time() - start_time) * 1000
        
        content = response.choices[0].message.content or None
        
        parsed_tool_calls = None
        if response.choices[0].message.tool_calls:
            from ..schemas import AIToolCall
            parsed_tool_calls = [
                AIToolCall(
                    id=tc.id,
                    type=tc.type,
                    function={"name": tc.function.name, "arguments": tc.function.arguments}
                )
                for tc in response.choices[0].message.tool_calls
            ]

        finish_reason = response.choices[0].finish_reason
        usage = response.usage
        
        info = AIResponseInfo(
            provider="mistral",
            model=model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=finish_reason,
            request_id=response.id,
            latency_ms=latency
        )
        
        return AIResponse(content=content, tool_calls=parsed_tool_calls, info=info)
