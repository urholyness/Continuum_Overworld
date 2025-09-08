"""
LLM Service - MAR Shared Component
Handles LLM API calls with fallback support
"""

import os
import json
from typing import Dict, List, Optional, Any


def query_llm(prompt: str, model: str = "gpt-4o", **kwargs) -> Dict[str, Any]:
    """
    Query LLM with fallback support
    
    Args:
        prompt: The prompt to send
        model: Preferred model (gpt-4o, claude-3, etc.)
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with 'output' key containing response
    """
    
    # Check if we have API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not openai_key and not anthropic_key:
        # Return mock response for demo purposes
        return {
            "output": json.dumps({
                "functionality_type": "processor",
                "input_signature": ["str", "dict"],
                "output_signature": ["dict"],
                "dependencies": ["json", "pathlib"],
                "complexity_score": 0.6,
                "reusability_score": 0.8,
                "llm_compatible": True,
                "agent_potential": "high",
                "doc": "This is a mock analysis for demonstration purposes.",
                "related_patterns": ["data_processor", "file_handler"]
            }),
            "model_used": "mock",
            "tokens_used": 0
        }
    
    try:
        if model.startswith("gpt") and openai_key:
            return _query_openai(prompt, model, **kwargs)
        elif model.startswith("claude") and anthropic_key:
            return _query_anthropic(prompt, model, **kwargs)
        else:
            # Fallback to available service
            if openai_key:
                return _query_openai(prompt, "gpt-4o", **kwargs)
            elif anthropic_key:
                return _query_anthropic(prompt, "claude-3-sonnet-20240229", **kwargs)
                
    except Exception as e:
        print(f"⚠️ LLM query failed: {e}")
        return {
            "output": "LLM query failed - using fallback response",
            "error": str(e),
            "model_used": "error_fallback"
        }


def _query_openai(prompt: str, model: str, **kwargs) -> Dict[str, Any]:
    """Query OpenAI API"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get('max_tokens', 2000),
            temperature=kwargs.get('temperature', 0.1)
        )
        
        return {
            "output": response.choices[0].message.content,
            "model_used": model,
            "tokens_used": response.usage.total_tokens
        }
        
    except ImportError:
        print("⚠️ OpenAI package not installed. Install with: pip install openai")
        return {"output": "OpenAI package not available", "error": "missing_package"}
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")


def _query_anthropic(prompt: str, model: str, **kwargs) -> Dict[str, Any]:
    """Query Anthropic API"""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        response = client.messages.create(
            model=model,
            max_tokens=kwargs.get('max_tokens', 2000),
            temperature=kwargs.get('temperature', 0.1),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "output": response.content[0].text,
            "model_used": model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
        
    except ImportError:
        print("⚠️ Anthropic package not installed. Install with: pip install anthropic")
        return {"output": "Anthropic package not available", "error": "missing_package"}
    except Exception as e:
        raise Exception(f"Anthropic API error: {e}")


