
class test_processor_accessAgent:
    """Agent based on test_processor_access from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\test_document_ai.py"""
    
    def __init__(self):
        self.name = "test_processor_accessAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Test access to the configured processor"""
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
        processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
        processor_name = f'projects/{project_id}/locations/{location}/processors/{processor_id}'
        logger.info(f'Testing processor access: {processor_name}')
        processor = client.get_processor(name=processor_name)
        logger.info(f'✅ Processor found:')
        logger.info(f'  Name: {processor.display_name}')
        logger.info(f'  Type: {processor.type_}')
        logger.info(f'  State: {processor.state}')
        logger.info(f'  Create Time: {processor.create_time}')
        return True
    except Exception as e:
        logger.error(f'❌ Failed to access processor: {e}')
        logger.error('Possible issues:')
        logger.error('  1. Document AI API not enabled in Google Cloud Console')
        logger.error('  2. Incorrect processor ID or location')
        logger.error('  3. Service account lacks Document AI permissions')
        logger.error('  4. Project ID mismatch')
        return False
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
