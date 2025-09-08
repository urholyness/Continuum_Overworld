
class extract_domainAgent:
    """Agent based on extract_domain from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "extract_domainAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ''
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
