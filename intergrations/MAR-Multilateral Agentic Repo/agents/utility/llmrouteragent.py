
class LLMRouterAgent:
    """Agent based on LLMRouter from ..\Nyxion\backend\integrations\llm_providers.py"""
    
    def __init__(self):
        self.name = "LLMRouterAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Route LLM requests to appropriate providers"""
        self.providers = {}
        if settings.OPENAI_API_KEY:
            self.providers['openai'] = OpenAIProvider()
        if settings.ANTHROPIC_API_KEY:
            self.providers['anthropic'] = AnthropicProvider()
    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """Get specific provider"""
        if provider_name not in self.providers:
            raise LLMAPIError(provider_name, 'Provider not available or not configured')
        return self.providers[provider_name]
    async def analyze_text_coherence(self, text: str, provider: Optional[str]=None, context: Optional[str]=None) -> Dict[str, Any]:
        """Analyze text coherence with optional provider selection"""
        if not provider:
            provider = 'openai' if 'openai' in self.providers else list(self.providers.keys())[0]
        llm_provider = self.get_provider(provider)
        return await llm_provider.analyze_text_coherence(text, context)
    async def extract_sentiment(self, text: str, provider: Optional[str]=None) -> Dict[str, Any]:
        """Extract sentiment with optional provider selection"""
        if not provider:
            provider = 'openai' if 'openai' in self.providers else list(self.providers.keys())[0]
        llm_provider = self.get_provider(provider)
        return await llm_provider.extract_sentiment(text)
    async def summarize_brand_mentions(self, mentions: List[Dict[str, Any]], provider: Optional[str]=None) -> Dict[str, Any]:
        """Summarize brand mentions with optional provider selection"""
        if not provider:
            provider = 'openai' if 'openai' in self.providers else list(self.providers.keys())[0]
        llm_provider = self.get_provider(provider)
        return await llm_provider.summarize_brand_mentions(mentions)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
