
class _extract_core_logicAgent:
    """Agent based on _extract_core_logic from ..\MAR-Multilateral Agentic Repo\admin\code_refactoring_service.py"""
    
    def __init__(self):
        self.name = "_extract_core_logicAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract and refactor core logic from source patterns"""
    logic_prompt = f"\n        Extract and refactor the core logic from these code patterns for agent generation:\n        \n        Patterns:\n        {[{'file': p.source_file, 'function': p.source_function, 'type': p.pattern_type, 'description': p.functionality_description} for p in patterns]}\n        \n        Generate refactored code that:\n        1. Removes file I/O and makes it data-driven\n        2. Separates core logic from infrastructure\n        3. Makes it reusable and configurable\n        4. Follows clean code principles\n        \n        Return:\n        - core_logic: Main processing logic\n        - post_processing: Output formatting logic\n        - extracted_logic: Specific extracted patterns\n        - analysis_logic: Analysis-specific logic (if applicable)\n        - extraction_logic: Extraction-specific logic (if applicable)\n        \n        Return as JSON.\n        "
    result = query_llm(logic_prompt, model='claude-3')
    return json.loads(result.get('output', '{}'))
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
