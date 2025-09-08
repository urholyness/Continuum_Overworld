
class GoogleSearchResultAgent:
    """Agent based on GoogleSearchResult from ..\Nyxion\backend\integrations\google_search.py"""
    
    def __init__(self):
        self.name = "GoogleSearchResultAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Represents a single search result"""
        self.title = data.get('title', '')
        self.link = data.get('link', '')
        self.snippet = data.get('snippet', '')
        self.display_link = data.get('displayLink', '')
        self.mime_type = data.get('mime', '')
        self.published_date = self._extract_date(data)
        self.pagemap = data.get('pagemap', {})
    def _extract_date(self, data: Dict[str, Any]) -> Optional[str]:
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
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {'title': self.title, 'link': self.link, 'snippet': self.snippet, 'display_link': self.display_link, 'published_date': self.published_date, 'mime_type': self.mime_type}
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
