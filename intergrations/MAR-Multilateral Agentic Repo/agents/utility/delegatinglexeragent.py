
class DelegatingLexerAgent:
    """Agent based on DelegatingLexer from ..\Nyxion\env\Lib\site-packages\pip\_vendor\pygments\lexer.py"""
    
    def __init__(self):
        self.name = "DelegatingLexerAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    This lexer takes two lexer as arguments. A root lexer and
    a language lexer. First everything is scanned using the language
    lexer, afterwards all ``Other`` tokens are lexed using the root
    lexer.
    The lexers from the ``template`` lexer package use this base lexer.
    """
        self.root_lexer = _root_lexer(**options)
        self.language_lexer = _language_lexer(**options)
        self.needle = _needle
        Lexer.__init__(self, **options)
    def get_tokens_unprocessed(self, text):
        buffered = ''
        insertions = []
        lng_buffer = []
        for i, t, v in self.language_lexer.get_tokens_unprocessed(text):
            if t is self.needle:
                if lng_buffer:
                    insertions.append((len(buffered), lng_buffer))
                    lng_buffer = []
                buffered += v
            else:
                lng_buffer.append((i, t, v))
        if lng_buffer:
            insertions.append((len(buffered), lng_buffer))
        return do_insertions(insertions, self.root_lexer.get_tokens_unprocessed(buffered))
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
