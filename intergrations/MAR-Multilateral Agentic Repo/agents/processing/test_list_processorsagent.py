
class test_list_processorsAgent:
    """Agent based on test_list_processors from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\test_document_ai.py"""
    
    def __init__(self):
        self.name = "test_list_processorsAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Test listing all processors in the project"""
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
        parent = f'projects/{project_id}/locations/{location}'
        logger.info(f'Listing processors in: {parent}')
        processors = client.list_processors(parent=parent)
        processor_list = list(processors)
        logger.info(f'✅ Found {len(processor_list)} processors:')
        for processor in processor_list:
            logger.info(f"  - {processor.display_name} ({processor.type_}) - ID: {processor.name.split('/')[-1]}")
        return True
    except Exception as e:
        logger.error(f'❌ Failed to list processors: {e}')
        return False
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
