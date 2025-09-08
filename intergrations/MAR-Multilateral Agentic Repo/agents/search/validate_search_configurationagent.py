
class validate_search_configurationAgent:
    """Agent based on validate_search_configuration from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "validate_search_configurationAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
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
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
