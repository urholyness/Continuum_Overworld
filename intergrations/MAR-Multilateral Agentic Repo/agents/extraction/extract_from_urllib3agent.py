
class extract_from_urllib3Agent:
    """Agent based on extract_from_urllib3 from ..\Nyxion\env\Lib\site-packages\pip\_vendor\urllib3\contrib\securetransport.py"""
    
    def __init__(self):
        self.name = "extract_from_urllib3Agent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """
    Undo monkey-patching by :func:`inject_into_urllib3`.
    """
    util.SSLContext = orig_util_SSLContext
    util.ssl_.SSLContext = orig_util_SSLContext
    util.HAS_SNI = orig_util_HAS_SNI
    util.ssl_.HAS_SNI = orig_util_HAS_SNI
    util.IS_SECURETRANSPORT = False
    util.ssl_.IS_SECURETRANSPORT = False
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
