
class search_esg_reports_api_with_retryAgent:
    """Agent based on search_esg_reports_api_with_retry from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\esg_scraper_patched.py"""
    
    def __init__(self):
        self.name = "search_esg_reports_api_with_retryAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """
        Search for ESG reports using Google Custom Search API with retry logic.
        Args:
            company (str): Company name
            website (str): Company website  
            max_results (int): Maximum number of results
        Returns:
            SearchResult: Search results with metadata
        """
    start_time = time.time()
    retry_count = 0
    cache_key = f'esg_api_patched:{company}:{website}'
    cached_result = self.redis_client.get(cache_key)
    if cached_result:
        logger.info(f'API cache hit for {company}')
        cached_data = json.loads(cached_result)
        return SearchResult(**cached_data)
    if not self.search_service:
        return SearchResult(company=company, ticker='', website=website, urls=[], normalized_urls=[], search_method='api', search_time=time.time() - start_time, success=False, error_message='Google Custom Search API not available')
    company_lower = company.lower()
    search_queries = self.enhanced_search_queries.copy()
    for key, queries in self.company_specific_queries.items():
        if key in company_lower:
            search_queries.extend(queries)
            logger.info(f'Added {len(queries)} company-specific queries for {company}')
    all_urls = []
    normalized_urls = []
    while retry_count <= self.max_retries:
        try:
            for query_template in search_queries[:5]:
                query = f'site:{website} ({query_template})'
                logger.info(f'API search (attempt {retry_count + 1}): {query}')
                result = self.search_service.cse().list(q=query, cx=self.cse_id, num=min(max_results, 10), fileType='pdf').execute()
                self.metrics.api_calls_made += 1
                for item in result.get('items', []):
                    original_url = item.get('link')
                    if original_url:
                        normalized_url = self.normalize_url(original_url)
                        if self._is_valid_pdf_url(normalized_url) and self._is_esg_related_url(normalized_url):
                            all_urls.append(original_url)
                            normalized_urls.append(normalized_url)
                time.sleep(self.api_delay)
                if len(all_urls) >= max_results:
                    break
            seen = set()
            unique_urls = []
            unique_normalized = []
            for i, url in enumerate(all_urls):
                normalized = normalized_urls[i] if i < len(normalized_urls) else url
                if normalized not in seen:
                    seen.add(normalized)
                    unique_urls.append(url)
                    unique_normalized.append(normalized)
            search_result = SearchResult(company=company, ticker='', website=website, urls=unique_urls[:max_results], normalized_urls=unique_normalized[:max_results], search_method='api', search_time=time.time() - start_time, success=True, retry_count=retry_count)
            self.redis_client.setex(cache_key, 86400, json.dumps(asdict(search_result)))
            self.metrics.cost_estimate += 0.005 * min(len(search_queries), 5)
            logger.info(f'API search successful for {company}: {len(unique_urls)} URLs found (attempt {retry_count + 1})')
            return search_result
        except HttpError as e:
            if e.resp.status in [429, 403]:
                retry_count += 1
                self.metrics.retry_attempts += 1
                if retry_count <= self.max_retries:
                    delay = self.rate_limit_delay * 2 ** (retry_count - 1)
                    logger.warning(f'Rate limit hit for {company}, retrying in {delay}s (attempt {retry_count})')
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f'Max retries exceeded for {company}: {e}')
                    break
            else:
                logger.error(f'API error for {company}: {e}')
                break
        except Exception as e:
            retry_count += 1
            self.metrics.retry_attempts += 1
            if retry_count <= self.max_retries:
                logger.warning(f'Error searching for {company}, retrying: {e}')
                time.sleep(self.retry_delay)
                continue
            else:
                logger.error(f'Max retries exceeded for {company}: {e}')
                break
    return SearchResult(company=company, ticker='', website=website, urls=[], normalized_urls=[], search_method='api', search_time=time.time() - start_time, success=False, retry_count=retry_count, error_message=f'Failed after {retry_count} attempts')
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
