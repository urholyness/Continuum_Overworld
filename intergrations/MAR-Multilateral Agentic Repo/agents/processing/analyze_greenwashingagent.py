
class analyze_greenwashingAgent:
    """Agent based on analyze_greenwashing from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor_enhanced.py"""
    
    def __init__(self):
        self.name = "analyze_greenwashingAgent"
        self.category = "processing"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Comprehensive greenwashing analysis"""
    indicator_scores = {}
    flagged_sections = []
    config = self.greenwashing_config
    if 'vagueness' in config['indicators']:
        vague_config = config['indicators']['vagueness']
        vague_count = 0
        for pattern in vague_config['patterns']:
            matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
            vague_count += len(matches)
            for match in matches:
                context = self.get_context_text(full_text, match.start(), match.end(), 100)
                flagged_sections.append({'type': 'vagueness', 'text': match.group(0), 'context': context, 'severity': 'medium', 'page': 1})
        total_sentences = len(re.split('[.!?]+', full_text))
        vague_ratio = vague_count / max(total_sentences, 1)
        indicator_scores['vagueness'] = min(100, vague_ratio / vague_config['threshold'] * 100)
    if 'sentiment_imbalance' in config['indicators']:
        sentiment_config = config['indicators']['sentiment_imbalance']
        blob = TextBlob(full_text)
        overall_sentiment = blob.sentiment.polarity
        risk_words = ['risk', 'challenge', 'difficulty', 'problem', 'issue', 'concern']
        risk_count = sum((len(re.findall(word, full_text, re.IGNORECASE)) for word in risk_words))
        total_words = len(full_text.split())
        risk_ratio = risk_count / max(total_words, 1)
        if overall_sentiment > sentiment_config['positive_threshold'] and risk_ratio < sentiment_config['risk_mentions_min']:
            indicator_scores['sentiment_imbalance'] = 80
            flagged_sections.append({'type': 'sentiment_imbalance', 'text': 'Overly positive tone without risk acknowledgment', 'context': f'Sentiment: {overall_sentiment:.2f}, Risk ratio: {risk_ratio:.3f}', 'severity': 'high', 'page': 1})
        else:
            indicator_scores['sentiment_imbalance'] = 0
    if 'contradictions' in config['indicators']:
        contradiction_config = config['indicators']['contradictions']
        contradiction_score = 0
        for claim in contradiction_config['zero_claims']:
            if re.search(claim, full_text, re.IGNORECASE):
                relevant_kpis = [kpi for kpi in kpis if 'carbon' in kpi.kpi_name.lower() or 'emission' in kpi.kpi_name.lower()]
                if any((kpi.kpi_value > 0 for kpi in relevant_kpis)):
                    contradiction_score += 25
                    flagged_sections.append({'type': 'contradiction', 'text': claim, 'context': f'Claim contradicts KPI data: {[kpi.kpi_value for kpi in relevant_kpis[:3]]}', 'severity': 'high', 'page': 1})
        indicator_scores['contradictions'] = min(100, contradiction_score)
    if 'omissions' in config['indicators']:
        omission_config = config['indicators']['omissions']
        required_categories = omission_config['required_categories']
        found_categories = []
        for category in required_categories:
            if re.search(category, full_text, re.IGNORECASE):
                found_categories.append(category)
        missing_count = len(required_categories) - len(found_categories)
        omission_ratio = missing_count / len(required_categories)
        indicator_scores['omissions'] = omission_ratio * 100
        if missing_count > 0:
            missing_cats = [cat for cat in required_categories if cat not in found_categories]
            flagged_sections.append({'type': 'omissions', 'text': f"Missing categories: {', '.join(missing_cats)}", 'context': f'Found: {len(found_categories)}/{len(required_categories)} required categories', 'severity': 'medium', 'page': 1})
    if 'hype' in config['indicators']:
        hype_config = config['indicators']['hype']
        hype_count = 0
        for keyword in hype_config['keywords']:
            matches = len(re.findall(keyword, full_text, re.IGNORECASE))
            hype_count += matches
        if hype_count > hype_config['threshold']:
            indicator_scores['hype'] = min(100, hype_count / hype_config['threshold'] * 100)
            flagged_sections.append({'type': 'hype', 'text': f'Excessive marketing language: {hype_count} instances', 'context': 'Multiple superlative claims without substantiation', 'severity': 'low', 'page': 1})
        else:
            indicator_scores['hype'] = 0
    weights = config['weights']
    overall_score = sum((indicator_scores.get(indicator, 0) * weights.get(indicator, 0) for indicator in weights.keys()))
    return GreenwashingAnalysis(company=company, ticker=ticker, overall_score=overall_score, indicator_scores=indicator_scores, flagged_sections=flagged_sections, report_name=report_name, analysis_year=analysis_year, analysis_date=datetime.now())
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
