
class scan_projectsAgent:
    """Agent based on scan_projects from ..\MAR-Multilateral Agentic Repo\real_agent_generator.py"""
    
    def __init__(self):
        self.name = "scan_projectsAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
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
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
