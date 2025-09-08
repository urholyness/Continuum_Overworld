
class analyze_code_patternsAgent:
    """Agent based on analyze_code_patterns from ..\MAR-Multilateral Agentic Repo\admin\code_refactoring_service.py"""
    
    def __init__(self):
        self.name = "analyze_code_patternsAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Analyze discovered code to identify reusable patterns"""
    patterns = []
    for item in discovered_metadata:
        try:
            source_path = Path(item['file'])
            with open(source_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            analysis_prompt = f"\n                Analyze this code for agent generation potential:\n                \n                File: {item['file']}\n                Function/Class: {item['name']}\n                Type: {item['type']}\n                \n                Code:\n                {item.get('source_code', 'N/A')}\n                \n                Determine:\n                1. Pattern type (processor/analyzer/extractor/validator/other)\n                2. Input/output types\n                3. Core functionality description\n                4. Dependencies required\n                5. Reusability score (0-1)\n                6. Complexity score (0-1)\n                \n                Return JSON format.\n                "
            analysis = query_llm(analysis_prompt, model='gpt-4o')
            pattern_data = json.loads(analysis.get('output', '{}'))
            pattern = CodePattern(pattern_id=item['id'], pattern_type=pattern_data.get('pattern_type', 'unknown'), source_file=item['file'], source_function=item['name'], functionality_description=pattern_data.get('functionality', ''), input_types=pattern_data.get('input_types', []), output_types=pattern_data.get('output_types', []), dependencies=pattern_data.get('dependencies', []), complexity_score=pattern_data.get('complexity_score', 0.5), reusability_score=pattern_data.get('reusability_score', 0.5))
            patterns.append(pattern)
        except Exception as e:
            print(f"❌ Failed to analyze pattern {item['id']}: {e}")
    return patterns
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
