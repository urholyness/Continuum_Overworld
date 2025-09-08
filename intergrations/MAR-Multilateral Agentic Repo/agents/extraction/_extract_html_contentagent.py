
class _extract_html_contentAgent:
    """Agent based on _extract_html_content from ..\Rank_AI\02_report_acquisition\ai_report_downloader.py"""
    
    def __init__(self):
        self.name = "_extract_html_contentAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract readable text content from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read(5000)
        cleaned_text = ''
        in_tag = False
        for char in html_content:
            if char == '<':
                in_tag = True
            elif char == '>':
                in_tag = False
            elif not in_tag:
                cleaned_text += char
        lines = []
        for line in cleaned_text.split('\n'):
            line = line.strip()
            if line and len(line) > 3:
                lines.append(line)
        cleaned_content = '\n'.join(lines[:50])
        if cleaned_content.strip():
            return (cleaned_content[:2000], 'html_text_extraction')
        else:
            return (f'HTML file detected but no readable text content found', 'html_no_text')
    except Exception as e:
        return (f'HTML extraction error: {str(e)}', 'html_extraction_error')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
