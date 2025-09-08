
class AIModelManagerAgent:
    """Agent based on AIModelManager from ..\Rank_AI\ai_model_manager.py"""
    
    def __init__(self):
        self.name = "AIModelManagerAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Manages multiple AI models with intelligent fallback and routing
    """
        """Initialize with configuration"""
        self.models = self._initialize_models()
        self.task_routing = self._initialize_task_routing()
        self.retry_config = {'max_retries': 3, 'base_delay': 1.0, 'max_delay': 60.0, 'exponential_base': 2}
        self.usage_stats = {'total_requests': 0, 'total_cost': 0.0, 'model_usage': {}, 'failures': {}}
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    def _initialize_models(self) -> Dict[str, ModelConfig]:
        """Initialize available AI models"""
        models = {}
        if os.getenv('OPENAI_API_KEY'):
            models['openai_gpt4'] = ModelConfig(provider='openai', model_name='gpt-4', api_key=os.getenv('OPENAI_API_KEY'), endpoint='https://api.openai.com/v1/chat/completions', max_tokens=4000, temperature=0.1, cost_per_1k_tokens=0.03, capabilities=['search', 'extraction', 'validation', 'reasoning'])
            models['openai_gpt35'] = ModelConfig(provider='openai', model_name='gpt-3.5-turbo', api_key=os.getenv('OPENAI_API_KEY'), endpoint='https://api.openai.com/v1/chat/completions', max_tokens=4000, temperature=0.1, cost_per_1k_tokens=0.001, capabilities=['search', 'extraction', 'reasoning'])
        if os.getenv('GEMINI_API_KEY'):
            models['gemini_pro'] = ModelConfig(provider='gemini', model_name='gemini-pro', api_key=os.getenv('GEMINI_API_KEY'), endpoint='https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent', max_tokens=8000, temperature=0.1, cost_per_1k_tokens=0.001, capabilities=['search', 'extraction', 'validation', 'reasoning'])
        if os.getenv('ANTHROPIC_API_KEY'):
            models['claude_3'] = ModelConfig(provider='anthropic', model_name='claude-3-opus-20240229', api_key=os.getenv('ANTHROPIC_API_KEY'), endpoint='https://api.anthropic.com/v1/messages', max_tokens=4000, temperature=0.1, cost_per_1k_tokens=0.015, capabilities=['extraction', 'validation', 'reasoning', 'analysis'])
        models['regex_fallback'] = ModelConfig(provider='local', model_name='regex_patterns', api_key=None, endpoint=None, max_tokens=0, temperature=0, cost_per_1k_tokens=0, capabilities=['extraction'])
        models['statistical_fallback'] = ModelConfig(provider='local', model_name='statistical_analysis', api_key=None, endpoint=None, max_tokens=0, temperature=0, cost_per_1k_tokens=0, capabilities=['validation'])
        return models
    def _initialize_task_routing(self) -> Dict[str, List[str]]:
        """Define preferred models for each task type"""
        return {'search': ['openai_gpt4', 'gemini_pro', 'openai_gpt35'], 'extraction': ['openai_gpt4', 'gemini_pro', 'claude_3', 'regex_fallback'], 'validation': ['openai_gpt4', 'claude_3', 'gemini_pro', 'statistical_fallback'], 'reasoning': ['openai_gpt4', 'claude_3', 'gemini_pro', 'openai_gpt35'], 'default': ['openai_gpt4', 'gemini_pro', 'openai_gpt35', 'regex_fallback']}
    def get_model_for_task(self, task_type: str, exclude_models: List[str]=None) -> Optional[str]:
        """Get the best available model for a task type"""
        exclude_models = exclude_models or []
        preferred_models = self.task_routing.get(task_type, self.task_routing['default'])
        for model_id in preferred_models:
            if model_id not in exclude_models and model_id in self.models:
                if not self._is_rate_limited(model_id):
                    return model_id
    def _is_rate_limited(self, model_id: str) -> bool:
        """Check if a model is currently rate limited"""
        failures = self.usage_stats['failures'].get(model_id, {})
        last_failure = failures.get('last_429', 0)
        if time.time() - last_failure < 3600:
            return True
        return False
    async def call_model_async(self, prompt: str, task_type: str='default', system_prompt: str=None, **kwargs) -> ModelResponse:
        """Call AI model with automatic fallback (async version)"""
        return self.call_model(prompt, task_type, system_prompt, **kwargs)
    def call_model(self, prompt: str, task_type: str='default', system_prompt: str=None, **kwargs) -> ModelResponse:
        """Call AI model with automatic fallback"""
        exclude_models = []
        attempts = 0
        while attempts < self.retry_config['max_retries']:
            model_id = self.get_model_for_task(task_type, exclude_models)
            if not model_id:
                return ModelResponse(content='', provider='none', model='none', success=False, error='No available models for task')
            model_config = self.models[model_id]
            try:
                start_time = time.time()
                if model_config.provider == 'openai':
                    response = self._call_openai(prompt, model_config, system_prompt, **kwargs)
                elif model_config.provider == 'gemini':
                    response = self._call_gemini(prompt, model_config, system_prompt, **kwargs)
                elif model_config.provider == 'anthropic':
                    response = self._call_anthropic(prompt, model_config, system_prompt, **kwargs)
                elif model_config.provider == 'local':
                    response = self._call_local_fallback(prompt, model_config, task_type, **kwargs)
                else:
                    raise ValueError(f'Unknown provider: {model_config.provider}')
                response.latency = time.time() - start_time
                self._track_usage(model_id, response)
                return response
            except Exception as e:
                error_str = str(e)
                logger.warning(f'Model {model_id} failed: {error_str}')
                self._track_failure(model_id, error_str)
                if '429' in error_str or 'rate limit' in error_str.lower():
                    self.usage_stats['failures'].setdefault(model_id, {})['last_429'] = time.time()
                exclude_models.append(model_id)
                if attempts < self.retry_config['max_retries'] - 1:
                    delay = min(self.retry_config['base_delay'] * self.retry_config['exponential_base'] ** attempts, self.retry_config['max_delay'])
                    logger.info(f'Retrying in {delay:.1f} seconds...')
                    time.sleep(delay)
                attempts += 1
        return ModelResponse(content='', provider='none', model='none', success=False, error=f'All models failed after {attempts} attempts')
    def _call_openai(self, prompt: str, config: ModelConfig, system_prompt: str=None, **kwargs) -> ModelResponse:
        """Call OpenAI API"""
        headers = {'Authorization': f'Bearer {config.api_key}', 'Content-Type': 'application/json'}
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})
        data = {'model': config.model_name, 'messages': messages, 'temperature': kwargs.get('temperature', config.temperature), 'max_tokens': kwargs.get('max_tokens', config.max_tokens)}
        response = requests.post(config.endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        tokens = result.get('usage', {}).get('total_tokens', 0)
        return ModelResponse(content=content, provider=config.provider, model=config.model_name, success=True, tokens_used=tokens, cost=tokens / 1000 * config.cost_per_1k_tokens if tokens else None)
    def _call_gemini(self, prompt: str, config: ModelConfig, system_prompt: str=None, **kwargs) -> ModelResponse:
        """Call Google Gemini API"""
        url = f'{config.endpoint}?key={config.api_key}'
        full_prompt = prompt
        if system_prompt:
            full_prompt = f'{system_prompt}\n\n{prompt}'
        data = {'contents': [{'parts': [{'text': full_prompt}]}], 'generationConfig': {'temperature': kwargs.get('temperature', config.temperature), 'maxOutputTokens': kwargs.get('max_tokens', config.max_tokens)}}
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        return ModelResponse(content=content, provider=config.provider, model=config.model_name, success=True)
    def _call_anthropic(self, prompt: str, config: ModelConfig, system_prompt: str=None, **kwargs) -> ModelResponse:
        """Call Anthropic Claude API"""
        headers = {'x-api-key': config.api_key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}
        data = {'model': config.model_name, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': kwargs.get('max_tokens', config.max_tokens), 'temperature': kwargs.get('temperature', config.temperature)}
        if system_prompt:
            data['system'] = system_prompt
        response = requests.post(config.endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result['content'][0]['text']
        return ModelResponse(content=content, provider=config.provider, model=config.model_name, success=True)
    def _call_local_fallback(self, prompt: str, config: ModelConfig, task_type: str, **kwargs) -> ModelResponse:
        """Call local fallback methods (regex, statistical analysis)"""
        if config.model_name == 'regex_patterns':
            content = self._regex_extraction(prompt, **kwargs)
        elif config.model_name == 'statistical_analysis':
            content = self._statistical_validation(prompt, **kwargs)
        else:
            content = 'Local fallback not implemented'
        return ModelResponse(content=content, provider=config.provider, model=config.model_name, success=True, cost=0.0)
    def _regex_extraction(self, content: str, **kwargs) -> str:
        """Regex-based KPI extraction fallback"""
        import re
        kpis = {}
        patterns = {'scope_1_emissions': 'scope\\s*1\\s*emissions?[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'scope_2_emissions': 'scope\\s*2\\s*emissions?[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'total_energy': 'total\\s*energy\\s*consumption[:\\s]*([0-9,]+\\.?[0-9]*)\\s*gwh', 'renewable_energy': 'renewable\\s*energy[:\\s]*([0-9,]+\\.?[0-9]*)\\s*%', 'employees': 'total\\s*employees?[:\\s]*([0-9,]+)', 'water_consumption': 'water\\s*consumption[:\\s]*([0-9,]+\\.?[0-9]*)\\s*(million\\s*)?liters'}
        content_lower = content.lower()
        for kpi_name, pattern in patterns.items():
            match = re.search(pattern, content_lower, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                try:
                    kpis[kpi_name] = float(value)
                except ValueError:
        return json.dumps(kpis)
    def _statistical_validation(self, data: str, **kwargs) -> str:
        """Statistical validation fallback"""
        try:
            kpis = json.loads(data)
        except:
            kpis = {}
        validation_results = {}
        for kpi_name, value in kpis.items():
            is_valid = True
            confidence = 0.7
            if isinstance(value, (int, float)):
                if 'emissions' in kpi_name and value < 0:
                    is_valid = False
                elif 'percentage' in kpi_name and (value < 0 or value > 100):
                    is_valid = False
                elif value < 0:
                    confidence = 0.3
            validation_results[kpi_name] = {'valid': is_valid, 'confidence': confidence}
        return json.dumps(validation_results)
    def _track_usage(self, model_id: str, response: ModelResponse):
        """Track model usage for analytics"""
        self.usage_stats['total_requests'] += 1
        if response.cost:
            self.usage_stats['total_cost'] += response.cost
        if model_id not in self.usage_stats['model_usage']:
            self.usage_stats['model_usage'][model_id] = {'requests': 0, 'successes': 0, 'total_cost': 0.0, 'avg_latency': 0.0}
        stats = self.usage_stats['model_usage'][model_id]
        stats['requests'] += 1
        if response.success:
            stats['successes'] += 1
        if response.cost:
            stats['total_cost'] += response.cost
        if response.latency:
            prev_avg = stats['avg_latency']
            stats['avg_latency'] = (prev_avg * (stats['requests'] - 1) + response.latency) / stats['requests']
    def _track_failure(self, model_id: str, error: str):
        """Track model failures"""
        if model_id not in self.usage_stats['failures']:
            self.usage_stats['failures'][model_id] = {'total': 0, 'errors': {}}
        self.usage_stats['failures'][model_id]['total'] += 1
        error_type = 'unknown'
        if '429' in error:
            error_type = 'rate_limit'
        elif '401' in error:
            error_type = 'auth'
        elif 'timeout' in error.lower():
            error_type = 'timeout'
        if error_type not in self.usage_stats['failures'][model_id]['errors']:
            self.usage_stats['failures'][model_id]['errors'][error_type] = 0
        self.usage_stats['failures'][model_id]['errors'][error_type] += 1
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics report"""
        return {'summary': {'total_requests': self.usage_stats['total_requests'], 'total_cost': f"${self.usage_stats['total_cost']:.2f}", 'active_models': len([m for m in self.models if m in self.usage_stats['model_usage']])}, 'model_performance': {model_id: {'requests': stats['requests'], 'success_rate': f"{stats['successes'] / stats['requests'] * 100:.1f}%" if stats['requests'] > 0 else '0%', 'total_cost': f"${stats['total_cost']:.2f}", 'avg_latency': f"{stats['avg_latency']:.2f}s"} for model_id, stats in self.usage_stats['model_usage'].items()}, 'failures': self.usage_stats['failures']}
    def _load_config(self, config_path: str):
        """Load configuration from file"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        if 'retry_config' in config:
            self.retry_config.update(config['retry_config'])
        if 'task_routing' in config:
            self.task_routing.update(config['task_routing'])
        if 'custom_models' in config:
            for model_id, model_config in config['custom_models'].items():
                self.models[model_id] = ModelConfig(**model_config)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
