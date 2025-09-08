
class to_search_stringAgent:
    """Agent based on to_search_string from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "to_search_stringAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Convert to search query string"""
    if not self.keywords:
        return ''
    result = self.keywords[0]
    for i, op in enumerate(self.operators):
        if i + 1 < len(self.keywords):
            if op == BooleanOperator.NOT:
                result += f' -{self.keywords[i + 1]}'
            else:
                result += f' {self.keywords[i + 1]}'
    return result
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
