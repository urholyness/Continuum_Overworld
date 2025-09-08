
class SubprocessMixinAgent:
    """Agent based on SubprocessMixin from ..\Nyxion\env\Lib\site-packages\pip\_vendor\distlib\util.py"""
    
    def __init__(self):
        self.name = "SubprocessMixinAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Mixin for running subprocesses and capturing their output
    """
        self.verbose = verbose
        self.progress = progress
    def reader(self, stream, context):
        """
        callable (if specified) or write progress information to sys.stderr.
        """
        progress = self.progress
        verbose = self.verbose
        while True:
            s = stream.readline()
            if not s:
                break
            if progress is not None:
                progress(s, context)
            else:
                if not verbose:
                    sys.stderr.write('.')
                else:
                    sys.stderr.write(s.decode('utf-8'))
                sys.stderr.flush()
        stream.close()
    def run_command(self, cmd, **kwargs):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        t1 = threading.Thread(target=self.reader, args=(p.stdout, 'stdout'))
        t1.start()
        t2 = threading.Thread(target=self.reader, args=(p.stderr, 'stderr'))
        t2.start()
        p.wait()
        t1.join()
        t2.join()
        if self.progress is not None:
            self.progress('done.', 'main')
        elif self.verbose:
            sys.stderr.write('done.\n')
        return p
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
