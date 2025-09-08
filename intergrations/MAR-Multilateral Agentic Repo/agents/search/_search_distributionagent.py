
class _search_distributionAgent:
    """Agent based on _search_distribution from ..\Nyxion\env\Lib\site-packages\pip\_internal\metadata\pkg_resources.py"""
    
    def __init__(self):
        self.name = "_search_distributionAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Find a distribution matching the ``name`` in the environment.
        This searches from *all* distributions available in the environment, to
        match the behavior of ``pkg_resources.get_distribution()``.
        """
    canonical_name = canonicalize_name(name)
    for dist in self.iter_all_distributions():
        if dist.canonical_name == canonical_name:
            return dist
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
