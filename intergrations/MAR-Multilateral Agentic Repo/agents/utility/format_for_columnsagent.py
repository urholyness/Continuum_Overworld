
class format_for_columnsAgent:
    """Agent based on format_for_columns from ..\Nyxion\env\Lib\site-packages\pip\_internal\commands\list.py"""
    
    def __init__(self):
        self.name = "format_for_columnsAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Convert the package data into something usable
    by output_package_listing_columns.
    """
    header = ['Package', 'Version']
    running_outdated = options.outdated
    if running_outdated:
        header.extend(['Latest', 'Type'])
    def wheel_build_tag(dist: BaseDistribution) -> Optional[str]:
        try:
            wheel_file = dist.read_text('WHEEL')
        except FileNotFoundError:
        return Parser().parsestr(wheel_file).get('Build')
    build_tags = [wheel_build_tag(p) for p in pkgs]
    has_build_tags = any(build_tags)
    if has_build_tags:
        header.append('Build')
    if options.verbose >= 1:
        header.append('Location')
    if options.verbose >= 1:
        header.append('Installer')
    has_editables = any((x.editable for x in pkgs))
    if has_editables:
        header.append('Editable project location')
    data = []
    for i, proj in enumerate(pkgs):
        row = [proj.raw_name, proj.raw_version]
        if running_outdated:
            row.append(str(proj.latest_version))
            row.append(proj.latest_filetype)
        if has_build_tags:
            row.append(build_tags[i] or '')
        if has_editables:
            row.append(proj.editable_project_location or '')
        if options.verbose >= 1:
            row.append(proj.location or '')
        if options.verbose >= 1:
            row.append(proj.installer)
        data.append(row)
    return (data, header)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
