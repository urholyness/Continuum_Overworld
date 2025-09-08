
class _extract_kpis_from_tablesAgent:
    """Agent based on _extract_kpis_from_tables from ..\Rank_AI\03_document_parsing\langchain_esg_parser.py"""
    
    def __init__(self):
        self.name = "_extract_kpis_from_tablesAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
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
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
