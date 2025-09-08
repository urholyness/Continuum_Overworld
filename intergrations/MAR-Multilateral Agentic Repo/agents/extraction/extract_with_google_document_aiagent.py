
class extract_with_google_document_aiAgent:
    """Agent based on extract_with_google_document_ai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_document_ai_extraction.py"""
    
    def __init__(self):
        self.name = "extract_with_google_document_aiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Use Google Document AI for proper PDF text extraction"""
    try:
        from google.cloud import documentai
        from google.oauth2 import service_account
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
        if not all([creds_path, project_id]):
            return {'success': False, 'error': 'Missing Google Cloud credentials or project ID', 'text': ''}
        print(f'🔧 Using Google Document AI...')
        print(f'   Project: {project_id}')
        print(f'   Location: {location}')
        print(f'   Credentials: {creds_path}')
        client = documentai.DocumentProcessorServiceClient()
        with open(pdf_path, 'rb') as f:
            document_content = f.read()
        name = f'projects/{project_id}/locations/{location}/processors/general'
        request = documentai.ProcessRequest(name=name, raw_document=documentai.RawDocument(content=document_content, mime_type='application/pdf'))
        print(f'🔄 Processing PDF with Google Document AI...')
        result = client.process_document(request=request)
        document = result.document
        full_text = document.text
        tables_text = ''
        for page in document.pages:
            for table in page.tables:
                tables_text += '\\n--- TABLE ---\\n'
                for row in table.header_rows + table.body_rows:
                    row_text = []
                    for cell in row.cells:
                        cell_text = ''.join([full_text[segment.start_index:segment.end_index] for segment in cell.layout.text_anchor.text_segments])
                        row_text.append(cell_text.strip())
                    tables_text += ' | '.join(row_text) + '\\n'
        combined_text = full_text
        if tables_text:
            combined_text += '\\n\\n=== STRUCTURED TABLES ===\\n' + tables_text
        return {'success': True, 'text': combined_text, 'pages': len(document.pages), 'method': 'Google_Document_AI', 'tables_found': len([table for page in document.pages for table in page.tables])}
    except ImportError:
        return {'success': False, 'error': 'Google Cloud Document AI library not installed', 'text': ''}
    except Exception as e:
        return {'success': False, 'error': f'Google Document AI failed: {str(e)}', 'text': ''}
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
