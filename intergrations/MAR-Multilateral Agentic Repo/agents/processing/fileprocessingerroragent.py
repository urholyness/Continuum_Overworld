
class FileProcessingErrorAgent:
    """Agent based on FileProcessingError from ..\Nyxion\backend\utils\exceptions.py"""
    
    def __init__(self):
        self.name = "FileProcessingErrorAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """File processing error"""
        super().__init__(message=f'File processing error: {message}', error_code='FILE_PROCESSING_ERROR', status_code=422, details=details)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
