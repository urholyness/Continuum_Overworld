
class extract_text_fallbackAgent:
    """Agent based on extract_text_fallback from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "extract_text_fallbackAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
        Fallback text extraction using PyPDF2 and pdfplumber
        Args:
            pdf_content (bytes): PDF content
        Returns:
            Optional[str]: Extracted text or None if failed
        """
    try:
        with pdfplumber.open(BytesIO(pdf_content)) as pdf:
            text_parts = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            if text_parts:
                extracted_text = '\n'.join(text_parts)
                logger.info(f'pdfplumber extracted {len(extracted_text)} characters')
                return extracted_text
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        if text_parts:
            extracted_text = '\n'.join(text_parts)
            logger.info(f'PyPDF2 extracted {len(extracted_text)} characters')
            return extracted_text
    except Exception as e:
        logger.error(f'Error in fallback text extraction: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
