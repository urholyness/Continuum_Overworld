
class extract_text_document_aiAgent:
    """Agent based on extract_text_document_ai from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "extract_text_document_aiAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Extract text from PDF using Google Document AI with page chunking
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text or None if failed
        """
    if not self.document_ai_client:
        logger.warning('Document AI client not available')
    try:
        document = {'content': pdf_content, 'mime_type': 'application/pdf'}
        request = {'name': self.processor_name, 'raw_document': document}
        result = self.document_ai_client.process_document(request=request)
        text = result.document.text
        logger.info(f'Document AI extracted {len(text)} characters from full document')
        return text
    except GoogleAPIError as e:
        if 'PAGE_LIMIT_EXCEEDED' in str(e):
            logger.warning(f'Document exceeds page limit, attempting chunked processing: {e}')
            return self._extract_text_document_ai_chunked(pdf_content)
        else:
            logger.error(f'Google Document AI error: {e}')
    except Exception as e:
        logger.error(f'Error processing document with Document AI: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
