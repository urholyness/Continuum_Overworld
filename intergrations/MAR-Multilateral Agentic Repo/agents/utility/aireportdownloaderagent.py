
class AIReportDownloaderAgent:
    """Agent based on AIReportDownloader from ..\Rank_AI\02_report_acquisition\ai_report_downloader.py"""
    
    def __init__(self):
        self.name = "AIReportDownloaderAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Pure AI-powered ESG report acquisition system with multi-AI validation"""
        """Initialize AI report downloader with multi-AI validation"""
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.download_dir = download_dir
        self.validation_methods = validation_methods
        if not self.openai_key:
            raise ValueError('Missing OPENAI_API_KEY for AI content validation')
        os.makedirs(self.download_dir, exist_ok=True)
        try:
            from ai_multi_validator import MultiAIValidator
            self.multi_validator = MultiAIValidator(validation_methods=validation_methods)
            print(f'✅ Multi-AI validator initialized with methods: {self.multi_validator.validation_methods}')
        except ImportError:
            print('⚠️ Multi-AI validator not available, using basic OpenAI validation')
            self.multi_validator = None
    def acquire_reports(self, stage1_urls: Dict) -> Dict[str, List[AcquisitionResult]]:
        """
        AI-guided acquisition of ESG reports from Stage 1 URLs
        Uses pure AI reasoning for content validation - no regex patterns
        """
        print(f'🤖 AI Report Acquisition Starting')
        print(f'📁 Download directory: {self.download_dir}')
        results = {}
        for company, urls in stage1_urls.items():
            print(f"\n🏢 ACQUIRING: {company.replace('_', ' ').title()}")
            print('=' * 50)
            company_results = []
            for url_data in urls:
                result = self._ai_acquire_single_report(url_data, company)
                company_results.append(result)
            results[company] = company_results
        return results
    def _ai_acquire_single_report(self, url_data: Dict, company: str) -> AcquisitionResult:
        """AI-guided acquisition of a single ESG report"""
        url = url_data['url']
        title = url_data['title']
        print(f'\n📥 ACQUIRING: {title}')
        print(f'🔗 URL: {url}')
        pre_validation = self._ai_pre_download_validation(url, title, company)
        if not pre_validation['should_download']:
            print(f"❌ AI Pre-validation: {pre_validation['reasoning']}")
            return AcquisitionResult(url=url, title=title, content_type='unknown', file_size=0, download_success=False, ai_content_validation=pre_validation, local_path=None, download_timestamp=datetime.now().isoformat(), acquisition_method='AI_PRE_VALIDATION_REJECTED', ai_quality_score=0.0)
        download_result = self._ai_intelligent_download(url, title, company)
        if not download_result['success']:
            print(f"❌ Download failed: {download_result['error']}")
            return AcquisitionResult(url=url, title=title, content_type='unknown', file_size=0, download_success=False, ai_content_validation=download_result, local_path=None, download_timestamp=datetime.now().isoformat(), acquisition_method='AI_DOWNLOAD_FAILED', ai_quality_score=0.0)
        try:
            import nest_asyncio
            nest_asyncio.apply()
            content_validation = asyncio.run(self._multi_ai_post_download_validation(download_result['local_path'], url, title, company))
        except ImportError:
            content_validation = self._sync_post_download_validation(download_result['local_path'], url, title, company)
        print(f"✅ Downloaded: {download_result['file_size']} bytes")
        print(f"🤖 AI Quality Score: {content_validation['quality_score']:.1f}%")
        return AcquisitionResult(url=url, title=title, content_type=download_result['content_type'], file_size=download_result['file_size'], download_success=True, ai_content_validation=content_validation, local_path=download_result['local_path'], download_timestamp=datetime.now().isoformat(), acquisition_method='AI_GUIDED_DOWNLOAD', ai_quality_score=content_validation['quality_score'])
    def _ai_pre_download_validation(self, url: str, title: str, company: str) -> Dict:
        """AI validates URL before download attempt"""
        prompt = f"""\nAnalyze this URL for ESG report download viability.\n\nCOMPANY: {company}\nURL: {url}\nTITLE: {title}\n\nEvaluate:\n1. Is this likely a downloadable ESG report file?\n2. Is the URL structure valid and accessible?\n3. Are there any security or content concerns?\n4. What's the expected file type and size?\n\nRESPOND IN JSON:\n{{\n  "should_download": true/false,\n  "reasoning": "detailed AI assessment",\n  "expected_file_type": "pdf|html|doc|unknown",\n  "estimated_size_mb": 5.2,\n  "security_assessment": "safe|caution|risky",\n  "download_strategy": "direct|browser_headers|special_handling"\n}}\n"""
        try:
            response = self._call_openai(prompt, max_tokens=800)
            return json.loads(response)
        except Exception as e:
            print(f'⚠️ AI pre-validation failed: {e}')
            return {'should_download': True, 'reasoning': f'AI validation error, proceeding with caution: {str(e)}', 'expected_file_type': 'unknown', 'estimated_size_mb': 0, 'security_assessment': 'unknown', 'download_strategy': 'direct'}
    def _ai_intelligent_download(self, url: str, title: str, company: str) -> Dict:
        """AI-guided intelligent download with smart headers and retry logic"""
        try:
            headers = self._ai_generate_download_headers(url)
            filename = self._ai_generate_filename(url, title, company)
            local_path = os.path.join(self.download_dir, filename)
            print(f'  📊 AI Headers: {len(headers)} custom headers')
            print(f'  📄 AI Filename: {filename}')
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            content = response.content
            is_pdf = content.startswith(b'%PDF')
            is_html = 'text/html' in content_type or content.startswith(b'<!DOCTYPE') or content.startswith(b'<html')
            if is_html and (not is_pdf):
                print(f'  ❌ Downloaded HTML instead of PDF')
                print(f'  💡 Content-Type: {content_type}')
                print(f'  🔍 Attempting to find PDF link in HTML...')
                html_text = content.decode('utf-8', errors='ignore')
                pdf_urls = []
                import re
                pdf_pattern = 'href=["\\\']([^"\\\']*\\.pdf[^"\\\']*)["\\\']'
                matches = re.findall(pdf_pattern, html_text, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        pdf_urls.append(match)
                    elif match.startswith('/'):
                        from urllib.parse import urljoin
                        pdf_urls.append(urljoin(url, match))
                if pdf_urls:
                    print(f'  🔗 Found {len(pdf_urls)} PDF links in HTML')
                    pdf_url = pdf_urls[0]
                    print(f'  📥 Attempting to download: {pdf_url[:80]}...')
                    try:
                        pdf_response = requests.get(pdf_url, headers=headers, timeout=30, allow_redirects=True)
                        pdf_response.raise_for_status()
                        if pdf_response.content.startswith(b'%PDF'):
                            print(f'  ✅ Successfully downloaded PDF from HTML page')
                            content = pdf_response.content
                            content_type = pdf_response.headers.get('content-type', 'application/pdf')
                        else:
                            return {'success': False, 'error': 'Found PDF link but download was not a valid PDF', 'local_path': None, 'file_size': 0, 'content_type': content_type}
                    except Exception as e:
                        return {'success': False, 'error': f'Failed to download PDF from HTML: {str(e)}', 'local_path': None, 'file_size': 0, 'content_type': content_type}
                else:
                    return {'success': False, 'error': 'Downloaded HTML page with no PDF links found', 'local_path': None, 'file_size': 0, 'content_type': content_type}
            if not content.startswith(b'%PDF'):
                return {'success': False, 'error': f'Downloaded content is not a PDF (content-type: {content_type})', 'local_path': None, 'file_size': 0, 'content_type': content_type}
            with open(local_path, 'wb') as f:
                f.write(content)
            return {'success': True, 'local_path': local_path, 'file_size': len(content), 'content_type': content_type, 'status_code': response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e), 'local_path': None, 'file_size': 0, 'content_type': 'unknown'}
    def _ai_generate_download_headers(self, url: str) -> Dict[str, str]:
        """AI generates appropriate HTTP headers for the download"""
        domain = urlparse(url).netloc
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1'}
        if 'corporate' in domain or 'about.' in domain:
            headers['Referer'] = f'https://{domain}/'
        return headers
    def _ai_generate_filename(self, url: str, title: str, company: str) -> str:
        """AI generates safe, descriptive filename"""
        url_parts = url.split('.')
        extension = url_parts[-1].lower() if len(url_parts) > 1 else 'pdf'
        if '?' in extension:
            extension = extension.split('?')[0]
        valid_extensions = ['pdf', 'html', 'doc', 'docx', 'txt']
        if extension not in valid_extensions:
            extension = 'pdf'
        company_clean = company.replace('_', '-')
        title_words = title.replace(' ', '-').lower()
        max_title_length = 50
        if len(title_words) > max_title_length:
            title_words = title_words[:max_title_length]
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f'{company_clean}-2024-esg-report-{url_hash}.{extension}'
        return filename
    def _ai_post_download_validation(self, file_path: str, url: str, title: str, company: str) -> Dict:
        """AI validates downloaded content quality"""
        file_size = os.path.getsize(file_path)
        file_ext = file_path.split('.')[-1].lower()
        sample_content = ''
        content_extraction_method = ''
        try:
            if file_ext == 'pdf':
                sample_content, content_extraction_method = self._extract_pdf_content(file_path)
            elif file_ext in ['html', 'htm']:
                sample_content, content_extraction_method = self._extract_html_content(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    sample_content = f.read(2000)
                    content_extraction_method = 'plain_text_read'
        except Exception as e:
            sample_content = f'Content extraction failed: {str(e)}'
            content_extraction_method = 'extraction_error'
        prompt = f'\nValidate this downloaded ESG report content.\n\nCOMPANY: {company}\nEXPECTED TITLE: {title}\nFILE SIZE: {file_size} bytes\nFILE TYPE: {file_ext}\nEXTRACTION METHOD: {content_extraction_method}\nSAMPLE CONTENT: {sample_content[:1000]}\n\nAssess:\n1. Is this a valid ESG/sustainability report file?\n2. Does the content match the expected company and year (2024)?\n3. Is the file size reasonable for an ESG report?\n4. Any quality issues or concerns?\n\nRate overall quality 0-100%.\n\nRESPOND IN JSON:\n{{\n  "is_valid_report": true/false,\n  "quality_score": 85.5,\n  "content_assessment": "detailed analysis of file content",\n  "file_type_validation": "confirmed PDF|HTML|other",\n  "company_match": true/false,\n  "year_match": true/false,\n  "concerns": ["list", "of", "issues"],\n  "recommendations": "AI recommendations for this file"\n}}\n'
        try:
            response = self._call_openai(prompt, max_tokens=1000)
            validation = json.loads(response)
            return validation
        except Exception as e:
            print(f'⚠️ AI post-validation failed: {e}')
            return {'is_valid_report': True, 'quality_score': 70.0, 'content_assessment': f'AI validation error: {str(e)}', 'file_type_validation': f'File type: {file_ext}', 'company_match': True, 'year_match': True, 'concerns': ['AI validation unavailable'], 'recommendations': 'Manual review recommended'}
    def _extract_pdf_content(self, file_path: str) -> Tuple[str, str]:
        """Extract readable text content from PDF file"""
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
            with open(file_path, 'rb') as f:
                first_bytes = f.read(10)
                if first_bytes.startswith(b'%PDF-'):
                    return (f'Valid PDF file detected ({os.path.getsize(file_path)} bytes), but no PDF extraction library available', 'pdf_validation_only')
                else:
                    return (f'File does not appear to be a valid PDF (starts with: {first_bytes})', 'invalid_pdf_format')
        except Exception as e:
            return (f'PDF extraction error: {str(e)}', 'pdf_extraction_error')
    def _extract_html_content(self, file_path: str) -> Tuple[str, str]:
        """Extract readable text content from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read(5000)
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
            cleaned_content = '\n'.join(lines[:50])
            if cleaned_content.strip():
                return (cleaned_content[:2000], 'html_text_extraction')
            else:
                return (f'HTML file detected but no readable text content found', 'html_no_text')
        except Exception as e:
            return (f'HTML extraction error: {str(e)}', 'html_extraction_error')
    def _sync_post_download_validation(self, file_path: str, url: str, title: str, company: str) -> Dict:
        """Synchronous fallback validation"""
        if not os.path.exists(file_path):
            return {'quality_score': 0.0, 'validation_methods': ['file_check'], 'validation_results': {'file_exists': False}, 'reasoning': 'Downloaded file not found'}
        file_size = os.path.getsize(file_path)
        if file_size < 1000:
            return {'quality_score': 20.0, 'validation_methods': ['file_size'], 'validation_results': {'file_size_bytes': file_size}, 'reasoning': 'File too small to be meaningful ESG report'}
        try:
            with open(file_path, 'rb') as f:
                header = f.read(10)
                is_pdf = header.startswith(b'%PDF-')
        except:
            is_pdf = False
        quality_score = 70.0 if is_pdf else 50.0
        return {'quality_score': quality_score, 'validation_methods': ['file_check', 'format_detection'], 'validation_results': {'file_exists': True, 'file_size_bytes': file_size, 'is_pdf': is_pdf}, 'reasoning': f"Basic validation complete - {('PDF detected' if is_pdf else 'Non-PDF file')}"}
    async def _multi_ai_post_download_validation(self, file_path: str, url: str, title: str, company: str) -> Dict:
        """Multi-AI validation of downloaded content"""
        if self.multi_validator:
            try:
                multi_result = await self.multi_validator.validate_report_content(file_path, url, title, company)
                return {'is_valid_report': multi_result.consensus_score > 50, 'quality_score': multi_result.consensus_score, 'content_assessment': multi_result.consensus_assessment, 'file_type_validation': f'Multi-AI validation using {len(multi_result.method_results)} methods', 'company_match': any((r.company_match for r in multi_result.method_results.values() if r.error is None)), 'year_match': any((r.year_match for r in multi_result.method_results.values() if r.error is None)), 'concerns': multi_result.final_concerns, 'recommendations': multi_result.recommendation, 'method_results': {method: {'quality_score': result.quality_score, 'confidence': result.confidence, 'assessment': result.content_assessment, 'processing_time': result.processing_time, 'error': result.error} for method, result in multi_result.method_results.items()}, 'agreement_level': multi_result.agreement_level, 'best_method': multi_result.best_method}
            except Exception as e:
                print(f'⚠️ Multi-AI validation failed, falling back to basic validation: {e}')
                return await self._fallback_validation(file_path, url, title, company)
        else:
            return await self._fallback_validation(file_path, url, title, company)
    async def _fallback_validation(self, file_path: str, url: str, title: str, company: str) -> Dict:
        """Fallback to basic AI validation if multi-AI system fails"""
        return self._ai_post_download_validation(file_path, url, title, company)
    def _call_openai(self, prompt: str, max_tokens: int=1000) -> str:
        """Call OpenAI API with error handling"""
        headers = {'Authorization': f'Bearer {self.openai_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-4', 'messages': [{'role': 'system', 'content': 'You are an expert ESG analyst specializing in report acquisition and validation. Provide accurate, detailed analysis in the requested JSON format.'}, {'role': 'user', 'content': prompt}], 'temperature': 0.1, 'max_tokens': max_tokens}
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
