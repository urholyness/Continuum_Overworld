
class AgentGenerationOrchestratorAgent:
    """Agent based on AgentGenerationOrchestrator from ..\MAR-Multilateral Agentic Repo\admin\agent_generation_orchestrator.py"""
    
    def __init__(self):
        self.name = "AgentGenerationOrchestratorAgent"
        self.category = "automation"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Main orchestrator for automated agent generation from codebase scanning
    Implements the full MAR vision: scan -> analyze -> refactor -> generate
    """
        self.projects_root = Path(projects_root)
        self.mar_root = Path(mar_root)
        self.omen_agent = OmenAgent(root_dir=str(self.projects_root), output_dir=str(self.mar_root / 'agents' / 'assets'))
        self.refactoring_service = CodeRefactoringService(str(self.mar_root))
        self.session_log = []
        self.generated_agents = []
    def run_full_pipeline(self, auto_generate: bool=False, max_agents: int=5) -> Dict[str, Any]:
        """
        Execute the complete agent generation pipeline
        Args:
            auto_generate: If True, automatically generates agents from suggestions
            max_agents: Maximum number of agents to generate in one run
        Returns:
            Pipeline execution results
        """
        session_start = datetime.now()
        print('🌟 Starting MAR Agent Generation Pipeline...')
        results = {'session_start': session_start.isoformat(), 'discoveries': [], 'suggestions': [], 'generated_agents': [], 'errors': [], 'stats': {}}
        try:
            print('\n📡 Phase 1: Code Discovery & Analysis')
            discovery_results = self.omen_agent.run()
            results['discoveries'] = [d.__dict__ if hasattr(d, '__dict__') else d for d in discovery_results['discoveries']]
            results['suggestions'] = discovery_results['suggestions']
            print('\n🔍 Phase 2: Pattern Analysis & Conversion')
            patterns = self._convert_discoveries_to_patterns(discovery_results['discoveries'])
            if auto_generate and results['suggestions']:
                print(f'\n🤖 Phase 3: Auto-generating up to {max_agents} agents...')
                generated_agents = self._auto_generate_agents(results['suggestions'][:max_agents], patterns)
                results['generated_agents'] = generated_agents
            print('\n📋 Phase 4: Summary & Recommendations')
            results['stats'] = self._generate_session_stats(results)
            self._print_pipeline_summary(results)
        except Exception as e:
            error_msg = f'Pipeline failed: {str(e)}'
            print(f'❌ {error_msg}')
            results['errors'].append(error_msg)
        self._save_session_results(results)
        return results
    def _convert_discoveries_to_patterns(self, discoveries: List[CodeDiscovery]) -> List[CodePattern]:
        """Convert Omen discoveries to refactoring service patterns"""
        patterns = []
        for discovery in discoveries:
            if isinstance(discovery, dict):
                pattern = CodePattern(pattern_id=discovery.get('id', ''), pattern_type=discovery.get('functionality_type', 'other'), source_file=discovery.get('file', ''), source_function=discovery.get('name', ''), functionality_description=discovery.get('doc', ''), input_types=discovery.get('input_signature', []), output_types=discovery.get('output_signature', []), dependencies=discovery.get('dependencies', []), complexity_score=discovery.get('complexity_score', 0.5), reusability_score=discovery.get('reusability_score', 0.5))
            else:
                pattern = CodePattern(pattern_id=discovery.id, pattern_type=discovery.functionality_type, source_file=discovery.file, source_function=discovery.name, functionality_description=discovery.doc, input_types=discovery.input_signature, output_types=discovery.output_signature, dependencies=discovery.dependencies, complexity_score=discovery.complexity_score, reusability_score=discovery.reusability_score)
            patterns.append(pattern)
        return patterns
    def _auto_generate_agents(self, suggestions: List[Dict], patterns: List[CodePattern]) -> List[Dict[str, Any]]:
        """Automatically generate agents from top suggestions"""
        generated_agents = []
        for suggestion in suggestions:
            try:
                agent_name = suggestion['suggested_agent_name']
                func_type = suggestion['functionality_type']
                matching_patterns = [p for p in patterns if p.pattern_type == func_type]
                if matching_patterns:
                    print(f'   🔧 Generating {agent_name}...')
                    blueprint = self.refactoring_service.create_agent_from_patterns(matching_patterns[:3], agent_name.replace('_agent', ''))
                    generated_agents.append({'agent_name': blueprint.agent_name, 'category': blueprint.agent_category, 'functionality': blueprint.core_functionality, 'source_patterns': len(blueprint.source_patterns), 'compatible_llms': blueprint.compatible_llms, 'generated_at': datetime.now().isoformat()})
                    print(f'   ✅ Generated {agent_name} successfully')
            except Exception as e:
                error_msg = f"Failed to generate {suggestion.get('suggested_agent_name', 'unknown')}: {str(e)}"
                print(f'   ❌ {error_msg}')
        return generated_agents
    def _generate_session_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate session statistics"""
        return {'total_discoveries': len(results['discoveries']), 'high_potential_discoveries': len([d for d in results['discoveries'] if d.get('agent_potential') == 'high']), 'agent_suggestions': len(results['suggestions']), 'agents_generated': len(results['generated_agents']), 'errors_encountered': len(results['errors']), 'success_rate': len(results['generated_agents']) / max(len(results['suggestions']), 1) * 100}
    def _print_pipeline_summary(self, results: Dict[str, Any]):
        """Print comprehensive pipeline summary"""
        stats = results['stats']
        print(f'\n🎯 MAR Agent Generation Pipeline - Session Complete')
        print(f'=' * 60)
        print(f"📊 Discoveries:     {stats['total_discoveries']} total, {stats['high_potential_discoveries']} high-potential")
        print(f"💡 Suggestions:     {stats['agent_suggestions']} agent suggestions generated")
        print(f"🤖 Agents Created:  {stats['agents_generated']} agents successfully generated")
        print(f"🎯 Success Rate:    {stats['success_rate']:.1f}%")
        if results['errors']:
            print(f"⚠️  Errors:         {stats['errors_encountered']} errors encountered")
        if results['generated_agents']:
            print(f'\n🚀 Generated Agents:')
            for agent in results['generated_agents']:
                print(f"   • {agent['agent_name']} ({agent['category']}) - {agent['source_patterns']} patterns")
        print(f'\n💾 Session data saved to MAR admin directory')
        print(f'🔗 Check the agents/ directory for new agent files')
    def _save_session_results(self, results: Dict[str, Any]):
        """Save session results for future reference"""
        session_file = self.mar_root / 'admin' / f"generation_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        serializable_results = self._make_serializable(results)
        with open(session_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        print(f'📝 Session results saved to {session_file}')
    def _make_serializable(self, obj):
        """Make object JSON serializable"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        else:
            return obj
    def generate_specific_agent(self, agent_name: str, functionality_types: List[str]) -> Optional[AgentBlueprint]:
        """Generate a specific agent by functionality types"""
        print(f'🎯 Generating specific agent: {agent_name}')
        if not hasattr(self.omen_agent, 'collected') or not self.omen_agent.collected:
            print('   🔍 Running code discovery first...')
            self.omen_agent.run()
        patterns = self._convert_discoveries_to_patterns(self.omen_agent.collected)
        matching_patterns = [p for p in patterns if p.pattern_type in functionality_types]
        if not matching_patterns:
            print(f'   ❌ No patterns found for functionality types: {functionality_types}')
        print(f'   🔧 Found {len(matching_patterns)} matching patterns')
        try:
            blueprint = self.refactoring_service.create_agent_from_patterns(matching_patterns, agent_name)
            print(f'   ✅ Successfully generated {agent_name}')
            return blueprint
        except Exception as e:
            print(f'   ❌ Failed to generate {agent_name}: {str(e)}')
    def list_available_patterns(self) -> Dict[str, List[str]]:
        """List all available patterns by functionality type"""
        if not hasattr(self.omen_agent, 'collected') or not self.omen_agent.collected:
            print('🔍 Running code discovery...')
            self.omen_agent.run()
        patterns_by_type = {}
        for discovery in self.omen_agent.collected:
            func_type = discovery.functionality_type if hasattr(discovery, 'functionality_type') else discovery.get('functionality_type', 'other')
            if func_type not in patterns_by_type:
                patterns_by_type[func_type] = []
            pattern_info = {'name': discovery.name if hasattr(discovery, 'name') else discovery.get('name'), 'file': discovery.file if hasattr(discovery, 'file') else discovery.get('file'), 'reusability': discovery.reusability_score if hasattr(discovery, 'reusability_score') else discovery.get('reusability_score', 0.5)}
            patterns_by_type[func_type].append(pattern_info)
        return patterns_by_type
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
