
class BrandBuzzServiceAgent:
    """Agent based on BrandBuzzService from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "BrandBuzzServiceAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Main service for Brand Buzz functionality"""
        self.query_builder = SearchQueryBuilder()
        self.preset_themes = {'trust': KeywordCombination(keywords=['trust', 'reliable', 'credibility', 'reputation'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR]), 'scandal': KeywordCombination(keywords=['scandal', 'controversy', 'investigation', 'allegation'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR]), 'quality': KeywordCombination(keywords=['quality', 'defect', 'recall', 'complaint'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR]), 'environment': KeywordCombination(keywords=['pollution', 'emissions', 'environmental', 'sustainability'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR]), 'fraud': KeywordCombination(keywords=['fraud', 'scam', 'deception', 'misleading'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR]), 'safety': KeywordCombination(keywords=['injury', 'accident', 'danger', 'hazard', 'safety'], operators=[BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR, BooleanOperator.OR])}
    def get_preset_themes(self) -> Dict[str, KeywordCombination]:
        """Get available preset themes"""
        return self.preset_themes
    def create_custom_combination(self, keywords: List[str], operator_type: BooleanOperator=BooleanOperator.OR) -> KeywordCombination:
        """Create a custom keyword combination with same operator throughout"""
        if len(keywords) <= 1:
            return KeywordCombination(keywords=keywords, operators=[])
        operators = [operator_type] * (len(keywords) - 1)
        return KeywordCombination(keywords=keywords, operators=operators)
    def create_complex_combination(self, keyword_operator_pairs: List[Tuple[str, Optional[BooleanOperator]]]) -> KeywordCombination:
        """Create a complex keyword combination with different operators"""
        keywords = []
        operators = []
        for i, (keyword, operator) in enumerate(keyword_operator_pairs):
            keywords.append(keyword)
            if operator and i < len(keyword_operator_pairs) - 1:
                operators.append(operator)
        return KeywordCombination(keywords=keywords, operators=operators)
    def validate_search_configuration(self, config: SearchConfiguration) -> Tuple[bool, List[str]]:
        """Validate search configuration and return errors if any"""
        errors = []
        if not config.brands:
            errors.append('At least one brand must be specified')
        elif len(config.brands) > 50:
            errors.append('Maximum 50 brands allowed per search')
        if not config.keyword_combinations:
            errors.append('At least one keyword combination must be specified')
        if not config.source_types:
            errors.append('At least one source type must be selected')
        if config.time_period_days < 1 or config.time_period_days > 365:
            errors.append('Time period must be between 1 and 365 days')
        if config.search_depth < 1 or config.search_depth > 50:
            errors.append('Search depth must be between 1 and 50 results per query')
        return (len(errors) == 0, errors)
    def estimate_search_cost(self, config: SearchConfiguration) -> Dict[str, Any]:
        """Estimate the cost of running a search"""
        total_queries = len(config.brands) * len(config.keyword_combinations) * len(config.source_types)
        total_results = total_queries * config.search_depth
        google_search_cost = total_queries * 0.005
        llm_analysis_cost = total_results * 0.002
        return {'total_queries': total_queries, 'total_results': total_results, 'estimated_google_cost': round(google_search_cost, 2), 'estimated_llm_cost': round(llm_analysis_cost, 2), 'total_estimated_cost': round(google_search_cost + llm_analysis_cost, 2), 'estimated_time_minutes': max(1, total_results // 60)}
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
