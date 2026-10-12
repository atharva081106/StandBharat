import pytest
from unittest.mock import patch, MagicMock
from app.ai.providers.openai import OpenAIProvider
from app.ai.exceptions import AINotConfiguredException, AIAuthException, AIInvalidRequestException
import openai

def test_missing_or_invalid_placeholder_key():
    with patch('app.ai.providers.openai.ai_config.OPENAI_API_KEY', ''):
        with pytest.raises(AINotConfiguredException):
            OpenAIProvider()
            
    with patch('app.ai.providers.openai.ai_config.OPENAI_API_KEY', 'your_api_key_here'):
        with pytest.raises(AINotConfiguredException):
            OpenAIProvider()
            
    with patch('app.ai.providers.openai.ai_config.OPENAI_API_KEY', 'sk-dummy-key'):
        with pytest.raises(AINotConfiguredException):
            OpenAIProvider()

def test_auth_exception_scrubs_secret():
    with patch('app.ai.providers.openai.ai_config.OPENAI_API_KEY', 'valid-looking-key'):
        provider = OpenAIProvider()
        
        # Mock client chat completions to throw AuthenticationError with a secret inside
        mock_create = MagicMock(side_effect=openai.AuthenticationError(
            message="Incorrect API key provided: valid-looking-key",
            response=MagicMock(),
            body={}
        ))
        provider.client.chat.completions.create = mock_create
        
        with pytest.raises(AIAuthException) as excinfo:
            from app.ai.schemas import AIRequestMessage
            provider.generate(messages=[AIRequestMessage(role="user", content="Hi")], model="gpt-4o")
            
        assert "valid-looking-key" not in str(excinfo.value)
        assert "Invalid or missing API key" in str(excinfo.value)

def test_mistral_missing_or_invalid_placeholder_key():
    from app.ai.providers.mistral import MistralProvider
    with patch('app.ai.providers.mistral.ai_config.MISTRAL_API_KEY', ''):
        with pytest.raises(AINotConfiguredException):
            MistralProvider()
            
    with patch('app.ai.providers.mistral.ai_config.MISTRAL_API_KEY', 'your_api_key_here'):
        with pytest.raises(AINotConfiguredException):
            MistralProvider()
            
    with patch('app.ai.providers.mistral.ai_config.MISTRAL_API_KEY', 'mstrl_dummy_key'):
        with pytest.raises(AINotConfiguredException):
            MistralProvider()

def test_mistral_auth_exception_scrubs_secret():
    from app.ai.providers.mistral import MistralProvider
    with patch('app.ai.providers.mistral.ai_config.MISTRAL_API_KEY', 'valid-mistral-key'):
        provider = MistralProvider()
        
        mock_create = MagicMock(side_effect=openai.AuthenticationError(
            message="Incorrect API key provided: valid-mistral-key",
            response=MagicMock(),
            body={}
        ))
        provider.client.chat.completions.create = mock_create
        
        with pytest.raises(AIAuthException) as excinfo:
            from app.ai.schemas import AIRequestMessage
            provider.generate(messages=[AIRequestMessage(role="user", content="Hi")], model="ministral-8b-latest")
            
        assert "valid-mistral-key" not in str(excinfo.value)
        assert "Invalid or missing API key" in str(excinfo.value)
