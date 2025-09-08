
class _kpi_extraction_agentAgent:
    """Agent based on _kpi_extraction_agent from ..\Rank_AI\03_document_parsing\simple_esg_parser.py"""
    
    def __init__(self):
        self.name = "_kpi_extraction_agentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Agent 5: Simple KPI Extraction (keyword matching)"""
    if not state.raw_content:
        return state
    try:
        extracted_kpis = {}
        content_lower = state.raw_content.lower()
        kpi_keywords = {'scope_1_emissions': ['scope 1', 'direct emissions'], 'scope_2_emissions': ['scope 2', 'indirect emissions'], 'total_energy': ['energy consumption', 'total energy'], 'renewable_energy_pct': ['renewable energy', 'renewable %'], 'water_consumption': ['water consumption', 'water usage'], 'waste_generated': ['waste generated', 'total waste'], 'employee_count': ['employees', 'workforce', 'headcount'], 'safety_incidents': ['safety', 'incidents', 'lost time'], 'board_diversity': ['board diversity', 'diversity'], 'training_hours': ['training hours', 'training']}
        for kpi_name, keywords in kpi_keywords.items():
            found = any((keyword in content_lower for keyword in keywords))
            extracted_kpis[kpi_name] = {'value': None, 'confidence': 0.5 if found else 0.0, 'found_keywords': found}
        state.extracted_kpis = extracted_kpis
        found_count = sum((1 for kpi in extracted_kpis.values() if kpi.get('found_keywords')))
        state.agent_logs.append({'agent': 'KPIExtractor', 'action': 'extract_kpis', 'status': 'success', 'details': f'Found {found_count}/{len(self.target_kpis)} KPI keywords', 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        state.agent_logs.append({'agent': 'KPIExtractor', 'action': 'extract_kpis', 'status': 'error', 'error': str(e), 'timestamp': datetime.now().isoformat()})
    return state
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
