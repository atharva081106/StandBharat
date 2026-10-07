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
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        start_time = time.time()
        
        oai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=oai_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except openai.AuthenticationError as e:
            raise AIAuthException(f"OpenAI Authentication Error: {str(e)}")
        except openai.RateLimitError as e:
            raise AIRateLimitException(f"OpenAI Rate Limit Error: {str(e)}")
        except openai.BadRequestError as e:
            raise AIInvalidRequestException(f"OpenAI Invalid Request: {str(e)}")
        except Exception as e:
            raise AIProviderException(f"OpenAI error: {str(e)}")
            
        latency = (time.time() - start_time) * 1000
        
        content = response.choices[0].message.content or ""
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
        
        return AIResponse(content=content, info=info)
