
class SearchConfigurationAgent:
    """Agent based on SearchConfiguration from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "SearchConfigurationAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
        class SearchConfiguration:
    """Complete search configuration for Brand Buzz"""
    brands: List[str]
    keyword_combinations: List[KeywordCombination]
    source_types: List[SourceType]
    time_period_days: int
    search_depth: int
    include_negative_keywords: bool = True
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {'brands': self.brands, 'keyword_combinations': [{'keywords': kc.keywords, 'operators': [op.value for op in kc.operators]} for kc in self.keyword_combinations], 'source_types': [st.value for st in self.source_types], 'time_period_days': self.time_period_days, 'search_depth': self.search_depth, 'include_negative_keywords': self.include_negative_keywords}
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchConfiguration':
        """Create from dictionary"""
        keyword_combinations = []
        for kc_data in data.get('keyword_combinations', []):
            keyword_combinations.append(KeywordCombination(keywords=kc_data['keywords'], operators=[BooleanOperator(op) for op in kc_data.get('operators', [])]))
        return cls(brands=data['brands'], keyword_combinations=keyword_combinations, source_types=[SourceType(st) for st in data['source_types']], time_period_days=data['time_period_days'], search_depth=data['search_depth'], include_negative_keywords=data.get('include_negative_keywords', True))
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
