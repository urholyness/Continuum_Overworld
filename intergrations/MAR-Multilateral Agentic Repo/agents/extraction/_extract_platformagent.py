
class _extract_platformAgent:
    """Agent based on _extract_platform from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\survey_automation.py"""
    
    def __init__(self):
        self.name = "_extract_platformAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract platform name from URL"""
    if 'linkedin.com' in url:
        return 'linkedin'
    elif 'reddit.com' in url:
        return 'reddit'
    elif 'twitter.com' in url:
        return 'twitter'
    else:
        return 'other'
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
