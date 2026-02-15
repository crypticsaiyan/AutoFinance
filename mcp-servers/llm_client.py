"""
AutoFinance LLM Client - OpenAI with Ollama Fallback

Provides a unified interface for LLM calls with automatic fallback:
1. Try OpenAI if API key is present
2. Fall back to Ollama (local) if no OpenAI key

Usage:
    from llm_client import get_llm_response
    
    response = get_llm_response(
        prompt="Analyze this stock data...",
        system_prompt="You are a financial analyst.",
        max_tokens=500
    )
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime


def get_llm_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.7,
    model_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get LLM response with automatic fallback from OpenAI to Ollama.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system/instruction prompt
        max_tokens: Maximum tokens to generate
        temperature: Temperature for response generation (0.0-1.0)
        model_preference: Specific model to use (optional)
    
    Returns:
        Dict with 'response', 'provider', 'model', 'tokens_used', 'error' (if any)
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Try OpenAI first if key exists
    if openai_key and openai_key not in ["your_openai_key_here", ""]:
        try:
            return _call_openai(prompt, system_prompt, max_tokens, temperature, model_preference)
        except Exception as e:
            # If OpenAI fails, fall back to Ollama
            print(f"⚠️  OpenAI failed ({str(e)}), falling back to Ollama...")
            return _call_ollama(prompt, system_prompt, max_tokens, temperature, model_preference)
    
    # Use Ollama as default if no OpenAI key
    return _call_ollama(prompt, system_prompt, max_tokens, temperature, model_preference)


def _call_openai(
    prompt: str,
    system_prompt: Optional[str],
    max_tokens: int,
    temperature: float,
    model: Optional[str]
) -> Dict[str, Any]:
    """Call OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model_name = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return {
        "response": response.choices[0].message.content,
        "provider": "openai",
        "model": model_name,
        "tokens_used": response.usage.total_tokens,
        "timestamp": datetime.utcnow().isoformat()
    }


def _call_ollama(
    prompt: str,
    system_prompt: Optional[str],
    max_tokens: int,
    temperature: float,
    model: Optional[str]
) -> Dict[str, Any]:
    """Call Ollama API (local)."""
    try:
        import requests
    except ImportError:
        raise ImportError("Requests package not installed. Run: pip install requests")
    
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model_name = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Combine system and user prompts for Ollama
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"
    
    try:
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "response": data.get("response", ""),
            "provider": "ollama",
            "model": model_name,
            "tokens_used": data.get("eval_count", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to Ollama. Is it running? Start with: ollama serve",
            "provider": "ollama",
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Ollama error: {str(e)}",
            "provider": "ollama",
            "model": model_name,
            "timestamp": datetime.utcnow().isoformat()
        }


def check_llm_availability() -> Dict[str, Any]:
    """
    Check which LLM providers are available.
    
    Returns:
        Dict with availability status for each provider
    """
    status = {
        "openai": {
            "available": False,
            "configured": False,
            "reason": ""
        },
        "ollama": {
            "available": False,
            "configured": True,  # Ollama doesn't need config
            "reason": ""
        }
    }
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key not in ["your_openai_key_here", ""]:
        status["openai"]["configured"] = True
        try:
            import openai
            status["openai"]["available"] = True
            status["openai"]["reason"] = "API key configured and package installed"
        except ImportError:
            status["openai"]["reason"] = "API key configured but 'openai' package not installed"
    else:
        status["openai"]["reason"] = "No API key configured"
    
    # Check Ollama
    try:
        import requests
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=2)
        if response.status_code == 200:
            status["ollama"]["available"] = True
            models = response.json().get("models", [])
            status["ollama"]["reason"] = f"Running with {len(models)} models available"
            status["ollama"]["models"] = [m["name"] for m in models]
        else:
            status["ollama"]["reason"] = "Server not responding correctly"
    except requests.exceptions.ConnectionError:
        status["ollama"]["reason"] = "Not running (start with: ollama serve)"
    except Exception as e:
        status["ollama"]["reason"] = f"Error: {str(e)}"
    
    # Determine recommended provider
    if status["openai"]["available"]:
        status["recommended"] = "openai"
    elif status["ollama"]["available"]:
        status["recommended"] = "ollama"
    else:
        status["recommended"] = None
        status["warning"] = "No LLM provider available"
    
    return status


# Simple test function
if __name__ == "__main__":
    print("🔍 Checking LLM availability...")
    print("")
    
    status = check_llm_availability()
    
    print(f"OpenAI: {'✅' if status['openai']['available'] else '❌'} {status['openai']['reason']}")
    print(f"Ollama: {'✅' if status['ollama']['available'] else '❌'} {status['ollama']['reason']}")
    print("")
    
    if status.get("recommended"):
        print(f"📌 Recommended provider: {status['recommended']}")
        
        # Test the LLM
        print("\n🧪 Testing LLM response...")
        result = get_llm_response(
            prompt="What is 2+2? Answer in one sentence.",
            system_prompt="You are a helpful assistant."
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Provider: {result['provider']}")
            print(f"   Model: {result['model']}")
            print(f"   Response: {result['response'][:100]}...")
    else:
        print("⚠️  No LLM provider available!")
        print("\nTo use OpenAI: Set OPENAI_API_KEY environment variable")
        print("To use Ollama: Install and run 'ollama serve', then 'ollama pull llama3.2'")
