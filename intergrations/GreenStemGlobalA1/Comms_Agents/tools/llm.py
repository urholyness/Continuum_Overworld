"""
LLM tool for AI model interactions in Comms Agents.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
import json

logger = logging.getLogger(__name__)

# LLM client cache
_llm_client = None


def get_llm_client():
    """Get the configured LLM client."""
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    try:
        # Try to initialize based on environment configuration
        client = _initialize_llm_client()
        if client:
            _llm_client = client
            logger.info("LLM client initialized successfully")
            return client
        else:
            logger.warning("No LLM client configured, using fallback mode")
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        return None


def _initialize_llm_client():
    """Initialize the appropriate LLM client based on configuration."""
    # Check for OpenAI
    if os.getenv("OPENAI_API_KEY"):
        return _init_openai_client()
    
    # Check for Anthropic
    elif os.getenv("ANTHROPIC_API_KEY"):
        return _init_anthropic_client()
    
    # Check for Google Gemini
    elif os.getenv("GEMINI_API_KEY"):
        return _init_gemini_client()
    
    # Check for Groq
    elif os.getenv("GROQ_API_KEY"):
        return _init_groq_client()
    
    # Check for local models
    elif os.getenv("LOCAL_MODEL_PATH"):
        return _init_local_client()
    
    else:
        logger.info("No LLM API keys found, using fallback mode")
        return None


def _init_openai_client():
    """Initialize OpenAI client."""
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        logger.info("OpenAI client initialized")
        return client
        
    except ImportError:
        logger.warning("OpenAI package not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        return None


def _init_anthropic_client():
    """Initialize Anthropic client."""
    try:
        from anthropic import AsyncAnthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        client = AsyncAnthropic(
            api_key=api_key
        )
        
        logger.info("Anthropic client initialized")
        return client
        
    except ImportError:
        logger.warning("Anthropic package not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")
        return None


def _init_gemini_client():
    """Initialize Google Gemini client."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Create a client-like interface
        client = GeminiClient()
        logger.info("Google Gemini client initialized")
        return client
        
    except ImportError:
        logger.warning("Google Generative AI package not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None


def _init_groq_client():
    """Initialize Groq client."""
    try:
        from groq import AsyncGroq
        
        api_key = os.getenv("GROQ_API_KEY")
        
        client = AsyncGroq(
            api_key=api_key
        )
        
        logger.info("Groq client initialized")
        return client
        
    except ImportError:
        logger.warning("Groq package not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None


def _init_local_client():
    """Initialize local model client."""
    try:
        # This would integrate with local models like Ollama, LM Studio, etc.
        logger.info("Local model support not yet implemented")
        return None
        
    except Exception as e:
        logger.error(f"Failed to initialize local client: {e}")
        return None


class GeminiClient:
    """Wrapper for Google Gemini client to match other client interfaces."""
    
    def __init__(self):
        import google.generativeai as genai
        self.genai = genai
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs):
        """Chat completion with Gemini."""
        try:
            # Convert messages to Gemini format
            prompt = self._messages_to_prompt(messages)
            
            response = self.model.generate_content(prompt)
            return {
                "choices": [{
                    "message": {
                        "content": response.text
                    }
                }]
            }
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to a single prompt."""
        prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        return prompt.strip()


async def generate_text(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    **kwargs
) -> str:
    """
    Generate text using the configured LLM.
    
    Args:
        prompt: Input prompt
        model: Model to use (optional, uses default if not specified)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        **kwargs: Additional parameters
        
    Returns:
        Generated text
    """
    client = get_llm_client()
    
    if not client:
        logger.warning("No LLM client available, returning placeholder text")
        return _generate_placeholder_text(prompt)
    
    try:
        if hasattr(client, 'chat'):
            # OpenAI, Anthropic, Groq style
            messages = [{"role": "user", "content": prompt}]
            response = await client.chat.completions.create(
                model=model or _get_default_model(client),
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
            
        elif hasattr(client, 'generate_content'):
            # Gemini style
            response = await client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }
            )
            return response.text
            
        else:
            logger.warning("Unknown LLM client type, using fallback")
            return _generate_placeholder_text(prompt)
            
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        return _generate_placeholder_text(prompt)


def _get_default_model(client) -> str:
    """Get default model for the client type."""
    if hasattr(client, 'models'):
        # OpenAI style
        return "gpt-3.5-turbo"
    elif hasattr(client, 'messages'):
        # Anthropic style
        return "claude-3-sonnet-20240229"
    elif hasattr(client, 'generate_content'):
        # Gemini style
        return "gemini-pro"
    else:
        return "unknown"


def _generate_placeholder_text(prompt: str) -> str:
    """Generate placeholder text when LLM is not available."""
    # Simple template-based generation
    if "linkedin" in prompt.lower():
        return "This is a placeholder LinkedIn post. Please configure an LLM client for AI-generated content."
    elif "twitter" in prompt.lower() or "x" in prompt.lower():
        return "This is a placeholder X post. Please configure an LLM client for AI-generated content."
    elif "email" in prompt.lower():
        return "This is a placeholder email. Please configure an LLM client for AI-generated content."
    else:
        return "This is placeholder content. Please configure an LLM client for AI-generated content."


async def generate_structured_output(
    prompt: str,
    output_schema: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Generate structured output using the configured LLM.
    
    Args:
        prompt: Input prompt
        output_schema: Expected output schema
        **kwargs: Additional parameters
        
    Returns:
        Structured output matching the schema
    """
    try:
        # Add schema instructions to prompt
        schema_prompt = f"""
{prompt}

Please provide your response in the following JSON format:
{json.dumps(output_schema, indent=2)}

Ensure the response is valid JSON and matches the schema exactly.
"""
        
        # Generate text
        response_text = await generate_text(schema_prompt, **kwargs)
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            else:
                logger.warning("No JSON found in LLM response")
                return _create_fallback_output(output_schema)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from LLM response: {e}")
            return _create_fallback_output(output_schema)
            
    except Exception as e:
        logger.error(f"Structured output generation failed: {e}")
        return _create_fallback_output(output_schema)


def _create_fallback_output(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Create fallback output when structured generation fails."""
    fallback = {}
    
    for key, value in schema.items():
        if isinstance(value, dict) and "type" in value:
            if value["type"] == "string":
                fallback[key] = f"Fallback {key}"
            elif value["type"] == "array":
                fallback[key] = [f"Fallback {key} item"]
            elif value["type"] == "object":
                fallback[key] = {}
            else:
                fallback[key] = None
        else:
            fallback[key] = value
    
    return fallback


async def embed_text(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embeddings for text.
    
    Args:
        text: Text to embed
        model: Embedding model to use
        
    Returns:
        Embedding vector
    """
    client = get_llm_client()
    
    if not client:
        logger.warning("No LLM client available for embeddings")
        return [0.0] * 1536  # Default embedding size
    
    try:
        if hasattr(client, 'embeddings'):
            # OpenAI style
            response = await client.embeddings.create(
                model=model or "text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        elif hasattr(client, 'messages'):
            # Anthropic style
            response = await client.messages.create(
                model=model or "claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": text}]
            )
            # This is a placeholder - Anthropic doesn't have embeddings in the same way
            return [0.0] * 1536
            
        else:
            logger.warning("Embeddings not supported by this client")
            return [0.0] * 1536
            
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return [0.0] * 1536


def get_available_models() -> List[str]:
    """Get list of available models."""
    client = get_llm_client()
    
    if not client:
        return []
    
    try:
        if hasattr(client, 'models'):
            # OpenAI style
            models = client.models.list()
            return [model.id for model in models.data]
        else:
            return ["default"]
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        return []


if __name__ == "__main__":
    # Test the LLM tool
    import asyncio
    
    async def test():
        print("Testing LLM tool...")
        
        # Test text generation
        prompt = "Write a short LinkedIn post about AI in business"
        response = await generate_text(prompt)
        print(f"Generated text: {response}")
        
        # Test structured output
        schema = {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {"type": "array"}
        }
        
        structured = await generate_structured_output(prompt, schema)
        print(f"Structured output: {json.dumps(structured, indent=2)}")
        
        # Test embeddings
        embedding = await embed_text("test text")
        print(f"Embedding length: {len(embedding)}")
        
        # Show available models
        models = get_available_models()
        print(f"Available models: {models}")
    
    asyncio.run(test())

