
class test_kpi_extractorAgent:
    """Agent based on test_kpi_extractor from ..\Archieves\Stat-R_AI\esg_kpi_mvp\test_document_ai.py"""
    
    def __init__(self):
        self.name = "test_kpi_extractorAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Test the Document AI KPI Extractor"""
    try:
        print('\n⚙️  Testing Document AI KPI Extractor...')
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from kpi_extractor_document_ai import DocumentAIKPIExtractor
        extractor = DocumentAIKPIExtractor()
        print(f'   📊 Document AI enabled: {extractor.document_ai_enabled}')
        print(f'   🤖 Gemini enabled: {extractor.gemini_enabled}')
        if extractor.document_ai_enabled and extractor.gemini_enabled:
            print('   ✅ Full AI pipeline ready!')
            return True
        elif extractor.document_ai_enabled:
            print('   ⚠️  Document AI ready, Gemini needs configuration')
            return True
        else:
            print('   ❌ Document AI not available')
            return False
    except ImportError as e:
        print(f'   ❌ KPI Extractor import failed: {e}')
        return False
    except Exception as e:
        print(f'   ❌ KPI Extractor test failed: {e}')
        return False
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
