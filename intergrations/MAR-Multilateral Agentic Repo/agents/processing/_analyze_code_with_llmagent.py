
class _analyze_code_with_llmAgent:
    """Agent based on _analyze_code_with_llm from ..\MAR-Multilateral Agentic Repo\admin\omen_agent.py"""
    
    def __init__(self):
        self.name = "_analyze_code_with_llmAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Use LLM to analyze code for agent generation potential"""
    analysis_prompt = f"\n        Analyze this code for AI agent generation potential:\n        \n        File: {path}\n        Name: {node.name}\n        Type: {('function' if isinstance(node, ast.FunctionDef) else 'class')}\n        \n        Code:\n        {source_code}\n        \n        Determine:\n        1. functionality_type: What type of processing does this do? (processor/analyzer/extractor/validator/transformer/searcher/other)\n        2. input_signature: What types of inputs does it expect? (list of type descriptions)\n        3. output_signature: What types of outputs does it produce? (list of type descriptions)\n        4. dependencies: What external libraries/modules does it use? (list)\n        5. complexity_score: How complex is this code? (0.0-1.0, where 1.0 is very complex)\n        6. reusability_score: How reusable is this for other contexts? (0.0-1.0, where 1.0 is highly reusable)\n        7. llm_compatible: Could this benefit from LLM integration? (true/false)\n        8. agent_potential: Overall potential as an agent component (high/medium/low)\n        9. doc: Brief documentation of what this code does\n        10. related_patterns: What other patterns might this work well with? (list of strings)\n        \n        Return JSON format only.\n        "
    try:
        response = query_llm(analysis_prompt, model='gpt-4o')
        analysis_data = json.loads(response.get('output', '{}'))
        if analysis_data.get('agent_potential', 'low') in ['high', 'medium']:
            return CodeDiscovery(id=self.make_id(path, node.name), name=node.name, file=str(path), type='function' if isinstance(node, ast.FunctionDef) else 'class', source_code=source_code, doc=analysis_data.get('doc', ''), status='discovered', functionality_type=analysis_data.get('functionality_type', 'other'), input_signature=analysis_data.get('input_signature', []), output_signature=analysis_data.get('output_signature', []), dependencies=analysis_data.get('dependencies', []), complexity_score=float(analysis_data.get('complexity_score', 0.5)), reusability_score=float(analysis_data.get('reusability_score', 0.5)), llm_compatible=bool(analysis_data.get('llm_compatible', False)), agent_potential=analysis_data.get('agent_potential', 'low'), related_patterns=analysis_data.get('related_patterns', []))
    except Exception as e:
        print(f'❌ LLM analysis failed for {node.name}: {e}')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
