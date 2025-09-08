
class AIKPIExtractorAgent:
    """Agent based on AIKPIExtractor from ..\Rank_AI\04_kpi_extraction\ai_kpi_extractor.py"""
    
    def __init__(self):
        self.name = "AIKPIExtractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
    Stage 4: Configurable AI-powered KPI extraction system
    Capabilities:
    - Load flexible KPI configurations from JSON
    - Runtime KPI selection and prioritization
    - Multi-pattern matching with confidence scoring
    - Table and content extraction with cross-validation
    - MAR integration ready with unified data architecture
    """
        """
        Initialize KPI extractor with configuration
        Args:
            config_path: Path to kpi_config.json (default: local)
            kpi_set: KPI set to use ("standard_esg", "environmental_focused", etc.)
        """
        self.config_path = config_path or Path(__file__).parent / 'kpi_config.json'
        self.config = self._load_config()
        self.default_kpi_set = kpi_set
        self.target_kpis = self._resolve_kpi_set(kpi_set)
        print(f'✅ AI KPI Extractor initialized')
        print(f'📊 Default KPI set: {kpi_set}')
        print(f'🎯 Target KPIs loaded: {len(self.target_kpis)}')
    def _load_config(self) -> Dict:
        """Load KPI configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f'KPI config file not found: {self.config_path}')
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON in config file: {e}')
    def _resolve_kpi_set(self, kpi_set: str) -> Dict[str, Dict]:
        """Resolve KPI set with reference handling"""
        if kpi_set not in self.config['kpi_sets']:
            raise ValueError(f"KPI set '{kpi_set}' not found in configuration")
        kpi_definitions = {}
        raw_set = self.config['kpi_sets'][kpi_set]
        for kpi_key, kpi_config in raw_set.items():
            if isinstance(kpi_config, str) and kpi_config.startswith('@'):
                ref_parts = kpi_config[1:].split('.')
                ref_set, ref_key = (ref_parts[0], ref_parts[1])
                kpi_definitions[kpi_key] = self.config['kpi_sets'][ref_set][ref_key]
            else:
                kpi_definitions[kpi_key] = kpi_config
        return kpi_definitions
    def extract_kpis(self, content: str, company_name: str, reporting_year: int, target_kpis: Optional[List[str]]=None, structured_tables: Optional[List[Dict]]=None, processing_mode: str='comprehensive') -> ESGExtractionState:
        """
        Main KPI extraction method with configurable parameters
        Args:
            content: Raw document content from Stage 3
            company_name: Company name for context
            reporting_year: Reporting year for validation
            target_kpis: Specific KPIs to extract (None = use default set)
            structured_tables: Table data from Stage 3
            processing_mode: "comprehensive", "targeted", "high_confidence"
        Returns:
            ESGExtractionState with extraction results
        """
        if target_kpis:
            kpis_to_extract = {k: v for k, v in self.target_kpis.items() if k in target_kpis}
            state.agent_logs.append({'agent': 'KPISelector', 'action': 'filter_target_kpis', 'status': 'success', 'details': f'Filtering to {len(kpis_to_extract)} specific KPIs: {target_kpis}', 'timestamp': datetime.now().isoformat()})
        else:
            kpis_to_extract = self.target_kpis
        state.target_kpis = kpis_to_extract
        extraction_results = {}
        table_results = self._extract_from_tables(structured_tables, kpis_to_extract) if structured_tables else {}
        content_results = self._extract_from_content(content, kpis_to_extract)
        for kpi_key, kpi_config in kpis_to_extract.items():
            table_result = table_results.get(kpi_key)
            content_result = content_results.get(kpi_key)
            if table_result and table_result.confidence >= state.confidence_threshold:
                extraction_results[kpi_key] = table_result
            elif content_result and content_result.confidence >= state.confidence_threshold:
                extraction_results[kpi_key] = content_result
            elif processing_mode != 'high_confidence':
                best_result = max([r for r in [table_result, content_result] if r], key=lambda x: x.confidence, default=None)
                if best_result:
                    extraction_results[kpi_key] = best_result
        state.extracted_kpis = extraction_results
        found_kpis = len([r for r in extraction_results.values() if r.value is not None])
        total_kpis = len(kpis_to_extract)
        state.extraction_metadata = {'extraction_rate': f'{found_kpis}/{total_kpis} ({found_kpis / total_kpis * 100:.1f}%)', 'processing_mode': processing_mode, 'confidence_threshold': state.confidence_threshold, 'extraction_methods': ['table_analysis', 'content_pattern_matching'], 'performance_metrics': {'found_kpis': found_kpis, 'total_targets': total_kpis, 'success_rate': found_kpis / total_kpis if total_kpis > 0 else 0}}
        state.agent_logs.append({'agent': 'AIKPIExtractor', 'action': 'extract_kpis_complete', 'status': 'success', 'details': f'Extracted {found_kpis}/{total_kpis} KPIs ({found_kpis / total_kpis * 100:.1f}%)', 'timestamp': datetime.now().isoformat()})
        state.coordination_metadata['extraction_end'] = datetime.now().isoformat()
        return state
    def _extract_from_tables(self, tables: List[Dict], target_kpis: Dict[str, Dict]) -> Dict[str, KPIExtractionResult]:
        """Extract KPIs from structured table data"""
        results = {}
        if not tables:
            return results
        for table in tables:
            table_data = table.get('data', [])
            table_id = table.get('table_id', 'unknown')
            if not table_data:
                continue
            for kpi_key, kpi_config in target_kpis.items():
                if kpi_key in results:
                    continue
                patterns = kpi_config.get('patterns', [])
                units = kpi_config.get('units', [])
                for row_idx, row in enumerate(table_data):
                    for col_idx, cell in enumerate(row):
                        cell_str = str(cell).lower()
                        matched_patterns = [p for p in patterns if p.lower() in cell_str]
                        if matched_patterns:
                            value = self._extract_numeric_from_row(row, col_idx, units)
                            if value is not None:
                                results[kpi_key] = KPIExtractionResult(kpi_key=kpi_key, kpi_name=kpi_config['name'], value=value, unit=self._detect_unit(row, units), confidence=0.95, source=f'table_{table_id}', extraction_method='table_analysis', patterns_matched=matched_patterns, context_snippet=f"Row {row_idx}: {' | '.join(map(str, row))}")
                                break
        return results
    def _extract_from_content(self, content: str, target_kpis: Dict[str, Dict]) -> Dict[str, KPIExtractionResult]:
        """Extract KPIs from raw content using pure AI analysis"""
        results = {}
        if not content:
            return results
        openai_api_key = os.getenv('OPENAI_API_KEY')
        claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not openai_api_key and (not claude_api_key):
            print('❌ No LLM API keys available - Pure AI extraction requires OpenAI or Claude API')
            print('   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable')
            return results
        print(f"✅ Using pure LLM extraction (Claude: {('✓' if claude_api_key else '✗')}, OpenAI: {('✓' if openai_api_key else '✗')})")
        content_chunks = self._split_content_for_ai(content, max_chunk_size=3000)
        for kpi_key, kpi_config in target_kpis.items():
            kpi_name = kpi_config['name']
            possible_units = kpi_config.get('units', [])
            extraction_result = self._ai_extract_single_kpi(content_chunks, kpi_key, kpi_name, possible_units, openai_api_key)
            if extraction_result:
                results[kpi_key] = extraction_result
                print(f'✅ {kpi_key}: {extraction_result.value} {extraction_result.unit} (LLM confidence: {extraction_result.confidence:.0%})')
            else:
                print(f'❌ {kpi_key}: Not found by LLM analysis')
        return results
    def _extract_numeric_from_row(self, row: List, start_col: int, units: List[str]) -> Optional[float]:
        """Extract numeric value from table row"""
        for col_idx in range(start_col + 1, len(row)):
            value = self._parse_numeric_value(str(row[col_idx]))
            if value is not None:
                return value
        for col_idx in range(start_col - 1, -1, -1):
            value = self._parse_numeric_value(str(row[col_idx]))
            if value is not None:
                return value
    def _split_content_for_ai(self, content: str, max_chunk_size: int=3000) -> List[str]:
        """Split content into AI-processable chunks"""
        if len(content) <= max_chunk_size:
            return [content]
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ''
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    def _ai_extract_single_kpi(self, content_chunks: List[str], kpi_key: str, kpi_name: str, possible_units: List[str], openai_api_key: str) -> Optional[KPIExtractionResult]:
        """Use AI to extract a single KPI from content chunks with fallback"""
        for chunk_idx, chunk in enumerate(content_chunks):
            try:
                prompt = f'''\nYou are an expert ESG data analyst. Extract the specific KPI value from this ESG report content.\n\nTARGET KPI: {kpi_name}\nPOSSIBLE UNITS: {(', '.join(possible_units) if possible_units else 'Various units possible')}\n\nCONTENT TO ANALYZE:\n{chunk}\n\nYour task:\n1. Find mentions of "{kpi_name}" or closely related terms\n2. Extract the numerical value associated with this KPI\n3. Identify the unit of measurement\n4. Assess your confidence in the extraction\n\nRESPOND IN JSON FORMAT:\n{{\n  "found": true/false,\n  "value": numeric_value_only,\n  "unit": "detected_unit",\n  "confidence": 0.85,\n  "context": "sentence or phrase where you found the KPI",\n  "reasoning": "explanation of why this is the correct value"\n}}\n\nOnly respond with valid JSON. If the KPI is not found in this content, set "found": false.\n'''
                response = self._call_ai_api(prompt, openai_api_key)
                result = json.loads(response)
                if result.get('found') and result.get('value') is not None:
                    llm_confidence = result.get('confidence', 0.85)
                    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
                    if claude_api_key:
                        final_confidence = min(0.95, llm_confidence + 0.05)
                    else:
                        final_confidence = min(0.9, llm_confidence)
                    return KPIExtractionResult(kpi_key=kpi_key, kpi_name=kpi_name, value=float(result['value']), unit=result.get('unit'), confidence=final_confidence, source=f'llm_analysis_chunk_{chunk_idx}', extraction_method='pure_llm_analysis', patterns_matched=[], context_snippet=result.get('context', '')[:200])
            except Exception as e:
                if '429' in str(e) or 'Too Many Requests' in str(e):
                    print(f'❌ LLM API rate limited for {kpi_key} - Cannot extract without AI')
                else:
                    print(f'❌ LLM API failed for {kpi_key} in chunk {chunk_idx}: {e}')
                continue
    def _call_ai_api(self, prompt: str, api_key: str, use_claude: bool=True) -> str:
        """Call AI API for KPI extraction - Claude first, then OpenAI"""
        import requests
        if use_claude:
            claude_api_key = os.getenv('ANTHROPIC_API_KEY')
            if claude_api_key:
                try:
                    headers = {'x-api-key': claude_api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'}
                    data = {'model': 'claude-3-opus-20240229', 'max_tokens': 500, 'temperature': 0.1, 'messages': [{'role': 'user', 'content': prompt}]}
                    response = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=data, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    return result['content'][0]['text']
                except Exception as e:
                    print(f'⚠️ Claude API failed, falling back to OpenAI: {e}')
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert ESG data analyst specializing in precise KPI extraction from reports. Always respond with valid JSON.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 500}
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    def _detect_unit(self, row: List, possible_units: List[str]) -> Optional[str]:
        """Detect unit from table row"""
        row_text = ' '.join((str(cell) for cell in row)).lower()
        for unit in possible_units:
            if unit.lower() in row_text:
                return unit
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """Enhanced numeric value parsing without regex"""
        if not value_str:
        cleaned = str(value_str).replace(',', '').replace('$', '').replace('%', '')
        parts = cleaned.split()
        if parts:
            cleaned = parts[0].strip('()[]{}:;.,!?')
        if not cleaned:
        try:
            return float(cleaned)
        except ValueError:
    def save_results(self, state: ESGExtractionState, output_path: str):
        """Save Stage 4 KPI extraction results"""
        kpis_dict = {}
        if state.extracted_kpis:
            for kpi_key, result in state.extracted_kpis.items():
                kpis_dict[kpi_key] = asdict(result)
        results = {'timestamp': datetime.now().isoformat(), 'stage': 'stage_4_kpi_extraction', 'company': state.company_name, 'year': state.reporting_year, 'kpi_extraction_results': {'extracted_kpis': kpis_dict, 'extraction_metadata': state.extraction_metadata, 'processing_mode': state.processing_mode, 'confidence_threshold': state.confidence_threshold}, 'mar_integration': {'agent_logs': state.agent_logs, 'coordination_metadata': state.coordination_metadata, 'conversion_ready': True}, 'unified_db_integration': {'stage': 'stage_4_kpi_extraction', 'data_classification': 'esg_kpi_extractions', 'storage_ready': True, 'cross_project_tags': {'project': 'rank_ai', 'stage': 'kpi_extraction', 'company': state.company_name, 'year': state.reporting_year, 'confidence_level': 'production'}}}
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    def get_available_kpi_sets(self) -> List[str]:
        """Get list of available KPI sets"""
        return list(self.config['kpi_sets'].keys())
    def get_kpi_set_info(self, kpi_set: str) -> Dict:
        """Get information about a specific KPI set"""
        if kpi_set not in self.config['kpi_sets']:
            raise ValueError(f"KPI set '{kpi_set}' not found")
        kpis = self._resolve_kpi_set(kpi_set)
        return {'kpi_set': kpi_set, 'kpi_count': len(kpis), 'categories': list(set((kpi.get('category', 'unknown') for kpi in kpis.values()))), 'priorities': list(set((kpi.get('priority', 'medium') for kpi in kpis.values()))), 'kpis': list(kpis.keys())}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
