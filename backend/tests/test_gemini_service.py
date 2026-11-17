import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.llm_service import LLMService

def test_gemini_configuration_and_status():
    service = LLMService(
        provider="gemini",
        gemini_api_key="mock_test_key_1234567890",
        gemini_model="gemini-1.5-flash"
    )
    assert service.is_gemini_configured() is True
    assert service.is_gemini_available_sync() is True

    status = service.get_active_provider_info()
    assert status["provider"] == "gemini"
    assert status["model"] == "gemini-1.5-flash"
    assert status["connected"] is True

def test_gemini_payload_construction():
    service = LLMService(
        provider="gemini",
        gemini_api_key="mock_test_key_1234567890",
        gemini_model="gemini-1.5-flash"
    )
    url, headers, params, payload = service._get_gemini_endpoint_and_payload(
        prompt="Explain attention mechanisms",
        system="You are an expert scientist",
        temperature=0.2
    )
    assert "gemini-1.5-flash:generateContent" in url
    assert headers["x-goog-api-key"] == "mock_test_key_1234567890"
    assert params["key"] == "mock_test_key_1234567890"
    assert payload["contents"][0]["parts"][0]["text"] == "Explain attention mechanisms"
    assert payload["systemInstruction"]["parts"][0]["text"] == "You are an expert scientist"
    assert payload["generationConfig"]["temperature"] == 0.2

def test_gemini_response_extraction():
    service = LLMService()
    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "The Transformer uses multi-head attention [Attention, Page 1]."}
                    ]
                }
            }
        ]
    }
    extracted = service._extract_gemini_text(mock_gemini_response)
    assert extracted == "The Transformer uses multi-head attention [Attention, Page 1]."

    # Error payload extraction
    error_response = {"error": {"message": "Invalid API Key"}}
    assert service._extract_gemini_text(error_response) is None

def test_gemini_sync_generation_mocked():
    service = LLMService(
        provider="gemini",
        gemini_api_key="mock_test_key_1234567890",
        gemini_model="gemini-1.5-flash"
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": "Synthesized output from Gemini API [Paper, Page 2]."}]}}
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        res = service.generate_sync("Explain BERT")
        assert "Synthesized output from Gemini API" in res

@pytest.mark.asyncio
async def test_gemini_async_generation_mocked():
    service = LLMService(
        provider="gemini",
        gemini_api_key="mock_test_key_1234567890",
        gemini_model="gemini-1.5-flash"
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": "Async synthesized output from Gemini API [Paper, Page 1]."}]}}
        ]
    }

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        res = await service.generate("Explain Transformer")
        assert "Async synthesized output from Gemini API" in res

def test_gemini_fallback_on_empty_key():
    service = LLMService(provider="gemini", gemini_api_key="")
    assert service.is_gemini_configured() is False
    prompt = "[Document: BERT, Page: 1]\nBERT is bidirectional.\n\nQuery: what is BERT"
    res = service.generate_sync(prompt)
    assert "BERT" in res
