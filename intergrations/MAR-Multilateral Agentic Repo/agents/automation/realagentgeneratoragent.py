
class RealAgentGeneratorAgent:
    """Agent based on RealAgentGenerator from ..\MAR-Multilateral Agentic Repo\real_agent_generator.py"""
    
    def __init__(self):
        self.name = "RealAgentGeneratorAgent"
        self.category = "automation"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Actually scans projects and generates agents"""
        self.projects_root = Path(projects_root)
        self.discovered_patterns: List[CodePattern] = []
        self.generated_agents: List[GeneratedAgent] = []
        self.agent_templates = self._load_agent_templates()
    def _load_agent_templates(self) -> Dict[str, str]:
        """Load agent templates"""
    def scan_projects(self) -> List[CodePattern]:
        """Actually scan the projects folder for code patterns"""
        logger.info(f'Scanning projects in: {self.projects_root}')
        patterns = []
        patterns_of_interest = ['class.*Agent.*:', 'class.*Search.*:', 'class.*Extract.*:', 'class.*Process.*:', 'def.*search.*:', 'def.*extract.*:', 'def.*process.*:', 'def.*analyze.*:', 'def.*discover.*:']
        for py_file in self.projects_root.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        node_code = ast.unparse(node)
                        for pattern in patterns_of_interest:
                            if re.search(pattern, node_code, re.IGNORECASE):
                                pattern_obj = self._analyze_pattern(node, node_code, py_file)
                                if pattern_obj:
                                    patterns.append(pattern_obj)
                                break
            except Exception as e:
                logger.warning(f'Error parsing {py_file}: {e}')
        self.discovered_patterns = patterns
        logger.info(f'Discovered {len(patterns)} code patterns')
        return patterns
    def _analyze_pattern(self, node: ast.AST, source_code: str, file_path: Path) -> Optional[CodePattern]:
        """Analyze a code pattern for agent potential"""
        try:
            if isinstance(node, ast.ClassDef):
                pattern_type = 'class'
                name = node.name
            else:
                pattern_type = 'function'
                name = node.name
            dependencies = self._extract_dependencies(source_code)
            complexity = len(source_code.split('\n'))
            reusability = self._calculate_reusability(source_code, dependencies)
            agent_potential = self._determine_agent_potential(name, source_code, dependencies)
            return CodePattern(name=name, file_path=str(file_path), pattern_type=pattern_type, source_code=source_code, dependencies=dependencies, complexity=complexity, reusability=reusability, agent_potential=agent_potential)
        except Exception as e:
            logger.warning(f'Error analyzing pattern: {e}')
    def _extract_dependencies(self, source_code: str) -> List[str]:
        """Extract dependencies from source code"""
        dependencies = []
        agent_libs = ['requests', 'httpx', 'aiohttp', 'pandas', 'numpy', 'polars', 'openai', 'anthropic', 'langchain', 'beautifulsoup4', 'selenium', 'sqlalchemy', 'psycopg2', 'pydantic', 'dataclasses', 'asyncio', 'threading', 'logging', 'json', 'yaml']
        for lib in agent_libs:
            if lib in source_code.lower():
                dependencies.append(lib)
        return dependencies
    def _calculate_reusability(self, source_code: str, dependencies: List[str]) -> float:
        """Calculate reusability score (0.0-1.0)"""
        score = 0.0
        score += min(len(dependencies) * 0.1, 0.3)
        lines = len(source_code.split('\n'))
        score += min(lines * 0.01, 0.3)
        generic_patterns = ['def', 'class', 'return', 'if', 'for', 'while']
        for pattern in generic_patterns:
            if pattern in source_code:
                score += 0.05
        return min(score, 1.0)
    def _determine_agent_potential(self, name: str, source_code: str, dependencies: List[str]) -> str:
        """Determine agent potential"""
        score = 0
        agent_keywords = ['agent', 'search', 'extract', 'process', 'analyze', 'discover']
        for keyword in agent_keywords:
            if keyword.lower() in name.lower():
                score += 2
        score += len(dependencies)
        lines = len(source_code.split('\n'))
        if lines > 20:
            score += 2
        elif lines > 10:
            score += 1
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'
    def generate_agents(self) -> List[GeneratedAgent]:
        """Generate agents from discovered patterns"""
        logger.info('Generating agents from discovered patterns...')
        agents = []
        for pattern in self.discovered_patterns:
            if pattern.agent_potential in ['high', 'medium']:
                agent = self._create_agent_from_pattern(pattern)
                if agent:
                    agents.append(agent)
        self.generated_agents = agents
        logger.info(f'Generated {len(agents)} agents')
        return agents
    def _create_agent_from_pattern(self, pattern: CodePattern) -> Optional[GeneratedAgent]:
        """Create an agent from a code pattern"""
        try:
            category = self._determine_category(pattern)
            agent_name = f'{pattern.name}Agent'
            template_key = self._choose_template(pattern)
            template = self.agent_templates[template_key]
            agent_code = template.format(agent_name=agent_name, description=f'Agent based on {pattern.name} from {pattern.file_path}', category=category, original_logic=self._extract_core_logic(pattern.source_code))
            agent_dir = Path('agents') / category
            agent_dir.mkdir(parents=True, exist_ok=True)
            agent_file = agent_dir / f'{agent_name.lower()}.py'
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(agent_code)
            init_file = agent_dir / '__init__.py'
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(f'from .{agent_name.lower()} import {agent_name}\n')
            return GeneratedAgent(name=agent_name, category=category, source_pattern=pattern.name, file_path=str(agent_file), dependencies=pattern.dependencies, status='generated')
        except Exception as e:
            logger.error(f'Error creating agent from pattern {pattern.name}: {e}')
    def _determine_category(self, pattern: CodePattern) -> str:
        """Determine agent category based on pattern"""
        name_lower = pattern.name.lower()
        source_lower = pattern.source_code.lower()
        if any((word in name_lower for word in ['search', 'discover', 'find'])):
            return 'search'
        elif any((word in name_lower for word in ['extract', 'parse', 'scrape'])):
            return 'extraction'
        elif any((word in name_lower for word in ['process', 'analyze', 'transform'])):
            return 'processing'
        elif any((word in name_lower for word in ['agent', 'bot', 'automation'])):
            return 'automation'
        else:
            return 'utility'
    def _choose_template(self, pattern: CodePattern) -> str:
        """Choose appropriate template for pattern"""
        name_lower = pattern.name.lower()
        if any((word in name_lower for word in ['search', 'discover', 'find'])):
            return 'search_agent'
        elif any((word in name_lower for word in ['extract', 'parse', 'scrape'])):
            return 'extractor_agent'
        else:
            return 'base_agent'
    def _extract_core_logic(self, source_code: str) -> str:
        """Extract core logic from source code"""
        lines = source_code.split('\n')
        if lines:
            lines = lines[1:]
        core_lines = []
        for line in lines:
            if line.strip() and (not line.startswith('"""')) and (not line.startswith("'''")):
                    core_lines.append(line)
    def save_results(self):
        """Save discovery and generation results"""
        with open('discovered_patterns.json', 'w', encoding='utf-8') as f:
            json.dump([asdict(p) for p in self.discovered_patterns], f, indent=2)
        with open('generated_agents.json', 'w', encoding='utf-8') as f:
            json.dump([asdict(a) for a in self.generated_agents], f, indent=2)
        logger.info('Results saved to discovered_patterns.json and generated_agents.json')
    def run(self):
        """Run the complete agent generation process"""
        logger.info('Starting real agent generation process...')
        patterns = self.scan_projects()
        agents = self.generate_agents()
        self.save_results()
        print(f"\n{'=' * 50}")
        print(f'AGENT GENERATION COMPLETE')
        print(f"{'=' * 50}")
        print(f'Scanned projects: {self.projects_root}')
        print(f'Discovered patterns: {len(patterns)}')
        print(f'Generated agents: {len(agents)}')
        print(f'\nGenerated Agents:')
        for agent in agents:
            print(f'  - {agent.name} ({agent.category}) from {agent.source_pattern}')
        print(f"{'=' * 50}")
        return agents
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
