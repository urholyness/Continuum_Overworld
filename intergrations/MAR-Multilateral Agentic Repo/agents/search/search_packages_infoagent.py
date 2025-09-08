
class search_packages_infoAgent:
    """Agent based on search_packages_info from ..\Nyxion\env\Lib\site-packages\pip\_internal\commands\show.py"""
    
    def __init__(self):
        self.name = "search_packages_infoAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """
    Gather details from installed distributions. Print distribution name,
    version, location, and installed files. Installed files requires a
    pip generated 'installed-files.txt' in the distributions '.egg-info'
    directory.
    """
    env = get_default_environment()
    installed = {dist.canonical_name: dist for dist in env.iter_all_distributions()}
    query_names = [canonicalize_name(name) for name in query]
    missing = sorted([name for name, pkg in zip(query, query_names) if pkg not in installed])
    if missing:
        logger.warning('Package(s) not found: %s', ', '.join(missing))
    def _get_requiring_packages(current_dist: BaseDistribution) -> Iterator[str]:
        return (dist.metadata['Name'] or 'UNKNOWN' for dist in installed.values() if current_dist.canonical_name in {canonicalize_name(d.name) for d in dist.iter_dependencies()})
    for query_name in query_names:
        try:
            dist = installed[query_name]
        except KeyError:
            continue
        try:
            requires = sorted({req.name for req in dist.iter_dependencies()}, key=str.lower)
        except InvalidRequirement:
            requires = sorted(dist.iter_raw_dependencies(), key=str.lower)
        try:
            required_by = sorted(_get_requiring_packages(dist), key=str.lower)
        except InvalidRequirement:
            required_by = ['#N/A']
        try:
            entry_points_text = dist.read_text('entry_points.txt')
            entry_points = entry_points_text.splitlines(keepends=False)
        except FileNotFoundError:
            entry_points = []
        files_iter = dist.iter_declared_entries()
        if files_iter is None:
            files: Optional[List[str]] = None
        else:
            files = sorted(files_iter)
        metadata = dist.metadata
        project_urls = metadata.get_all('Project-URL', [])
        homepage = metadata.get('Home-page', '')
        if not homepage:
            for url in project_urls:
                url_label, url = url.split(',', maxsplit=1)
                normalized_label = normalize_project_url_label(url_label)
                if normalized_label == 'homepage':
                    homepage = url.strip()
                    break
        yield _PackageInfo(name=dist.raw_name, version=dist.raw_version, location=dist.location or '', editable_project_location=dist.editable_project_location, requires=requires, required_by=required_by, installer=dist.installer, metadata_version=dist.metadata_version or '', classifiers=metadata.get_all('Classifier', []), summary=metadata.get('Summary', ''), homepage=homepage, project_urls=project_urls, author=metadata.get('Author', ''), author_email=metadata.get('Author-email', ''), license=metadata.get('License', ''), license_expression=metadata.get('License-Expression', ''), entry_points=entry_points, files=files)
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
