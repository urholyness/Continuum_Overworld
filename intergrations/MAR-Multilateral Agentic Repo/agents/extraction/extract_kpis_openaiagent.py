
class extract_kpis_openaiAgent:
    """Agent based on extract_kpis_openai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "extract_kpis_openaiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Extract KPIs using OpenAI GPT for advanced text understanding
        Args:
            text (str): Extracted text from PDF
            max_length (int): Maximum text length to send to OpenAI
        Returns:
            List[KPIData]: List of extracted KPIs
        """
    if not self.openai_available:
        logger.warning('OpenAI API not available')
        return []
    try:
        if len(text) > max_length:
            text = text[:max_length]
        prompt = f'\n            Extract ESG (Environmental, Social, Governance) KPIs from the following text.\n            \n            Look for specific metrics like:\n            - Carbon emissions (Scope 1, 2, 3)\n            - Water consumption\n            - Renewable energy percentage\n            - Waste diversion rate\n            - Diversity metrics (women in workforce, leadership diversity)\n            - Safety incidents\n            - Board independence\n            \n            For each KPI found, provide:\n            - KPI name\n            - Numeric value\n            - Unit (if available)\n            - Year (if mentioned)\n            \n            Format as JSON array with objects containing: name, value, unit, year\n            \n            Text to analyze:\n            {text}\n            \n            JSON output:\n            '
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'system', 'content': 'You are an expert ESG analyst extracting KPIs from corporate reports.'}, {'role': 'user', 'content': prompt}], max_tokens=1000, temperature=0.1)
        content = response.choices[0].message.content.strip()
        json_match = re.search('\\[.*?\\]', content, re.DOTALL)
        if json_match:
            kpi_data = json.loads(json_match.group())
            kpis = []
            for item in kpi_data:
                if 'name' in item and 'value' in item:
                    kpi = KPIData(company='', ticker='', kpi_name=item['name'], kpi_value=float(item['value']) if item['value'] else None, kpi_unit=item.get('unit'), kpi_year=int(item['year']) if item.get('year') else None, confidence_score=0.9, source_url='', extraction_method='openai', raw_text=content)
                    kpis.append(kpi)
            return kpis
        logger.warning('Could not parse OpenAI response as JSON')
        return []
    except Exception as e:
        logger.error(f'Error extracting KPIs with OpenAI: {e}')
        return []
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
