
class _warn_unsafe_extraction_pathAgent:
    """Agent based on _warn_unsafe_extraction_path from ..\Nyxion\env\Lib\site-packages\pip\_vendor\pkg_resources\__init__.py"""
    
    def __init__(self):
        self.name = "_warn_unsafe_extraction_pathAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
        def _warn_unsafe_extraction_path(path):
    """
        If the default extraction path is overridden and set to an insecure
        location, such as /tmp, it opens up an opportunity for an attacker to
        replace an extracted file with an unauthorized payload. Warn the user
        if a known insecure location is used.
        See Distribute #375 for more details.
        """
    if os.name == 'nt' and (not path.startswith(os.environ['windir'])):
        return
    mode = os.stat(path).st_mode
    if mode & stat.S_IWOTH or mode & stat.S_IWGRP:
        msg = 'Extraction path is writable by group/others and vulnerable to attack when used with get_resource_filename ({path}). Consider a more secure location (set with .set_extraction_path or the PYTHON_EGG_CACHE environment variable).'.format(**locals())
        warnings.warn(msg, UserWarning)
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
