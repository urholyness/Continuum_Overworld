
class _extract_text_document_ai_chunkedAgent:
    """Agent based on _extract_text_document_ai_chunked from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_extract_text_document_ai_chunkedAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Extract text from large PDF using Document AI with page chunking
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text from all chunks combined
        """
    try:
        import PyPDF2
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
        total_pages = len(pdf_reader.pages)
        logger.info(f'Processing {total_pages} pages in chunks of 25 pages')
        all_text = []
        chunk_size = 25
        for start_page in range(0, total_pages, chunk_size):
            end_page = min(start_page + chunk_size, total_pages)
            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            chunk_buffer = BytesIO()
            pdf_writer.write(chunk_buffer)
            chunk_content = chunk_buffer.getvalue()
            chunk_buffer.close()
            logger.info(f'Processing pages {start_page + 1}-{end_page} with Document AI')
            document = {'content': chunk_content, 'mime_type': 'application/pdf'}
            request = {'name': self.processor_name, 'raw_document': document}
            result = self.document_ai_client.process_document(request=request)
            chunk_text = result.document.text
            if chunk_text:
                all_text.append(chunk_text)
                logger.info(f'Extracted {len(chunk_text)} characters from pages {start_page + 1}-{end_page}')
        combined_text = '\n\n--- PAGE BREAK ---\n\n'.join(all_text)
        logger.info(f'Document AI chunked processing completed: {len(combined_text)} total characters')
        return combined_text
    except Exception as e:
        logger.error(f'Error in chunked Document AI processing: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
