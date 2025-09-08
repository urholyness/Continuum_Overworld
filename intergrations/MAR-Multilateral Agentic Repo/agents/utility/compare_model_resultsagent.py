
class compare_model_resultsAgent:
    """Agent based on compare_model_results from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_document_ai_extraction.py"""
    
    def __init__(self):
        self.name = "compare_model_resultsAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Compare results from different AI models and pick best"""
    print(f'\\n🔍 COMPARING RESULTS FROM {len(results_list)} MODELS:')
    all_extractions = []
    for result in results_list:
        if result['success']:
            model_name = result.get('model_used', 'unknown')
            extractions = result.get('extractions', [])
            found_count = len([e for e in extractions if e.get('found')])
            print(f'   {model_name}: {found_count} KPIs found')
            for extraction in extractions:
                extraction['model_source'] = model_name
                all_extractions.append(extraction)
        else:
            model_name = result.get('model_used', 'unknown')
            print(f"   {model_name}: FAILED - {result.get('error', 'Unknown error')}")
    kpi_groups = {}
    for extraction in all_extractions:
        if extraction.get('found'):
            kpi_name = extraction.get('kpi_name')
            if kpi_name not in kpi_groups:
                kpi_groups[kpi_name] = []
            kpi_groups[kpi_name].append(extraction)
    best_extractions = []
    for kpi_name, extractions in kpi_groups.items():
        if extractions:
            model_scores = {'gpt-4': 3, 'gemini-pro': 2, 'gpt-3.5-turbo': 1}
            def score_extraction(ext):
                confidence = ext.get('confidence', 0)
                model_bonus = model_scores.get(ext.get('model_source', ''), 0) * 5
                return confidence + model_bonus
            best = max(extractions, key=score_extraction)
            best_extractions.append(best)
    return best_extractions
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
