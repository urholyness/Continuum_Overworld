
class _extract_kpis_from_contentAgent:
    """Agent based on _extract_kpis_from_content from ..\Rank_AI\03_document_parsing\langchain_esg_parser.py"""
    
    def __init__(self):
        self.name = "_extract_kpis_from_contentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
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
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
