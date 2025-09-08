
class output_package_listingAgent:
    """Agent based on output_package_listing from ..\Nyxion\env\Lib\site-packages\pip\_internal\commands\list.py"""
    
    def __init__(self):
        self.name = "output_package_listingAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            packages = sorted(packages, key=lambda dist: dist.canonical_name)
    if options.list_format == 'columns' and packages:
        data, header = format_for_columns(packages, options)
        self.output_package_listing_columns(data, header)
    elif options.list_format == 'freeze':
        for dist in packages:
            if options.verbose >= 1:
                write_output('%s==%s (%s)', dist.raw_name, dist.version, dist.location)
            else:
                write_output('%s==%s', dist.raw_name, dist.version)
    elif options.list_format == 'json':
        write_output(format_for_json(packages, options))
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
