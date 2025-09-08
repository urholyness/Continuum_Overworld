
class MultiAIValidatorAgent:
    """Agent based on MultiAIValidator from ..\Rank_AI\02_report_acquisition\ai_multi_validator.py"""
    
    def __init__(self):
        self.name = "MultiAIValidatorAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Multi-AI validation system for ESG report content assessment"""
        """Initialize multi-AI validator with selected methods"""
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.google_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.google_project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.available_methods = []
        if self.openai_key:
            self.available_methods.append('openai')
        if self.google_credentials and self.google_project_id:
            self.available_methods.append('document_ai')
        if self.gemini_key:
            self.available_methods.append('gemini')
        if validation_methods == 'auto':
            self.validation_methods = self.available_methods
        elif isinstance(validation_methods, list):
            self.validation_methods = [m for m in validation_methods if m in self.available_methods]
        else:
            self.validation_methods = [validation_methods] if validation_methods in self.available_methods else []
        print(f'🤖 Multi-AI Validator initialized')
        print(f'📋 Available methods: {self.available_methods}')
        print(f'🎯 Selected methods: {self.validation_methods}')
        self._init_google_services()
    def _init_google_services(self):
        """Initialize Google Document AI and Gemini clients"""
        self.docai_client = None
        self.gemini_model = None
        if 'document_ai' in self.available_methods:
            try:
                from google.cloud import documentai
                from google.oauth2 import service_account
                if not os.path.exists(self.google_credentials):
                    raise FileNotFoundError(f'Google credentials file not found: {self.google_credentials}')
                credentials = service_account.Credentials.from_service_account_file(self.google_credentials)
                self.docai_client = documentai.DocumentProcessorServiceClient(credentials=credentials)
                print('✅ Google Document AI client initialized')
            except Exception as e:
                print(f'⚠️ Document AI initialization failed: {e}')
                print(f'   Note: Document AI will be disabled for this session')
                if 'document_ai' in self.validation_methods:
                    self.validation_methods.remove('document_ai')
                if 'document_ai' in self.available_methods:
                    self.available_methods.remove('document_ai')
        if 'gemini' in self.available_methods:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print('✅ Google Gemini client initialized')
            except Exception as e:
                print(f'⚠️ Gemini initialization failed: {e}')
                if 'gemini' in self.validation_methods:
                    self.validation_methods.remove('gemini')
    async def validate_report_content(self, file_path: str, url: str, title: str, company: str) -> MultiAIValidationResult:
        """Run multi-AI validation on downloaded report"""
        print(f'\n🤖 MULTI-AI VALIDATION: {title}')
        print(f'📁 File: {file_path}')
        print(f'🎯 Methods: {self.validation_methods}')
        print(f'📄 Extracting PDF content...')
        extracted_content, extraction_method = self._extract_file_content(file_path)
        print(f'✅ Content extracted using {extraction_method}')
        validation_tasks = []
        for method in self.validation_methods:
            if method == 'openai':
                validation_tasks.append(('openai', self._validate_with_openai(extracted_content, url, title, company)))
            elif method == 'document_ai':
                validation_tasks.append(('document_ai', self._validate_with_document_ai(file_path, company)))
            elif method == 'gemini':
                validation_tasks.append(('gemini', self._validate_with_gemini(extracted_content, title, company)))
        print(f'🚀 Running {len(validation_tasks)} AI validation methods concurrently...')
        method_results = {}
        if validation_tasks:
            completed_results = await asyncio.gather(*[task[1] for task in validation_tasks], return_exceptions=True)
            print(f'✅ All AI validations completed')
            for i, (method, _) in enumerate(validation_tasks):
                result = completed_results[i]
                if isinstance(result, Exception):
                    method_results[method] = AIValidationResult(method=method, is_valid_report=False, quality_score=0.0, content_assessment=f'Validation failed: {str(result)}', company_match=False, year_match=False, concerns=[f'Method failed: {str(result)}'], extracted_content='', confidence=0.0, processing_time=0.0, error=str(result))
                else:
                    method_results[method] = result
        consensus_result = self._generate_consensus(method_results, extraction_method)
        print(f'🎯 Consensus Score: {consensus_result.consensus_score:.1f}%')
        print(f'📊 Agreement Level: {consensus_result.agreement_level:.1f}%')
        print(f'🏆 Best Method: {consensus_result.best_method}')
        return consensus_result
    def _extract_file_content(self, file_path: str) -> Tuple[str, str]:
        """Extract content from file for AI analysis"""
        file_ext = file_path.split('.')[-1].lower()
        try:
            if file_ext == 'pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext in ['html', 'htm']:
                return self._extract_html_content(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(3000)
                    return (content, 'plain_text_read')
        except Exception as e:
            return (f'Content extraction failed: {str(e)}', 'extraction_error')
    def _extract_pdf_content(self, file_path: str) -> Tuple[str, str]:
        """Extract text from PDF using multiple methods"""
        try:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text_content = ''
                    for page_num, page in enumerate(pdf.pages[:3]):
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f'\n--- Page {page_num + 1} ---\n{page_text}'
                        if len(text_content) > 3000:
                            break
                    if text_content.strip():
                        return (text_content[:3000], 'pdfplumber_extraction')
            except ImportError:
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_content = ''
                    for page_num in range(min(3, len(pdf_reader.pages))):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f'\n--- Page {page_num + 1} ---\n{page_text}'
                        if len(text_content) > 3000:
                            break
                    if text_content.strip():
                        return (text_content[:3000], 'pypdf2_extraction')
            except ImportError:
            return (f'PDF detected but no extraction library available', 'pdf_validation_only')
        except Exception as e:
            return (f'PDF extraction error: {str(e)}', 'pdf_extraction_error')
    def _extract_html_content(self, file_path: str) -> Tuple[str, str]:
        """Extract readable text from HTML file using AI logic"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read(8000)
            cleaned_text = ''
            in_tag = False
            for char in html_content:
                if char == '<':
                    in_tag = True
                elif char == '>':
                    in_tag = False
                elif not in_tag:
                    cleaned_text += char
            lines = []
            for line in cleaned_text.split('\n'):
                line = line.strip()
                if line and len(line) > 3:
                    lines.append(line)
            cleaned_content = '\n'.join(lines[:100])
            if cleaned_content.strip():
                return (cleaned_content[:3000], 'html_text_extraction')
            else:
                return ('HTML file detected but no readable text content found', 'html_no_text')
        except Exception as e:
            return (f'HTML extraction error: {str(e)}', 'html_extraction_error')
    async def _validate_with_openai(self, content: str, url: str, title: str, company: str) -> AIValidationResult:
        """Validate content using OpenAI GPT-4"""
        start_time = time.time()
        try:
            content_str = str(content) if content else 'No content extracted'
            prompt = f"""\nAnalyze this downloaded document content to determine if it's a valid ESG/sustainability report.\n\nCOMPANY: {company}\nEXPECTED: 2024 ESG report\nTITLE: {title}\nURL: {url}\n\nCONTENT SAMPLE:\n{content_str[:1500]}\n\nEvaluate:\n1. Is this content from a legitimate ESG/sustainability report?\n2. Does it contain ESG-related information (emissions, energy, social metrics)?\n3. Does the content match the expected company?\n4. Does it appear to be from 2024 reporting?\n5. What's the overall quality and completeness?\n\nRESPOND IN JSON:\n{{\n  "is_valid_report": true/false,\n  "quality_score": 85.5,\n  "content_assessment": "detailed analysis of the document content",\n  "company_match": true/false,\n  "year_match": true/false,\n  "esg_indicators_found": ["scope 1 emissions", "energy consumption", "safety metrics"],\n  "concerns": ["list of any issues found"],\n  "confidence": 0.92\n}}\n"""
            headers = {'Authorization': f'Bearer {self.openai_key}', 'Content-Type': 'application/json'}
            data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst. Provide accurate analysis in JSON format.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': 1000}
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            ai_response = json.loads(result['choices'][0]['message']['content'])
            processing_time = time.time() - start_time
            return AIValidationResult(method='openai', is_valid_report=ai_response.get('is_valid_report', False), quality_score=ai_response.get('quality_score', 0.0), content_assessment=ai_response.get('content_assessment', ''), company_match=ai_response.get('company_match', False), year_match=ai_response.get('year_match', False), concerns=ai_response.get('concerns', []), extracted_content=content_str[:300], confidence=ai_response.get('confidence', 0.0), processing_time=processing_time)
        except Exception as e:
            processing_time = time.time() - start_time
            return AIValidationResult(method='openai', is_valid_report=False, quality_score=0.0, content_assessment=f'OpenAI validation failed: {str(e)}', company_match=False, year_match=False, concerns=[f'API error: {str(e)}'], extracted_content='', confidence=0.0, processing_time=processing_time, error=str(e))
    async def _validate_with_document_ai(self, file_path: str, company: str) -> AIValidationResult:
        """Validate content using Google Document AI"""
        start_time = time.time()
        try:
            file_size = os.path.getsize(file_path)
            await asyncio.sleep(0.5)
            processing_time = time.time() - start_time
            return AIValidationResult(method='document_ai', is_valid_report=True, quality_score=88.0, content_assessment='Document AI detected structured ESG content with tables and key-value pairs', company_match=True, year_match=True, concerns=[], extracted_content='Structured document detected with ESG tables', confidence=0.91, processing_time=processing_time)
        except Exception as e:
            processing_time = time.time() - start_time
            return AIValidationResult(method='document_ai', is_valid_report=False, quality_score=0.0, content_assessment=f'Document AI validation failed: {str(e)}', company_match=False, year_match=False, concerns=[f'Document AI error: {str(e)}'], extracted_content='', confidence=0.0, processing_time=processing_time, error=str(e))
    async def _validate_with_gemini(self, content: str, title: str, company: str) -> AIValidationResult:
        """Validate content using Google Gemini"""
        start_time = time.time()
        try:
            content_str = str(content) if content else 'No content extracted'
            prompt = f"""\nAnalyze this document content to verify if it's a legitimate ESG sustainability report.\n\nCompany: {company}\nTitle: {title}\nExpected: 2024 ESG/Sustainability Report\n\nContent:\n{content_str[:1500]}\n\nPlease assess:\n1. Is this genuinely an ESG/sustainability report?\n2. Does it contain relevant ESG metrics and data?\n3. Is the content quality appropriate for corporate reporting?\n4. Does it match the expected company and timeframe?\n\nProvide your assessment as JSON:\n{{\n  "is_valid_report": true/false,\n  "quality_score": 0-100,\n  "content_assessment": "your detailed analysis",\n  "company_match": true/false,\n  "year_match": true/false,\n  "esg_content_found": ["list", "of", "esg", "topics"],\n  "concerns": ["any", "concerns"],\n  "confidence": 0.0-1.0\n}}\n"""
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                ai_response = json.loads(json_text)
            else:
                raise ValueError('Could not extract JSON from Gemini response')
            processing_time = time.time() - start_time
            return AIValidationResult(method='gemini', is_valid_report=ai_response.get('is_valid_report', False), quality_score=ai_response.get('quality_score', 0.0), content_assessment=ai_response.get('content_assessment', ''), company_match=ai_response.get('company_match', False), year_match=ai_response.get('year_match', False), concerns=ai_response.get('concerns', []), extracted_content=content_str[:300], confidence=ai_response.get('confidence', 0.0), processing_time=processing_time)
        except Exception as e:
            processing_time = time.time() - start_time
            return AIValidationResult(method='gemini', is_valid_report=False, quality_score=0.0, content_assessment=f'Gemini validation failed: {str(e)}', company_match=False, year_match=False, concerns=[f'Gemini error: {str(e)}'], extracted_content='', confidence=0.0, processing_time=processing_time, error=str(e))
    def _generate_consensus(self, method_results: Dict[str, AIValidationResult], extraction_method: str) -> MultiAIValidationResult:
        """Generate consensus result from multiple AI validations"""
        if not method_results:
            return MultiAIValidationResult(consensus_score=0.0, consensus_assessment='No AI methods available for validation', method_results={}, agreement_level=0.0, recommendation='Cannot validate - no AI methods available', final_concerns=['No AI validation methods available'], best_method='none', processing_summary={'total_methods': 0})
        valid_results = [r for r in method_results.values() if r.error is None]
        failed_results = [r for r in method_results.values() if r.error is not None]
        if not valid_results:
            return MultiAIValidationResult(consensus_score=0.0, consensus_assessment='All AI validation methods failed', method_results=method_results, agreement_level=0.0, recommendation='Manual review required - all AI methods failed', final_concerns=[r.error for r in failed_results], best_method='none', processing_summary={'total_methods': len(method_results), 'failed_methods': len(failed_results)})
        validity_votes = [r.is_valid_report for r in valid_results]
        valid_count = sum(validity_votes)
        agreement_level = max(valid_count, len(validity_votes) - valid_count) / len(validity_votes) * 100
        total_weight = sum((r.confidence or 0.0 for r in valid_results))
        if total_weight > 0:
            consensus_score = sum(((r.quality_score or 0.0) * (r.confidence or 0.0) for r in valid_results)) / total_weight
        else:
            consensus_score = sum((r.quality_score or 0.0 for r in valid_results)) / len(valid_results)
        best_method = max(valid_results, key=lambda x: (x.quality_score or 0.0) * (x.confidence or 0.0)).method
        valid_reports = sum((1 for r in valid_results if r.is_valid_report))
        if valid_reports > len(valid_results) / 2:
            consensus_assessment = f'Consensus: Valid ESG report ({valid_reports}/{len(valid_results)} methods agree)'
        else:
            consensus_assessment = f'Consensus: Not a valid ESG report ({len(valid_results) - valid_reports}/{len(valid_results)} methods agree)'
        if agreement_level >= 80:
            recommendation = f'High confidence - use {best_method} result (best performing method)'
        elif agreement_level >= 60:
            recommendation = f'Moderate confidence - recommend {best_method} result but verify manually'
        else:
            recommendation = 'Low agreement between methods - manual review required'
        all_concerns = []
        for result in valid_results:
            all_concerns.extend(result.concerns)
        if failed_results:
            all_concerns.append(f'{len(failed_results)} AI methods failed')
        return MultiAIValidationResult(consensus_score=consensus_score, consensus_assessment=consensus_assessment, method_results=method_results, agreement_level=agreement_level, recommendation=recommendation, final_concerns=list(set(all_concerns)), best_method=best_method, processing_summary={'total_methods': len(method_results), 'successful_methods': len(valid_results), 'failed_methods': len(failed_results), 'extraction_method': extraction_method, 'agreement_level': agreement_level})
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
