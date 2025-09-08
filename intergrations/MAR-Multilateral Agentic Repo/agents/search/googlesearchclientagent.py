
class GoogleSearchClientAgent:
    """Agent based on GoogleSearchClient from ..\Nyxion\backend\integrations\google_search.py"""
    
    def __init__(self):
        self.name = "GoogleSearchClientAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Client for Google Custom Search API"""
        self.api_key = api_key or settings.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = search_engine_id or settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = 'https://www.googleapis.com/customsearch/v1'
        if not self.api_key or not self.search_engine_id:
            raise ValueError('Google Search API key and Search Engine ID must be provided')
        self.requests_per_second = 10
        self.last_request_time = None
        self.request_lock = asyncio.Lock()
    async def _rate_limit(self):
        """Implement rate limiting"""
        async with self.request_lock:
            if self.last_request_time:
                elapsed = (datetime.now() - self.last_request_time).total_seconds()
                if elapsed < 1.0 / self.requests_per_second:
                    await asyncio.sleep(1.0 / self.requests_per_second - elapsed)
            self.last_request_time = datetime.now()
    async def search(self, query: str, num_results: int=10, start_index: int=1, date_restrict: Optional[int]=None, site_search: Optional[str]=None, exclude_sites: Optional[List[str]]=None) -> List[GoogleSearchResult]:
        """
        Perform a Google search
        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for results
            date_restrict: Restrict results to past N days
            site_search: Restrict to specific site
            exclude_sites: List of sites to exclude
        Returns:
            List of search results
        """
        await self._rate_limit()
        params = {'key': self.api_key, 'cx': self.search_engine_id, 'q': query, 'num': min(num_results, 10), 'start': start_index}
        if date_restrict:
            params['dateRestrict'] = f'd{date_restrict}'
        if site_search:
            params['siteSearch'] = site_search
        if exclude_sites:
            exclusions = ' '.join([f'-site:{site}' for site in exclude_sites])
            params['q'] = f'{query} {exclusions}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 429:
                        raise ExternalAPIError('Google Search API rate limit exceeded')
                    elif response.status != 200:
                        error_data = await response.json()
                        raise ExternalAPIError(f'Google Search API error: {error_data}')
                    data = await response.json()
                    search_info = data.get('searchInformation', {})
                    logger.info(f"Google search completed: query='{query}', total_results={search_info.get('totalResults', 0)}, search_time={search_info.get('searchTime', 0)}s")
                    items = data.get('items', [])
                    return [GoogleSearchResult(item) for item in items]
        except aiohttp.ClientError as e:
            logger.error(f'Google Search API request failed: {str(e)}')
            raise ExternalAPIError(f'Failed to connect to Google Search API: {str(e)}')
    async def search_multiple_pages(self, query: str, total_results: int=30, date_restrict: Optional[int]=None, site_search: Optional[str]=None, exclude_sites: Optional[List[str]]=None) -> List[GoogleSearchResult]:
        """
        Search multiple pages to get more than 10 results
        Args:
            query: Search query
            total_results: Total number of results to fetch
            date_restrict: Restrict results to past N days
            site_search: Restrict to specific site
            exclude_sites: List of sites to exclude
        Returns:
            List of all search results
        """
        all_results = []
        start_index = 1
        while len(all_results) < total_results:
            remaining = total_results - len(all_results)
            num_to_fetch = min(10, remaining)
            try:
                results = await self.search(query=query, num_results=num_to_fetch, start_index=start_index, date_restrict=date_restrict, site_search=site_search, exclude_sites=exclude_sites)
                if not results:
                    break
                all_results.extend(results)
                start_index += len(results)
                if start_index > 91:
                    logger.warning(f"Reached Google's result limit for query: {query}")
                    break
            except ExternalAPIError as e:
                logger.error(f'Error fetching page {start_index}: {str(e)}')
                break
        return all_results
    async def batch_search(self, queries: List[Dict[str, Any]], results_per_query: int=10, date_restrict: Optional[int]=None) -> Dict[str, List[GoogleSearchResult]]:
        """
        Perform multiple searches in batch
        Args:
            queries: List of query configurations
            results_per_query: Number of results per query
            date_restrict: Restrict results to past N days
        Returns:
            Dictionary mapping query to results
        """
        results = {}
        semaphore = asyncio.Semaphore(5)
        async def search_with_semaphore(query_config: Dict[str, Any]):
            async with semaphore:
                query = query_config['query']
                try:
                    search_results = await self.search_multiple_pages(query=query, total_results=results_per_query, date_restrict=date_restrict)
                    return (query, search_results)
                except Exception as e:
                    logger.error(f"Failed to search for query '{query}': {str(e)}")
                    return (query, [])
        tasks = [search_with_semaphore(q) for q in queries]
        search_results = await asyncio.gather(*tasks)
        for query, query_results in search_results:
            results[query] = query_results
        return results
    def estimate_cost(self, num_queries: int) -> float:
        """
        Estimate cost for number of queries
        Google Custom Search API pricing (as of 2024):
        - First 100 queries per day: Free
        - Additional queries: $5 per 1000 queries
        """
        if num_queries <= 100:
            return 0.0
        else:
            additional_queries = num_queries - 100
            return additional_queries / 1000 * 5.0
    async def test_connection(self) -> bool:
        """Test if the API credentials are valid"""
        try:
            results = await self.search('test', num_results=1)
            return True
        except Exception as e:
            logger.error(f'Google Search API test failed: {str(e)}')
            return False
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
