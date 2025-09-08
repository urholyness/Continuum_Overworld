
class KeywordCombinationAgent:
    """Agent based on KeywordCombination from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "KeywordCombinationAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
        class KeywordCombination:
    """Represents a keyword combination with operators"""
    keywords: List[str]
    operators: List[BooleanOperator]
    def to_search_string(self) -> str:
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
    def to_google_query(self) -> str:
        """Convert to Google search query format"""
        if not self.keywords:
            return ''
        parts = []
        i = 0
        while i < len(self.keywords):
            keyword = f'"{self.keywords[i]}"'
            if i < len(self.operators):
                if self.operators[i] == BooleanOperator.NOT:
                    keyword = f'-{keyword}'
                elif self.operators[i] == BooleanOperator.OR and i + 1 < len(self.keywords):
                    next_keyword = f'"{self.keywords[i + 1]}"'
                    parts.append(f'({keyword} OR {next_keyword})')
                    i += 2
                    continue
            parts.append(keyword)
            i += 1
        return ' '.join(parts)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
