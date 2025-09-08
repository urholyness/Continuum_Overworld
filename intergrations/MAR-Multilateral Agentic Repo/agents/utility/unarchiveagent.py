
class unarchiveAgent:
    """Agent based on unarchive from ..\Nyxion\env\Lib\site-packages\pip\_vendor\distlib\util.py"""
    
    def __init__(self):
        self.name = "unarchiveAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            def check_path(path):
        if not isinstance(path, text_type):
            path = path.decode('utf-8')
        p = os.path.abspath(os.path.join(dest_dir, path))
        if not p.startswith(dest_dir) or p[plen] != os.sep:
            raise ValueError('path outside destination: %r' % p)
    dest_dir = os.path.abspath(dest_dir)
    plen = len(dest_dir)
    archive = None
    if format is None:
        if archive_filename.endswith(('.zip', '.whl')):
            format = 'zip'
        elif archive_filename.endswith(('.tar.gz', '.tgz')):
            format = 'tgz'
            mode = 'r:gz'
        elif archive_filename.endswith(('.tar.bz2', '.tbz')):
            format = 'tbz'
            mode = 'r:bz2'
        elif archive_filename.endswith('.tar'):
            format = 'tar'
            mode = 'r'
        else:
            raise ValueError('Unknown format for %r' % archive_filename)
    try:
        if format == 'zip':
            archive = ZipFile(archive_filename, 'r')
            if check:
                names = archive.namelist()
                for name in names:
                    check_path(name)
        else:
            archive = tarfile.open(archive_filename, mode)
            if check:
                names = archive.getnames()
                for name in names:
                    check_path(name)
        if format != 'zip' and sys.version_info[0] < 3:
            for tarinfo in archive.getmembers():
                if not isinstance(tarinfo.name, text_type):
                    tarinfo.name = tarinfo.name.decode('utf-8')
        def extraction_filter(member, path):
            """Run tarfile.tar_filter, but raise the expected ValueError"""
            try:
                return tarfile.tar_filter(member, path)
            except tarfile.FilterError as exc:
                raise ValueError(str(exc))
        archive.extraction_filter = extraction_filter
        archive.extractall(dest_dir)
    finally:
        if archive:
            archive.close()
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
