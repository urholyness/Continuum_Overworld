
class OpenAIProviderAgent:
    """Agent based on OpenAIProvider from ..\Nyxion\backend\integrations\llm_providers.py"""
    
    def __init__(self):
        self.name = "OpenAIProviderAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """OpenAI API provider"""
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = 'https://api.openai.com/v1'
        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'} if self.api_key else {}
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        if not self.api_key:
            raise LLMAPIError('OpenAI', 'API key not configured')
        url = f'{self.base_url}/{endpoint}'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=data, timeout=60.0)
                if response.status_code >= 400:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                    raise LLMAPIError('OpenAI', error_msg)
                return response.json()
        except httpx.RequestError as e:
            raise LLMAPIError('OpenAI', f'Request failed: {str(e)}')
    async def analyze_text_coherence(self, text: str, context: Optional[str]=None) -> Dict[str, Any]:
        """Analyze text coherence using GPT-4"""
        try:
            prompt = f'''Analyze the following text for coherence, quality, and potential fraud indicators:\n\nText to analyze: "{text}"\n{(f'Context: {context}' if context else '')}\n\nPlease provide a JSON response with:\n1. coherence_score (0.0-1.0): How coherent and well-structured the text is\n2. sentiment_score (-1.0 to 1.0): Overall sentiment\n3. is_gibberish (boolean): Whether the text appears to be meaningless\n4. is_spam (boolean): Whether the text appears to be spam\n5. is_copy_paste (boolean): Whether the text appears to be copied from elsewhere\n6. key_themes (array): Main themes or topics mentioned\n7. analysis_summary (string): Brief summary of the analysis\n\nRespond only with valid JSON.'''
            data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert text analyst specializing in survey response quality assessment.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 1000}
            response = await self._make_request('chat/completions', data)
            content = response['choices'][0]['message']['content']
            analysis = json.loads(content)
            return analysis
        except Exception as e:
            logger.error(f'OpenAI text analysis error: {str(e)}')
            raise LLMAPIError('OpenAI', f'Text analysis failed: {str(e)}')
    async def extract_sentiment(self, text: str) -> Dict[str, Any]:
        """Extract sentiment using GPT-4"""
        try:
            prompt = f'Analyze the sentiment of the following text:\n\n"{text}"\n\nProvide a JSON response with:\n1. sentiment_score (-1.0 to 1.0): Negative to positive sentiment\n2. sentiment_label (string): "positive", "negative", or "neutral"\n3. confidence (0.0-1.0): Confidence in the sentiment analysis\n4. emotions (array): List of emotions detected\n\nRespond only with valid JSON.'
            data = {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'system', 'content': 'You are a sentiment analysis expert.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 500}
            response = await self._make_request('chat/completions', data)
            content = response['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
            logger.error(f'OpenAI sentiment analysis error: {str(e)}')
            raise LLMAPIError('OpenAI', f'Sentiment analysis failed: {str(e)}')
    async def summarize_brand_mentions(self, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize brand mentions for reputation analysis"""
        try:
            mentions_text = '\n'.join([f"- {mention.get('title', '')}: {mention.get('snippet', '')}" for mention in mentions[:10]])
            prompt = f'Analyze the following brand mentions and provide a comprehensive summary:\n\n{mentions_text}\n\nProvide a JSON response with:\n1. overall_sentiment (-1.0 to 1.0): Overall sentiment across all mentions\n2. risk_level (string): "low", "medium", "high", or "critical"\n3. key_findings (array): Main findings about the brand\n4. positive_aspects (array): Positive mentions\n5. negative_aspects (array): Concerns or negative mentions\n6. recommendations (array): Recommended actions\n7. summary (string): Executive summary\n\nRespond only with valid JSON.'
            data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are a brand reputation analyst.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.2, 'max_tokens': 1500}
            response = await self._make_request('chat/completions', data)
            content = response['choices'][0]['message']['content']
            return json.loads(content)
        except Exception as e:
            logger.error(f'OpenAI brand analysis error: {str(e)}')
            raise LLMAPIError('OpenAI', f'Brand analysis failed: {str(e)}')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
