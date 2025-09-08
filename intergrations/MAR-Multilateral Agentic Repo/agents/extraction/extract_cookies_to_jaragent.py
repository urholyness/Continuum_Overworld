
class extract_cookies_to_jarAgent:
    """Agent based on extract_cookies_to_jar from ..\Nyxion\env\Lib\site-packages\pip\_vendor\requests\cookies.py"""
    
    def __init__(self):
        self.name = "extract_cookies_to_jarAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Extract the cookies from the response into a CookieJar.
    :param jar: http.cookiejar.CookieJar (not necessarily a RequestsCookieJar)
    :param request: our own requests.Request object
    :param response: urllib3.HTTPResponse object
    """
    if not (hasattr(response, '_original_response') and response._original_response):
        return
    req = MockRequest(request)
    res = MockResponse(response._original_response.msg)
    jar.extract_cookies(res, req)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
