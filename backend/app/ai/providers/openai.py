from typing import List, Dict, Any, Optional
import time
from .base import BaseAIProvider
from ..schemas import AIRequestMessage, AIResponse, AIResponseInfo
from ..exceptions import AINotConfiguredException, AIProviderException, AIAuthException, AIRateLimitException, AIInvalidRequestException
from ..config import ai_config
import openai

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        if not ai_config.OPENAI_API_KEY:
            raise AINotConfiguredException("OpenAI API key is not configured")
        import openai
        self.client = openai.OpenAI(api_key=ai_config.OPENAI_API_KEY)

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
        
        oai_messages = []
        for msg in messages:
            oai_msg = {"role": msg.role}
            if msg.content is not None:
                oai_msg["content"] = msg.content
            if msg.tool_calls:
                oai_msg["tool_calls"] = [
                    {"id": tc.id, "type": tc.type, "function": tc.function}
                    for tc in msg.tool_calls
                ]
            if msg.tool_call_id:
                oai_msg["tool_call_id"] = msg.tool_call_id
            oai_messages.append(oai_msg)
        
        try:
            kwargs = {
                "model": model,
                "messages": oai_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if tools:
                kwargs["tools"] = tools

            response = self.client.chat.completions.create(**kwargs)
        except openai.AuthenticationError as e:
            raise AIAuthException(f"OpenAI Authentication Error: {str(e)}")
        except openai.RateLimitError as e:
            raise AIRateLimitException(f"OpenAI Rate Limit Error: {str(e)}")
        except openai.BadRequestError as e:
            raise AIInvalidRequestException(f"OpenAI Invalid Request: {str(e)}")
        except Exception as e:
            raise AIProviderException(f"OpenAI error: {str(e)}")
            
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
            provider="openai",
            model=model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            finish_reason=finish_reason,
            request_id=response.id,
            latency_ms=latency
        )
        
        return AIResponse(content=content, tool_calls=parsed_tool_calls, info=info)
