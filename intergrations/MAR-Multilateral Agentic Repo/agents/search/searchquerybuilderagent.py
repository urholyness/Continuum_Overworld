
class SearchQueryBuilderAgent:
    """Agent based on SearchQueryBuilder from ..\Nyxion\backend\services\brand_buzz.py"""
    
    def __init__(self):
        self.name = "SearchQueryBuilderAgent"
        self.category = "search"
        self.status = "active"
    
    def search(self, query, **kwargs):
        """Search functionality"""
            """Builds search queries for different search engines and sources"""
    SOURCE_DOMAINS = {SourceType.NEWS: ['news.google.com', 'cnn.com', 'bbc.com', 'reuters.com', 'nytimes.com', 'wsj.com', 'theguardian.com', 'forbes.com', 'bloomberg.com'], SourceType.SOCIAL_MEDIA: ['twitter.com', 'x.com', 'reddit.com', 'facebook.com', 'linkedin.com', 'instagram.com'], SourceType.REVIEW: ['trustpilot.com', 'yelp.com', 'g2.com', 'capterra.com', 'glassdoor.com'], SourceType.FORUM: ['reddit.com', 'quora.com', 'stackoverflow.com', 'news.ycombinator.com'], SourceType.BLOG: ['medium.com', 'wordpress.com', 'blogger.com', 'substack.com'], SourceType.PRESS_RELEASE: ['prnewswire.com', 'businesswire.com', 'prweb.com', 'einpresswire.com'], SourceType.GOVERNMENT: ['*.gov', '*.gov.uk', '*.gc.ca', '*.gov.au']}
    HIGH_RISK_KEYWORDS = {'scandal', 'fraud', 'lawsuit', 'investigation', 'breach', 'violation', 'recall', 'controversy', 'allegation', 'accused', 'guilty', 'penalty', 'fine', 'sanctions', 'bankruptcy'}
        self.query_cache = {}
    def build_queries(self, config: SearchConfiguration) -> List[Dict[str, Any]]:
        """Build all search queries based on configuration"""
        queries = []
        for brand in config.brands:
            for keyword_combo in config.keyword_combinations:
                for source_type in config.source_types:
                    query = self._build_single_query(brand, keyword_combo, source_type)
                    queries.append({'query': query, 'brand': brand, 'keywords': keyword_combo.keywords, 'source_type': source_type, 'metadata': {'keyword_combination': keyword_combo.to_dict() if hasattr(keyword_combo, 'to_dict') else {'keywords': keyword_combo.keywords, 'operators': [op.value for op in keyword_combo.operators]}}})
        return queries
    def _build_single_query(self, brand: str, keyword_combo: KeywordCombination, source_type: SourceType) -> str:
        """Build a single search query"""
        query_parts = [f'"{brand}"']
        keyword_query = keyword_combo.to_google_query()
        if keyword_query:
            query_parts.append(f'({keyword_query})')
        source_operators = self._get_source_operators(source_type)
        if source_operators:
            query_parts.append(source_operators)
        query_parts.append('-advertisement -sponsored -promo')
        return ' '.join(query_parts)
    def _get_source_operators(self, source_type: SourceType) -> str:
        """Get search operators for specific source type"""
        if source_type not in self.SOURCE_DOMAINS:
            return ''
        domains = self.SOURCE_DOMAINS[source_type]
        if source_type == SourceType.GOVERNMENT:
            return ' OR '.join([f'site:{domain}' for domain in domains])
        site_operators = ' OR '.join([f'site:{domain}' for domain in domains[:5]])
        return f'({site_operators})'
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ''
    def identify_source_type(self, url: str) -> SourceType:
        """Identify source type from URL"""
        domain = self.extract_domain(url).lower()
        for source_type, domains in self.SOURCE_DOMAINS.items():
            for source_domain in domains:
                if source_domain.startswith('*'):
                    if domain.endswith(source_domain[1:]):
                        return source_type
                elif domain == source_domain or domain.endswith(f'.{source_domain}'):
                    return source_type
        return SourceType.OTHER
    def calculate_risk_score(self, text: str, keywords: List[str], sentiment_score: float) -> float:
        """Calculate risk score based on keywords found and sentiment"""
        text_lower = text.lower()
        risk_score = 0.0
        high_risk_found = sum((1 for keyword in self.HIGH_RISK_KEYWORDS if keyword in text_lower))
        risk_score += min(high_risk_found * 0.2, 0.6)
        keywords_found = sum((1 for keyword in keywords if keyword.lower() in text_lower))
        risk_score += min(keywords_found * 0.1, 0.3)
        if sentiment_score < 0:
            risk_score += abs(sentiment_score) * 0.3
        return min(max(risk_score, 0.0), 1.0)
    def get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
        
    def run(self, query, **kwargs):
        """Main execution method"""
        return self.search(query, **kwargs)
