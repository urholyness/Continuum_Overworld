
class EnhancedKPIExtractorAgent:
    """Agent based on EnhancedKPIExtractor from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "EnhancedKPIExtractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Enhanced KPI Extractor with metadata and greenwashing analysis"""
        """Initialize the enhanced extractor"""
        self.load_greenwashing_config()
        self.kpi_patterns = {'carbon_emissions_scope1': {'patterns': ['scope\\s*1.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'direct.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'scope\\s*1.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental', 'context_words': ['scope', 'direct', 'emissions', 'carbon', 'co2']}, 'carbon_emissions_scope2': {'patterns': ['scope\\s*2.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'indirect.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'electricity.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental', 'context_words': ['scope', 'indirect', 'electricity', 'purchased', 'energy']}, 'total_carbon_emissions': {'patterns': ['total.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'gross.*?emissions?.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)', 'carbon.*?footprint.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(mt|tonnes?|tons?|tco2e?)'], 'unit': 'mt CO2e', 'category': 'environmental', 'context_words': ['total', 'gross', 'footprint', 'overall', 'aggregate']}, 'renewable_energy_percentage': {'patterns': ['renewable.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%', 'clean.*?energy.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?renewable.*?energy'], 'unit': '%', 'category': 'environmental', 'context_words': ['renewable', 'clean', 'solar', 'wind', 'sustainable']}, 'water_consumption': {'patterns': ['water.*?consumption.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(liters?|gallons?|m3|cubic)', 'water.*?usage.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(liters?|gallons?|m3|cubic)', 'water.*?withdrawal.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(liters?|gallons?|m3|cubic)'], 'unit': 'liters', 'category': 'environmental', 'context_words': ['water', 'consumption', 'usage', 'withdrawal', 'intake']}, 'waste_generated': {'patterns': ['waste.*?generated.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(tons?|tonnes?|kg|pounds?)', 'total.*?waste.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(tons?|tonnes?|kg|pounds?)', 'waste.*?production.*?(\\d+[\\d,]*(?:\\.\\d+)?)\\s*(tons?|tonnes?|kg|pounds?)'], 'unit': 'tonnes', 'category': 'environmental', 'context_words': ['waste', 'generated', 'produced', 'disposed', 'landfill']}, 'employee_diversity_percentage': {'patterns': ['diversity.*?(\\d+(?:\\.\\d+)?)\\s*%', 'women.*?workforce.*?(\\d+(?:\\.\\d+)?)\\s*%', 'underrepresented.*?(\\d+(?:\\.\\d+)?)\\s*%'], 'unit': '%', 'category': 'social', 'context_words': ['diversity', 'women', 'minority', 'inclusion', 'representation']}, 'safety_incidents': {'patterns': ['safety.*?incidents?.*?(\\d+[\\d,]*)', 'workplace.*?injuries?.*?(\\d+[\\d,]*)', 'accidents?.*?(\\d+[\\d,]*)'], 'unit': 'count', 'category': 'social', 'context_words': ['safety', 'incidents', 'injuries', 'accidents', 'workplace']}, 'board_diversity_percentage': {'patterns': ['board.*?diversity.*?(\\d+(?:\\.\\d+)?)\\s*%', 'independent.*?directors?.*?(\\d+(?:\\.\\d+)?)\\s*%', 'women.*?board.*?(\\d+(?:\\.\\d+)?)\\s*%'], 'unit': '%', 'category': 'governance', 'context_words': ['board', 'directors', 'governance', 'independent', 'oversight']}, 'ethics_training_percentage': {'patterns': ['ethics.*?training.*?(\\d+(?:\\.\\d+)?)\\s*%', 'compliance.*?training.*?(\\d+(?:\\.\\d+)?)\\s*%', '(\\d+(?:\\.\\d+)?)\\s*%.*?ethics.*?training'], 'unit': '%', 'category': 'governance', 'context_words': ['ethics', 'compliance', 'training', 'code', 'conduct']}}
        self.init_enhanced_database()
    def load_greenwashing_config(self):
        """Load greenwashing analysis configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'greenwashing_config.json')
            with open(config_path, 'r') as f:
                self.greenwashing_config = json.load(f)
            logger.info('Greenwashing configuration loaded successfully')
        except Exception as e:
            logger.error(f'Error loading greenwashing config: {e}')
            self.greenwashing_config = {'indicators': {}, 'weights': {}, 'thresholds': {'low': 25, 'medium': 50, 'high': 75}}
    def init_enhanced_database(self):
        """Initialize enhanced database schema"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS extracted_kpis_enhanced (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    kpi_name VARCHAR(255),\n                    kpi_value FLOAT,\n                    kpi_unit VARCHAR(100),\n                    kpi_year INTEGER,\n                    confidence_score FLOAT,\n                    source_url TEXT,\n                    extraction_method VARCHAR(50),\n                    report_name VARCHAR(500),\n                    page_number INTEGER,\n                    matched_text TEXT,\n                    context_text TEXT,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS greenwashing_analysis (\n                    id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    overall_score FLOAT,\n                    indicator_scores JSONB,\n                    flagged_sections JSONB,\n                    report_name VARCHAR(500),\n                    analysis_year INTEGER,\n                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            cursor.execute('\n                ALTER TABLE greenwashing_analysis ADD COLUMN IF NOT EXISTS analysis_year INTEGER\n            ')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_kpis_enhanced_company ON extracted_kpis_enhanced(company)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_greenwashing_company ON greenwashing_analysis(company)')
            conn.commit()
            cursor.close()
            conn.close()
            logger.info('Enhanced database schema initialized successfully')
        except Exception as e:
            logger.error(f'Error initializing enhanced database: {e}')
    def download_pdf(self, url: str) -> Optional[str]:
        """Download PDF to temporary file"""
        try:
            logger.info(f'Downloading PDF from: {url}')
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()
            logger.info(f'PDF downloaded to: {temp_file.name}')
            return temp_file.name
        except Exception as e:
            logger.error(f'Error downloading PDF: {e}')
    def extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract year from text context"""
        year_patterns = ['20[12]\\d', '\\b(20[12]\\d)\\b']
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return int(matches[-1])
    def get_context_text(self, text: str, match_start: int, match_end: int, context_size: int=200) -> str:
        """Extract context around a match"""
        start = max(0, match_start - context_size)
        end = min(len(text), match_end + context_size)
        return text[start:end].strip()
    def extract_kpis_from_page(self, page_text: str, page_number: int, company: str, ticker: str, source_url: str, report_name: str, input_year: Optional[int]=None) -> List[KPIMetadata]:
        """Extract KPIs from a single page with metadata and year tagging"""
        kpis = []
        for kpi_name, config in self.kpi_patterns.items():
            for pattern in config['patterns']:
                try:
                    for match in re.finditer(pattern, page_text, re.IGNORECASE):
                        value_str = match.group(1).replace(',', '')
                        try:
                            kpi_value = float(value_str)
                        except ValueError:
                            continue
                        context_text = self.get_context_text(page_text, match.start(), match.end())
                        kpi_year = input_year or self.extract_year_from_text(context_text)
                        if not kpi_year:
                            kpi_year = 2024
                        confidence_score = self.calculate_confidence_score(match.group(0), context_text, config.get('context_words', []))
                        kpi = KPIMetadata(company=company, ticker=ticker, kpi_name=kpi_name, kpi_value=kpi_value, kpi_unit=config['unit'], kpi_year=kpi_year, confidence_score=confidence_score, source_url=source_url, extraction_method='regex_enhanced', report_name=report_name, page_number=page_number, matched_text=match.group(0), context_text=context_text, created_at=datetime.now())
                        kpis.append(kpi)
                except Exception as e:
                    logger.warning(f'Error processing pattern {pattern} for {kpi_name}: {e}')
                    continue
        return kpis
    def calculate_confidence_score(self, matched_text: str, context_text: str, context_words: List[str]) -> float:
        """Calculate confidence score based on context"""
        base_score = 0.7
        context_lower = context_text.lower()
        context_matches = sum((1 for word in context_words if word.lower() in context_lower))
        context_boost = min(0.2, context_matches * 0.05)
        length_boost = min(0.1, len(matched_text) / 100)
        return min(1.0, base_score + context_boost + length_boost)
    def analyze_greenwashing(self, full_text: str, kpis: List[KPIMetadata], company: str, ticker: str, report_name: str, analysis_year: Optional[int]=None) -> GreenwashingAnalysis:
        """Comprehensive greenwashing analysis"""
        indicator_scores = {}
        flagged_sections = []
        config = self.greenwashing_config
        if 'vagueness' in config['indicators']:
            vague_config = config['indicators']['vagueness']
            vague_count = 0
            for pattern in vague_config['patterns']:
                matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
                vague_count += len(matches)
                for match in matches:
                    context = self.get_context_text(full_text, match.start(), match.end(), 100)
                    flagged_sections.append({'type': 'vagueness', 'text': match.group(0), 'context': context, 'severity': 'medium', 'page': 1})
            total_sentences = len(re.split('[.!?]+', full_text))
            vague_ratio = vague_count / max(total_sentences, 1)
            indicator_scores['vagueness'] = min(100, vague_ratio / vague_config['threshold'] * 100)
        if 'sentiment_imbalance' in config['indicators']:
            sentiment_config = config['indicators']['sentiment_imbalance']
            blob = TextBlob(full_text)
            overall_sentiment = blob.sentiment.polarity
            risk_words = ['risk', 'challenge', 'difficulty', 'problem', 'issue', 'concern']
            risk_count = sum((len(re.findall(word, full_text, re.IGNORECASE)) for word in risk_words))
            total_words = len(full_text.split())
            risk_ratio = risk_count / max(total_words, 1)
            if overall_sentiment > sentiment_config['positive_threshold'] and risk_ratio < sentiment_config['risk_mentions_min']:
                indicator_scores['sentiment_imbalance'] = 80
                flagged_sections.append({'type': 'sentiment_imbalance', 'text': 'Overly positive tone without risk acknowledgment', 'context': f'Sentiment: {overall_sentiment:.2f}, Risk ratio: {risk_ratio:.3f}', 'severity': 'high', 'page': 1})
            else:
                indicator_scores['sentiment_imbalance'] = 0
        if 'contradictions' in config['indicators']:
            contradiction_config = config['indicators']['contradictions']
            contradiction_score = 0
            for claim in contradiction_config['zero_claims']:
                if re.search(claim, full_text, re.IGNORECASE):
                    relevant_kpis = [kpi for kpi in kpis if 'carbon' in kpi.kpi_name.lower() or 'emission' in kpi.kpi_name.lower()]
                    if any((kpi.kpi_value > 0 for kpi in relevant_kpis)):
                        contradiction_score += 25
                        flagged_sections.append({'type': 'contradiction', 'text': claim, 'context': f'Claim contradicts KPI data: {[kpi.kpi_value for kpi in relevant_kpis[:3]]}', 'severity': 'high', 'page': 1})
            indicator_scores['contradictions'] = min(100, contradiction_score)
        if 'omissions' in config['indicators']:
            omission_config = config['indicators']['omissions']
            required_categories = omission_config['required_categories']
            found_categories = []
            for category in required_categories:
                if re.search(category, full_text, re.IGNORECASE):
                    found_categories.append(category)
            missing_count = len(required_categories) - len(found_categories)
            omission_ratio = missing_count / len(required_categories)
            indicator_scores['omissions'] = omission_ratio * 100
            if missing_count > 0:
                missing_cats = [cat for cat in required_categories if cat not in found_categories]
                flagged_sections.append({'type': 'omissions', 'text': f"Missing categories: {', '.join(missing_cats)}", 'context': f'Found: {len(found_categories)}/{len(required_categories)} required categories', 'severity': 'medium', 'page': 1})
        if 'hype' in config['indicators']:
            hype_config = config['indicators']['hype']
            hype_count = 0
            for keyword in hype_config['keywords']:
                matches = len(re.findall(keyword, full_text, re.IGNORECASE))
                hype_count += matches
            if hype_count > hype_config['threshold']:
                indicator_scores['hype'] = min(100, hype_count / hype_config['threshold'] * 100)
                flagged_sections.append({'type': 'hype', 'text': f'Excessive marketing language: {hype_count} instances', 'context': 'Multiple superlative claims without substantiation', 'severity': 'low', 'page': 1})
            else:
                indicator_scores['hype'] = 0
        weights = config['weights']
        overall_score = sum((indicator_scores.get(indicator, 0) * weights.get(indicator, 0) for indicator in weights.keys()))
        return GreenwashingAnalysis(company=company, ticker=ticker, overall_score=overall_score, indicator_scores=indicator_scores, flagged_sections=flagged_sections, report_name=report_name, analysis_year=analysis_year, analysis_date=datetime.now())
    def process_pdf_with_metadata(self, url: str, company: str, ticker: str, input_year: Optional[int]=None) -> Tuple[List[KPIMetadata], GreenwashingAnalysis]:
        """Process PDF with full metadata and greenwashing analysis with year tagging"""
        start_time = time.time()
        kpis = []
        greenwashing_analysis = None
        try:
            pdf_path = self.download_pdf(url)
            if not pdf_path:
                return (kpis, greenwashing_analysis)
            with pdfplumber.open(pdf_path) as pdf:
                report_name = pdf.metadata.get('Title', '') or url.split('/')[-1].replace('.pdf', '')
                if not report_name:
                    report_name = f'{company} ESG Report'
                if not input_year:
                    try:
                        creation_date = pdf.metadata.get('CreationDate', '')
                        if creation_date:
                            input_year = int(str(creation_date)[:4])
                    except:
                logger.info(f'Processing {report_name} - {len(pdf.pages)} pages for year {input_year}')
                all_page_texts = []
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text() or ''
                        all_page_texts.append(page_text)
                        page_kpis = self.extract_kpis_from_page(page_text, page_num, company, ticker, url, report_name, input_year)
                        kpis.extend(page_kpis)
                        logger.info(f'Page {page_num}: {len(page_kpis)} KPIs extracted')
                    except Exception as e:
                        logger.warning(f'Error processing page {page_num}: {e}')
                        continue
                full_text = ' '.join(all_page_texts)
                greenwashing_analysis = self.analyze_greenwashing(full_text, kpis, company, ticker, report_name, input_year)
            try:
                os.unlink(pdf_path)
            except:
            processing_time = time.time() - start_time
            logger.info(f'Processing complete: {len(kpis)} KPIs, greenwashing score: {greenwashing_analysis.overall_score:.1f}, time: {processing_time:.2f}s')
        except Exception as e:
            logger.error(f'Error processing PDF {url}: {e}')
        return (kpis, greenwashing_analysis)
    def save_results_to_database(self, kpis: List[KPIMetadata], greenwashing: GreenwashingAnalysis):
        """Save results to enhanced database"""
        try:
            if kpis:
                kpi_data = []
                for kpi in kpis:
                    kpi_data.append({'company': kpi.company, 'ticker': kpi.ticker, 'kpi_name': kpi.kpi_name, 'kpi_value': kpi.kpi_value, 'kpi_unit': kpi.kpi_unit, 'kpi_year': kpi.kpi_year, 'confidence_score': kpi.confidence_score, 'source_url': kpi.source_url, 'extraction_method': kpi.extraction_method, 'report_name': kpi.report_name, 'page_number': kpi.page_number, 'matched_text': kpi.matched_text, 'context_text': kpi.context_text})
                kpi_df = pd.DataFrame(kpi_data)
                kpi_df.to_sql('extracted_kpis_enhanced', self.engine, if_exists='append', index=False)
                logger.info(f'Saved {len(kpis)} KPIs to database')
            if greenwashing:
                gw_data = {'company': greenwashing.company, 'ticker': greenwashing.ticker, 'overall_score': greenwashing.overall_score, 'indicator_scores': json.dumps(greenwashing.indicator_scores), 'flagged_sections': json.dumps(greenwashing.flagged_sections), 'report_name': greenwashing.report_name, 'analysis_year': greenwashing.analysis_year}
                gw_df = pd.DataFrame([gw_data])
                gw_df.to_sql('greenwashing_analysis', self.engine, if_exists='append', index=False)
                logger.info(f'Saved greenwashing analysis to database')
        except Exception as e:
            logger.error(f'Error saving to database: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
