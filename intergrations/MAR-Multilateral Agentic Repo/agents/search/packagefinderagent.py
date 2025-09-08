
class PackageFinderAgent:
    """Agent based on PackageFinder from ..\Nyxion\env\Lib\site-packages\pip\_internal\index\package_finder.py"""
    
    def __init__(self):
        self.name = "PackageFinderAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """This finds packages.
    This is meant to match easy_install's technique for looking for
    packages, by reading pages and looking for appropriate links.
    """
        """
        This constructor is primarily meant to be used by the create() class
        method and from tests.
        :param format_control: A FormatControl object, used to control
            the selection of source packages / binary packages when consulting
            the index and links.
        :param candidate_prefs: Options to use when creating a
            CandidateEvaluator object.
        """
        if candidate_prefs is None:
            candidate_prefs = CandidatePreferences()
        format_control = format_control or FormatControl(set(), set())
        self._allow_yanked = allow_yanked
        self._candidate_prefs = candidate_prefs
        self._ignore_requires_python = ignore_requires_python
        self._link_collector = link_collector
        self._target_python = target_python
        self.format_control = format_control
        self._logged_links: Set[Tuple[Link, LinkType, str]] = set()
        self._all_candidates: Dict[str, List[InstallationCandidate]] = {}
        self._best_candidates: Dict[Tuple[str, Optional[specifiers.BaseSpecifier], Optional[Hashes]], BestCandidateResult] = {}
    @classmethod
    def create(cls, link_collector: LinkCollector, selection_prefs: SelectionPreferences, target_python: Optional[TargetPython]=None) -> 'PackageFinder':
        """Create a PackageFinder.
        :param selection_prefs: The candidate selection preferences, as a
            SelectionPreferences object.
        :param target_python: The target Python interpreter to use when
            checking compatibility. If None (the default), a TargetPython
            object will be constructed from the running Python.
        """
        if target_python is None:
            target_python = TargetPython()
        candidate_prefs = CandidatePreferences(prefer_binary=selection_prefs.prefer_binary, allow_all_prereleases=selection_prefs.allow_all_prereleases)
        return cls(candidate_prefs=candidate_prefs, link_collector=link_collector, target_python=target_python, allow_yanked=selection_prefs.allow_yanked, format_control=selection_prefs.format_control, ignore_requires_python=selection_prefs.ignore_requires_python)
    @property
    def target_python(self) -> TargetPython:
        return self._target_python
    @property
    def search_scope(self) -> SearchScope:
        return self._link_collector.search_scope
    @search_scope.setter
    def search_scope(self, search_scope: SearchScope) -> None:
        self._link_collector.search_scope = search_scope
    @property
    def find_links(self) -> List[str]:
        return self._link_collector.find_links
    @property
    def index_urls(self) -> List[str]:
        return self.search_scope.index_urls
    @property
    def proxy(self) -> Optional[str]:
        return self._link_collector.session.pip_proxy
    @property
    def trusted_hosts(self) -> Iterable[str]:
        for host_port in self._link_collector.session.pip_trusted_origins:
            yield build_netloc(*host_port)
    @property
    def custom_cert(self) -> Optional[str]:
        verify = self._link_collector.session.verify
        return verify if isinstance(verify, str) else None
    @property
    def client_cert(self) -> Optional[str]:
        cert = self._link_collector.session.cert
        assert not isinstance(cert, tuple), 'pip only supports PEM client certs'
        return cert
    @property
    def allow_all_prereleases(self) -> bool:
        return self._candidate_prefs.allow_all_prereleases
    def set_allow_all_prereleases(self) -> None:
        self._candidate_prefs.allow_all_prereleases = True
    @property
    def prefer_binary(self) -> bool:
        return self._candidate_prefs.prefer_binary
    def set_prefer_binary(self) -> None:
        self._candidate_prefs.prefer_binary = True
    def requires_python_skipped_reasons(self) -> List[str]:
        reasons = {detail for _, result, detail in self._logged_links if result == LinkType.requires_python_mismatch}
        return sorted(reasons)
    def make_link_evaluator(self, project_name: str) -> LinkEvaluator:
        canonical_name = canonicalize_name(project_name)
        formats = self.format_control.get_allowed_formats(canonical_name)
        return LinkEvaluator(project_name=project_name, canonical_name=canonical_name, formats=formats, target_python=self._target_python, allow_yanked=self._allow_yanked, ignore_requires_python=self._ignore_requires_python)
    def _sort_links(self, links: Iterable[Link]) -> List[Link]:
        """
        Returns elements of links in order, non-egg links first, egg links
        second, while eliminating duplicates
        """
        eggs, no_eggs = ([], [])
        seen: Set[Link] = set()
        for link in links:
            if link not in seen:
                seen.add(link)
                if link.egg_fragment:
                    eggs.append(link)
                else:
                    no_eggs.append(link)
        return no_eggs + eggs
    def _log_skipped_link(self, link: Link, result: LinkType, detail: str) -> None:
        entry = (link, result, detail)
        if entry not in self._logged_links:
            logger.debug('Skipping link: %s: %s', detail, link)
            self._logged_links.add(entry)
    def get_install_candidate(self, link_evaluator: LinkEvaluator, link: Link) -> Optional[InstallationCandidate]:
        """
        If the link is a candidate for install, convert it to an
        """
        result, detail = link_evaluator.evaluate_link(link)
        if result != LinkType.candidate:
            self._log_skipped_link(link, result, detail)
        try:
            return InstallationCandidate(name=link_evaluator.project_name, link=link, version=detail)
        except InvalidVersion:
    def evaluate_links(self, link_evaluator: LinkEvaluator, links: Iterable[Link]) -> List[InstallationCandidate]:
        """
        Convert links that are candidates to InstallationCandidate objects.
        """
        candidates = []
        for link in self._sort_links(links):
            candidate = self.get_install_candidate(link_evaluator, link)
            if candidate is not None:
                candidates.append(candidate)
        return candidates
    def process_project_url(self, project_url: Link, link_evaluator: LinkEvaluator) -> List[InstallationCandidate]:
        logger.debug('Fetching project page and analyzing links: %s', project_url)
        index_response = self._link_collector.fetch_response(project_url)
        if index_response is None:
            return []
        page_links = list(parse_links(index_response))
        with indent_log():
            package_links = self.evaluate_links(link_evaluator, links=page_links)
        return package_links
    def find_all_candidates(self, project_name: str) -> List[InstallationCandidate]:
        """Find all available InstallationCandidate for project_name
        This checks index_urls and find_links.
        All versions found are returned as an InstallationCandidate list.
        See LinkEvaluator.evaluate_link() for details on which files
        are accepted.
        """
        if project_name in self._all_candidates:
            return self._all_candidates[project_name]
        link_evaluator = self.make_link_evaluator(project_name)
        collected_sources = self._link_collector.collect_sources(project_name=project_name, candidates_from_page=functools.partial(self.process_project_url, link_evaluator=link_evaluator))
        page_candidates_it = itertools.chain.from_iterable((source.page_candidates() for sources in collected_sources for source in sources if source is not None))
        page_candidates = list(page_candidates_it)
        file_links_it = itertools.chain.from_iterable((source.file_links() for sources in collected_sources for source in sources if source is not None))
        file_candidates = self.evaluate_links(link_evaluator, sorted(file_links_it, reverse=True))
        if logger.isEnabledFor(logging.DEBUG) and file_candidates:
            paths = []
            for candidate in file_candidates:
                assert candidate.link.url
                try:
                    paths.append(candidate.link.file_path)
                except Exception:
                    paths.append(candidate.link.url)
            logger.debug('Local files found: %s', ', '.join(paths))
        self._all_candidates[project_name] = file_candidates + page_candidates
        return self._all_candidates[project_name]
    def make_candidate_evaluator(self, project_name: str, specifier: Optional[specifiers.BaseSpecifier]=None, hashes: Optional[Hashes]=None) -> CandidateEvaluator:
        """Create a CandidateEvaluator object to use."""
        candidate_prefs = self._candidate_prefs
        return CandidateEvaluator.create(project_name=project_name, target_python=self._target_python, prefer_binary=candidate_prefs.prefer_binary, allow_all_prereleases=candidate_prefs.allow_all_prereleases, specifier=specifier, hashes=hashes)
    def find_best_candidate(self, project_name: str, specifier: Optional[specifiers.BaseSpecifier]=None, hashes: Optional[Hashes]=None) -> BestCandidateResult:
        """Find matches for the given project and specifier.
        :param specifier: An optional object implementing `filter`
            (e.g. `packaging.specifiers.SpecifierSet`) to filter applicable
            versions.
        :return: A `BestCandidateResult` instance.
        """
        if (project_name, specifier, hashes) in self._best_candidates:
            return self._best_candidates[project_name, specifier, hashes]
        candidates = self.find_all_candidates(project_name)
        candidate_evaluator = self.make_candidate_evaluator(project_name=project_name, specifier=specifier, hashes=hashes)
        self._best_candidates[project_name, specifier, hashes] = candidate_evaluator.compute_best_candidate(candidates)
        return self._best_candidates[project_name, specifier, hashes]
    def find_requirement(self, req: InstallRequirement, upgrade: bool) -> Optional[InstallationCandidate]:
        """Try to find a Link matching req
        Expects req, an InstallRequirement and upgrade, a boolean
        Returns a InstallationCandidate if found,
        Raises DistributionNotFound or BestVersionAlreadyInstalled otherwise
        """
        name = req.name
        assert name is not None, 'find_requirement() called with no name'
        hashes = req.hashes(trust_internet=False)
        best_candidate_result = self.find_best_candidate(name, specifier=req.specifier, hashes=hashes)
        best_candidate = best_candidate_result.best_candidate
        installed_version: Optional[_BaseVersion] = None
        if req.satisfied_by is not None:
            installed_version = req.satisfied_by.version
        def _format_versions(cand_iter: Iterable[InstallationCandidate]) -> str:
            return ', '.join(sorted({str(c.version) for c in cand_iter}, key=parse_version)) or 'none'
        if installed_version is None and best_candidate is None:
            logger.critical('Could not find a version that satisfies the requirement %s (from versions: %s)', req, _format_versions(best_candidate_result.all_candidates))
            raise DistributionNotFound(f'No matching distribution found for {req}')
        def _should_install_candidate(candidate: Optional[InstallationCandidate]) -> 'TypeGuard[InstallationCandidate]':
            if installed_version is None:
                return True
            if best_candidate is None:
                return False
            return best_candidate.version > installed_version
        if not upgrade and installed_version is not None:
            if _should_install_candidate(best_candidate):
                logger.debug('Existing installed version (%s) satisfies requirement (most up-to-date version is %s)', installed_version, best_candidate.version)
            else:
                logger.debug('Existing installed version (%s) is most up-to-date and satisfies requirement', installed_version)
        if _should_install_candidate(best_candidate):
            logger.debug('Using version %s (newest of versions: %s)', best_candidate.version, _format_versions(best_candidate_result.applicable_candidates))
            return best_candidate
        logger.debug('Installed version (%s) is most up-to-date (past versions: %s)', installed_version, _format_versions(best_candidate_result.applicable_candidates))
        raise BestVersionAlreadyInstalled
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
