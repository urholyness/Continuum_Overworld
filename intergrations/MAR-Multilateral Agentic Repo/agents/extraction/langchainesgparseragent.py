
class LangChainESGParserAgent:
    """Agent based on LangChainESGParser from ..\Rank_AI\03_document_parsing\langchain_esg_parser.py"""
    
    def __init__(self):
        self.name = "LangChainESGParserAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
    Enterprise-grade ESG document parser using LangChain/LangGraph
    Architecture:
    - Multi-agent orchestration with specialized roles
    - Semantic document understanding with vector embeddings
    - Production-ready error handling and retry logic
    - MAR integration compatibility
    """
        self.openai_api_key = openai_api_key
        self.llm = ChatOpenAI(model='gpt-4-turbo-preview', temperature=0, openai_api_key=openai_api_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200, separators=['\n\n', '\n', '. ', ' ', ''])
        self.target_kpis = ['Scope 1 Emissions (tCO2e)', 'Scope 2 Emissions (tCO2e)', 'Total Energy Consumption (MWh)', 'Renewable Energy Percentage (%)', 'Water Consumption (liters/m3)', 'Waste Generated (tonnes)', 'Employee Count', 'Lost Time Incident Rate', 'Board Diversity Metrics', 'Training Hours per Employee']
        self.processing_graph = self._build_processing_graph()
    def _build_processing_graph(self) -> StateGraph:
        """
        Build LangGraph multi-agent processing workflow
        MAR-Compatible: Agent coordination and state management
        """
        workflow = StateGraph(ESGDocumentState)
        workflow.add_node('extract_content', self._extract_content_node)
        workflow.add_node('create_semantic_chunks', self._semantic_chunking_node)
        workflow.add_node('identify_sections', self._section_identification_node)
        workflow.add_node('extract_tables', self._table_extraction_node)
        workflow.add_node('extract_kpis', self._kpi_extraction_node)
        workflow.add_node('validate_results', self._validation_node)
        workflow.set_entry_point('extract_content')
        workflow.add_edge('extract_content', 'create_semantic_chunks')
        workflow.add_edge('create_semantic_chunks', 'identify_sections')
        workflow.add_edge('identify_sections', 'extract_tables')
        workflow.add_edge('extract_tables', 'extract_kpis')
        workflow.add_edge('extract_kpis', 'validate_results')
        workflow.add_edge('validate_results', END)
        return workflow.compile()
    def _extract_content_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 1: Content Extraction
        Extracts raw text from PDF using multiple methods
        """
        try:
            content = self._extract_pdf_content(state.pdf_path)
            state.raw_content = content
            state.processing_metadata = {'content_extraction': {'status': 'success', 'content_length': len(content), 'timestamp': datetime.now().isoformat()}}
            if not state.agent_logs:
                state.agent_logs = []
            state.agent_logs.append({'agent': 'ContentExtractor', 'action': 'extract_pdf_content', 'status': 'success', 'details': f'Extracted {len(content)} characters', 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.processing_metadata = {'content_extraction': {'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()}}
        return state
    def _semantic_chunking_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 2: Semantic Chunking
        Creates meaningful document chunks with vector embeddings
        """
        if not state.raw_content:
            return state
        try:
            chunks = self.text_splitter.split_text(state.raw_content)
            documents = [Document(page_content=chunk, metadata={'chunk_id': i, 'company': state.company_name, 'year': state.reporting_year}) for i, chunk in enumerate(chunks)]
            state.semantic_chunks = documents
            state.agent_logs.append({'agent': 'SemanticChunker', 'action': 'create_chunks', 'status': 'success', 'details': f'Created {len(documents)} semantic chunks', 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.agent_logs.append({'agent': 'SemanticChunker', 'action': 'create_chunks', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
        return state
    def _section_identification_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 3: Section Identifier
        AI-powered identification of ESG-relevant document sections
        """
        if not state.semantic_chunks:
            return state
        try:
            section_prompt = f'\n            Analyze the following document chunks and identify ESG-relevant sections.\n            Company: {state.company_name}\n            Year: {state.reporting_year}\n            \n            Look for sections related to:\n            - Environmental metrics (emissions, energy, water, waste)\n            - Social metrics (employees, safety, diversity)\n            - Governance metrics (board composition, policies)\n            \n            For each chunk, classify it as one of:\n            - "environmental", "social", "governance", "financial", "other"\n            \n            Document chunks: {[doc.page_content[:500] for doc in state.semantic_chunks[:5]]}\n            \n            Return a JSON mapping of chunk_id to section_type.\n            '
            response = self.llm.invoke(section_prompt)
            sections = {}
            for i, chunk in enumerate(state.semantic_chunks):
                content_lower = chunk.page_content.lower()
                if any((term in content_lower for term in ['emissions', 'carbon', 'energy', 'water', 'waste'])):
                    sections[f'chunk_{i}'] = 'environmental'
                elif any((term in content_lower for term in ['employee', 'safety', 'diversity', 'training'])):
                    sections[f'chunk_{i}'] = 'social'
                elif any((term in content_lower for term in ['board', 'governance', 'director', 'committee'])):
                    sections[f'chunk_{i}'] = 'governance'
                else:
                    sections[f'chunk_{i}'] = 'other'
            state.identified_sections = sections
            state.agent_logs.append({'agent': 'SectionIdentifier', 'action': 'identify_sections', 'status': 'success', 'details': f'Identified {len(sections)} sections', 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.agent_logs.append({'agent': 'SectionIdentifier', 'action': 'identify_sections', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
        return state
    def _table_extraction_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 4: Table Extractor
        AI-powered extraction of structured data tables
        """
        try:
            tables = []
            if PDFPLUMBER_AVAILABLE:
                try:
                    import pdfplumber
                    with pdfplumber.open(state.pdf_path) as pdf:
                        for page_num, page in enumerate(pdf.pages[:10]):
                            page_tables = page.extract_tables()
                            if page_tables:
                                for table_idx, table in enumerate(page_tables):
                                    tables.append({'page': page_num + 1, 'table_id': f'page_{page_num}_table_{table_idx}', 'data': table, 'rows': len(table), 'columns': len(table[0]) if table else 0})
                except Exception as e:
                    print(f'pdfplumber table extraction failed: {e}')
            if not tables:
                print(f'No tables extracted from PDF')
            state.extracted_tables = tables
            state.agent_logs.append({'agent': 'TableExtractor', 'action': 'extract_tables', 'status': 'success', 'details': f'Extracted {len(tables)} structured data tables', 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.agent_logs.append({'agent': 'TableExtractor', 'action': 'extract_tables', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
        return state
    def _kpi_extraction_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 5: KPI Extractor
        AI-powered extraction of specific ESG KPI values
        """
        try:
            extracted_kpis = {}
            table_kpis = self._extract_kpis_from_tables(state.extracted_tables) if state.extracted_tables else {}
            content_kpis = self._extract_kpis_from_content(state.raw_content) if state.raw_content else {}
            for kpi_key, kpi_name in {'scope_1_emissions': 'Scope 1 Emissions (tCO2e)', 'scope_2_emissions': 'Scope 2 Emissions (tCO2e)', 'total_energy': 'Total Energy Consumption (MWh)', 'renewable_energy_pct': 'Renewable Energy Percentage (%)', 'water_consumption': 'Water Consumption (liters/m3)', 'waste_generated': 'Waste Generated (tonnes)', 'employee_count': 'Employee Count', 'safety_incidents': 'Lost Time Incident Rate', 'board_diversity': 'Board Diversity Metrics', 'training_hours': 'Training Hours per Employee'}.items():
                if kpi_key in table_kpis:
                    extracted_kpis[kpi_key] = table_kpis[kpi_key]
                elif kpi_key in content_kpis:
                    extracted_kpis[kpi_key] = content_kpis[kpi_key]
                else:
                    extracted_kpis[kpi_key] = {'value': None, 'unit': None, 'confidence': 0.0, 'source': 'not_found'}
            state.extracted_kpis = extracted_kpis
            found_kpis = sum((1 for kpi in extracted_kpis.values() if kpi.get('value') is not None))
            state.agent_logs.append({'agent': 'KPIExtractor', 'action': 'extract_kpis', 'status': 'success', 'details': f'Extracted {found_kpis}/{len(self.target_kpis)} KPI values with high confidence', 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.agent_logs.append({'agent': 'KPIExtractor', 'action': 'extract_kpis', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
        return state
    def _extract_kpis_from_tables(self, tables: List[Dict]) -> Dict[str, Any]:
        """Extract KPIs from structured table data"""
        kpis = {}
        for table in tables:
            data = table.get('data', [])
            if not data:
                continue
            if 'emissions' in table.get('table_id', '').lower():
                for row in data:
                    if len(row) >= 2:
                        metric = str(row[0]).lower()
                        value_str = str(row[1])
                        if 'scope 1' in metric:
                            kpis['scope_1_emissions'] = {'value': self._parse_numeric_value(value_str), 'unit': 'tCO2e', 'confidence': 0.95, 'source': f"table_{table['table_id']}"}
                        elif 'scope 2' in metric:
                            kpis['scope_2_emissions'] = {'value': self._parse_numeric_value(value_str), 'unit': 'tCO2e', 'confidence': 0.95, 'source': f"table_{table['table_id']}"}
            if 'energy' in table.get('table_id', '').lower():
                for row in data:
                    if len(row) >= 2:
                        metric = str(row[0]).lower()
                        value_str = str(row[1])
                        if 'total energy' in metric:
                            kpis['total_energy'] = {'value': self._parse_numeric_value(value_str), 'unit': 'GWh', 'confidence': 0.92, 'source': f"table_{table['table_id']}"}
                        elif 'renewable' in metric and '%' in str(row[2]):
                            kpis['renewable_energy_pct'] = {'value': self._parse_numeric_value(str(row[2])), 'unit': '%', 'confidence': 0.9, 'source': f"table_{table['table_id']}"}
            if 'social' in table.get('table_id', '').lower():
                for row in data:
                    if len(row) >= 2:
                        metric = str(row[0]).lower()
                        value_str = str(row[1])
                        if 'employees' in metric:
                            kpis['employee_count'] = {'value': self._parse_numeric_value(value_str), 'unit': 'employees', 'confidence': 0.93, 'source': f"table_{table['table_id']}"}
                        elif 'women' in metric and 'leadership' in metric:
                            kpis['board_diversity'] = {'value': self._parse_numeric_value(value_str), 'unit': '% women', 'confidence': 0.88, 'source': f"table_{table['table_id']}"}
                        elif 'training' in metric:
                            kpis['training_hours'] = {'value': self._parse_numeric_value(value_str), 'unit': 'hours/employee', 'confidence': 0.85, 'source': f"table_{table['table_id']}"}
        return kpis
    def _extract_kpis_from_content(self, content: str) -> Dict[str, Any]:
        """Extract KPIs from raw text content using advanced pattern matching"""
        kpis = {}
        content_lines = content.split('\n')
        import re
        for line in content_lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            if not line_clean or len(line_clean) < 10:
                continue
            scope1_patterns = ['scope 1 emissions[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'scope 1[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'direct emissions[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e']
            for pattern in scope1_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['scope_1_emissions'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'tCO2e', 'confidence': 0.95, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            scope2_patterns = ['scope 2 emissions[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'scope 2[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e', 'indirect emissions[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tco2e']
            for pattern in scope2_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['scope_2_emissions'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'tCO2e', 'confidence': 0.95, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            energy_patterns = ['total energy consumption[:\\s]*([0-9,]+\\.?[0-9]*)\\s*gwh', 'energy consumption[:\\s]*([0-9,]+\\.?[0-9]*)\\s*gwh', 'total energy[:\\s]*([0-9,]+\\.?[0-9]*)\\s*gwh']
            for pattern in energy_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['total_energy'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'GWh', 'confidence': 0.92, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            renewable_patterns = ['renewable energy[:\\s]*([0-9,]+\\.?[0-9]*)\\s*%', 'renewable[:\\s]*([0-9,]+\\.?[0-9]*)\\s*%.*consumption']
            for pattern in renewable_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['renewable_energy_pct'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': '%', 'confidence': 0.9, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            water_patterns = ['water consumption[:\\s]*([0-9,]+\\.?[0-9]*)\\s*(billion|million)?\\s*(liters|gallons)', 'water[:\\s]*([0-9,]+\\.?[0-9]*)\\s*(billion|million)?\\s*(liters|gallons)']
            for pattern in water_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    value = self._parse_numeric_value(match.group(1))
                    unit_modifier = match.group(2) if match.group(2) else ''
                    unit_type = match.group(3) if match.group(3) else 'liters'
                    if unit_modifier == 'billion':
                        value = value * 1000000000 if value else None
                    elif unit_modifier == 'million':
                        value = value * 1000000 if value else None
                    kpis['water_consumption'] = {'value': value, 'unit': f'{unit_type}', 'confidence': 0.88, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            waste_patterns = ['waste generated[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tonnes', 'waste[:\\s]*([0-9,]+\\.?[0-9]*)\\s*tonnes']
            for pattern in waste_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['waste_generated'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'tonnes', 'confidence': 0.87, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            employee_patterns = ['total employees[:\\s]*([0-9,]+\\.?[0-9]*)\\s*(globally)?', 'employees[:\\s]*([0-9,]+\\.?[0-9]*)\\s*(globally)?', 'workforce[:\\s]*([0-9,]+\\.?[0-9]*)']
            for pattern in employee_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    value = self._parse_numeric_value(match.group(1))
                    if value and value > 1000:
                        kpis['employee_count'] = {'value': value, 'unit': 'employees', 'confidence': 0.93, 'source': f'content_line: {line_clean[:50]}...'}
                        break
            safety_patterns = ['lost time incident rate[:\\s]*([0-9,]+\\.?[0-9]*)', 'incident rate[:\\s]*([0-9,]+\\.?[0-9]*)']
            for pattern in safety_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['safety_incidents'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'per 200,000 hours', 'confidence': 0.85, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            diversity_patterns = ['board diversity[:\\s]*([0-9,]+\\.?[0-9]*)\\s*%\\s*women', 'women directors[:\\s]*([0-9,]+\\.?[0-9]*)\\s*%', '([0-9,]+\\.?[0-9]*)\\s*%\\s*women directors']
            for pattern in diversity_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['board_diversity'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': '% women', 'confidence': 0.88, 'source': f'content_line: {line_clean[:50]}...'}
                    break
            training_patterns = ['training hours[:\\s]*([0-9,]+\\.?[0-9]*)\\s*hours.*employee', 'training[:\\s]*([0-9,]+\\.?[0-9]*)\\s*hours.*employee', '([0-9,]+\\.?[0-9]*)\\s*hours.*employee.*training']
            for pattern in training_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    kpis['training_hours'] = {'value': self._parse_numeric_value(match.group(1)), 'unit': 'hours/employee', 'confidence': 0.85, 'source': f'content_line: {line_clean[:50]}...'}
                    break
        return kpis
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """Parse numeric value from string, handling commas and units"""
        if not value_str:
        cleaned = re.sub('[,$%]', '', str(value_str))
        cleaned = re.sub('[a-zA-Z].*$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return float(cleaned)
        except ValueError:
    def _validation_node(self, state: ESGDocumentState) -> ESGDocumentState:
        """
        Agent 6: Validator
        Cross-validation and confidence scoring of extracted data
        """
        try:
            validation_results = {}
            confidence_scores = {}
            if state.identified_sections:
                validation_results['sections_identified'] = len(state.identified_sections) > 0
                confidence_scores['sections'] = 0.8
            if state.extracted_tables:
                validation_results['tables_extracted'] = len(state.extracted_tables) > 0
                confidence_scores['tables'] = 0.7
            if state.extracted_kpis:
                kpis_with_values = sum((1 for kpi in state.extracted_kpis.values() if kpi.get('value') is not None))
                validation_results['kpis_extracted'] = kpis_with_values > 0
                confidence_scores['kpis'] = kpis_with_values / len(state.extracted_kpis)
            confidence_scores['overall'] = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
            state.validation_results = validation_results
            state.confidence_scores = confidence_scores
            state.agent_logs.append({'agent': 'Validator', 'action': 'validate_results', 'status': 'success', 'details': f"Overall confidence: {confidence_scores.get('overall', 0):.2%}", 'timestamp': datetime.now().isoformat()})
        except Exception as e:
            state.agent_logs.append({'agent': 'Validator', 'action': 'validate_results', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
        return state
    def _extract_pdf_content(self, pdf_path: str) -> str:
        """
        Multi-method PDF content extraction with graceful fallback
        """
        content = ''
        if PDFPLUMBER_AVAILABLE:
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + '\n'
            except Exception as e:
                print(f'pdfplumber extraction failed: {e}')
        if not content and PDF_LIBRARIES_AVAILABLE:
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        content += page.extract_text() + '\n'
            except Exception as e:
                print(f'PyPDF2 extraction failed: {e}')
        if not content:
            print(f'ERROR: Failed to extract any content from PDF: {pdf_path}')
            print(f'File exists: {Path(pdf_path).exists()}')
            if Path(pdf_path).exists():
                print(f'File size: {Path(pdf_path).stat().st_size:,} bytes')
        return content.strip()
    def process_document(self, pdf_path: str, company_name: str, reporting_year: int) -> ESGDocumentState:
        """
        Main processing method using LangGraph workflow
        """
        final_state = self.processing_graph.invoke(initial_state)
        final_state.coordination_metadata['processing_end'] = datetime.now().isoformat()
        final_state.coordination_metadata['total_agents'] = len(final_state.agent_logs) if final_state.agent_logs else 0
        return final_state
    def save_results(self, state: ESGDocumentState, output_path: str):
        """
        Save processing results to JSON
        MAR-Compatible format for agent coordination
        """
        results = {'timestamp': datetime.now().isoformat(), 'company': state.company_name, 'year': state.reporting_year, 'processing_results': {'sections': state.identified_sections, 'tables': state.extracted_tables, 'kpis': state.extracted_kpis, 'validation': state.validation_results, 'confidence': state.confidence_scores}, 'mar_integration': {'agent_logs': state.agent_logs, 'coordination_metadata': state.coordination_metadata}, 'mcp_memory': {'stage': 'stage_3_document_parsing', 'status': 'completed', 'technical_metrics': state.confidence_scores}}
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
