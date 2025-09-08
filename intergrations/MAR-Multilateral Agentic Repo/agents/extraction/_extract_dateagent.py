
class _extract_dateAgent:
    """Agent based on _extract_date from ..\Nyxion\backend\integrations\google_search.py"""
    
    def __init__(self):
        self.name = "_extract_dateAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract published date from various sources"""
    if 'metatags' in data.get('pagemap', {}):
        metatags = data['pagemap']['metatags'][0] if data['pagemap']['metatags'] else {}
        date_fields = ['article:published_time', 'datePublished', 'publish_date', 'DC.date.issued', 'sailthru.date', 'parsely-pub-date']
        for field in date_fields:
            if field in metatags:
                return metatags[field]
    import re
    date_pattern = '\\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \\d{1,2}, \\d{4}\\b'
    match = re.search(date_pattern, self.snippet)
    if match:
        return match.group()
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
