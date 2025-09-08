
class _extract_file_contentAgent:
    """Agent based on _extract_file_content from ..\Rank_AI\02_report_acquisition\ai_multi_validator.py"""
    
    def __init__(self):
        self.name = "_extract_file_contentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract content from file for AI analysis"""
    file_ext = file_path.split('.')[-1].lower()
    try:
        if file_ext == 'pdf':
            return self._extract_pdf_content(file_path)
        elif file_ext in ['html', 'htm']:
            return self._extract_html_content(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(3000)
                return (content, 'plain_text_read')
    except Exception as e:
        return (f'Content extraction failed: {str(e)}', 'extraction_error')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
