
class CodeRefactoringServiceAgent:
    """Agent based on CodeRefactoringService from ..\MAR-Multilateral Agentic Repo\admin\code_refactoring_service.py"""
    
    def __init__(self):
        self.name = "CodeRefactoringServiceAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Service for transforming discovered code into MAR-compatible agents"""
        self.mar_root = Path(mar_root)
        self.patterns_cache = {}
        self.agent_templates = self._load_agent_templates()
    def _load_agent_templates(self) -> Dict[str, str]:
        """Load agent code templates"""
    def analyze_code_patterns(self, discovered_metadata: List[Dict]) -> List[CodePattern]:
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
    def generate_agent_blueprint(self, patterns: List[CodePattern], agent_name: str) -> AgentBlueprint:
        """Generate agent blueprint from code patterns"""
        primary_pattern = max(patterns, key=lambda p: p.reusability_score)
        blueprint_prompt = f'\n        Create an agent blueprint from these code patterns:\n        \n        Primary Pattern: {primary_pattern.functionality_description}\n        Source: {primary_pattern.source_file}\n        \n        Additional Patterns:\n        {[p.functionality_description for p in patterns[1:]]}\n        \n        Generate:\n        1. Agent name and category\n        2. Core functionality description\n        3. Input schema (JSON schema format)\n        4. Output schema (JSON schema format)\n        5. Compatible LLMs\n        6. Test cases (3-5 examples)\n        \n        Agent should follow MAR methodology and be production-ready.\n        Return JSON format.\n        '
        blueprint_data = query_llm(blueprint_prompt, model='claude-3')
        blueprint_json = json.loads(blueprint_data.get('output', '{}'))
        return AgentBlueprint(agent_name=agent_name, agent_category=blueprint_json.get('category', 'utility'), core_functionality=blueprint_json.get('functionality', ''), input_schema=blueprint_json.get('input_schema', {}), output_schema=blueprint_json.get('output_schema', {}), dependencies=blueprint_json.get('dependencies', []), compatible_llms=blueprint_json.get('compatible_llms', ['gpt-4o']), source_patterns=patterns, generated_code='', test_cases=blueprint_json.get('test_cases', []))
    def generate_agent_code(self, blueprint: AgentBlueprint) -> str:
        """Generate complete agent code from blueprint"""
        extracted_logic = self._extract_core_logic(blueprint.source_patterns)
        primary_type = blueprint.source_patterns[0].pattern_type
        template_key = f'{primary_type}_agent' if f'{primary_type}_agent' in self.agent_templates else 'base_agent'
        agent_class_name = self._to_class_name(blueprint.agent_name)
        return code
    def _extract_core_logic(self, patterns: List[CodePattern]) -> Dict[str, str]:
        """Extract and refactor core logic from source patterns"""
        logic_prompt = f"\n        Extract and refactor the core logic from these code patterns for agent generation:\n        \n        Patterns:\n        {[{'file': p.source_file, 'function': p.source_function, 'type': p.pattern_type, 'description': p.functionality_description} for p in patterns]}\n        \n        Generate refactored code that:\n        1. Removes file I/O and makes it data-driven\n        2. Separates core logic from infrastructure\n        3. Makes it reusable and configurable\n        4. Follows clean code principles\n        \n        Return:\n        - core_logic: Main processing logic\n        - post_processing: Output formatting logic\n        - extracted_logic: Specific extracted patterns\n        - analysis_logic: Analysis-specific logic (if applicable)\n        - extraction_logic: Extraction-specific logic (if applicable)\n        \n        Return as JSON.\n        "
        result = query_llm(logic_prompt, model='claude-3')
        return json.loads(result.get('output', '{}'))
    def _to_class_name(self, agent_name: str) -> str:
        """Convert agent name to valid class name"""
        return ''.join((word.capitalize() for word in re.split('[_\\-\\s]+', agent_name)))
    def _generate_dataclass_fields(self, schema: Dict) -> str:
        """Generate dataclass fields from JSON schema"""
        if not schema.get('properties'):
            return 'data: Any'
        fields = []
        for field_name, field_def in schema['properties'].items():
            field_type = self._json_type_to_python_type(field_def.get('type', 'string'))
            required = field_name in schema.get('required', [])
            default = '' if required else ' = None'
            fields.append(f'    {field_name}: {field_type}{default}')
        return '\n'.join(fields)
    def _json_type_to_python_type(self, json_type: str) -> str:
        """Convert JSON schema type to Python type annotation"""
        type_mapping = {'string': 'str', 'integer': 'int', 'number': 'float', 'boolean': 'bool', 'array': 'List[Any]', 'object': 'Dict[str, Any]'}
        return type_mapping.get(json_type, 'Any')
    def create_agent_from_patterns(self, patterns: List[CodePattern], agent_name: str) -> AgentBlueprint:
        """Complete workflow: patterns -> blueprint -> code"""
        print(f"🔧 Creating agent '{agent_name}' from {len(patterns)} patterns...")
        blueprint = self.generate_agent_blueprint(patterns, agent_name)
        blueprint.generated_code = self.generate_agent_code(blueprint)
        self._save_agent(blueprint)
        return blueprint
    def _save_agent(self, blueprint: AgentBlueprint):
        """Save generated agent to MAR structure"""
        agent_dir = self.mar_root / 'agents' / blueprint.agent_category
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / f'{blueprint.agent_name}_agent.py'
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(blueprint.generated_code)
        prompt_dir = self.mar_root / 'shared' / 'prompts'
        prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = prompt_dir / f'{blueprint.agent_name}_prompt.txt'
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f'You are a {blueprint.core_functionality} agent.\n\n')
            f.write('Process the following input:\n{data}\n\n')
            f.write('Return structured output following the specified schema.')
        self._update_agent_registry(blueprint)
        print(f"✅ Agent '{blueprint.agent_name}' saved to {agent_file}")
    def _update_agent_registry(self, blueprint: AgentBlueprint):
        """Update the MAR agent registry with new agent"""
        registry_path = self.mar_root / 'configs' / 'agent_registry.json'
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = []
        agent_entry = {'name': f'{blueprint.agent_name}_agent', 'category': blueprint.agent_category, 'smart': True, 'compatible_llms': blueprint.compatible_llms, 'protocols': ['MCP', 'SCIP'], 'functionality': blueprint.core_functionality, 'generated_from': [p.source_file for p in blueprint.source_patterns], 'created_at': datetime.now().isoformat()}
        existing_idx = next((i for i, agent in enumerate(registry) if agent.get('name') == agent_entry['name']), None)
        if existing_idx is not None:
            registry[existing_idx] = agent_entry
        else:
            registry.append(agent_entry)
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
