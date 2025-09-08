
class TestCurveSearchingAgent:
    """Agent based on TestCurveSearching from ..\Nyxion\env\Lib\site-packages\ecdsa\test_curves.py"""
    
    def __init__(self):
        self.name = "TestCurveSearchingAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            def test_correct_name(self):
        c = curve_by_name('NIST256p')
        self.assertIs(c, NIST256p)
    def test_openssl_name(self):
        c = curve_by_name('prime256v1')
        self.assertIs(c, NIST256p)
    def test_unknown_curve(self):
        with self.assertRaises(UnknownCurveError) as e:
            curve_by_name('foo bar')
        self.assertIn("name 'foo bar' unknown, only curves supported: ['NIST192p', 'NIST224p'", str(e.exception))
    def test_with_None_as_parameter(self):
        with self.assertRaises(UnknownCurveError) as e:
            curve_by_name(None)
        self.assertIn("name None unknown, only curves supported: ['NIST192p', 'NIST224p'", str(e.exception))
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
