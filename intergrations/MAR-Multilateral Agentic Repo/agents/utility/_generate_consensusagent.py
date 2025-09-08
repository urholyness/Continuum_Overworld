
class _generate_consensusAgent:
    """Agent based on _generate_consensus from ..\Rank_AI\02_report_acquisition\ai_multi_validator.py"""
    
    def __init__(self):
        self.name = "_generate_consensusAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Generate consensus result from multiple AI validations"""
    if not method_results:
        return MultiAIValidationResult(consensus_score=0.0, consensus_assessment='No AI methods available for validation', method_results={}, agreement_level=0.0, recommendation='Cannot validate - no AI methods available', final_concerns=['No AI validation methods available'], best_method='none', processing_summary={'total_methods': 0})
    valid_results = [r for r in method_results.values() if r.error is None]
    failed_results = [r for r in method_results.values() if r.error is not None]
    if not valid_results:
        return MultiAIValidationResult(consensus_score=0.0, consensus_assessment='All AI validation methods failed', method_results=method_results, agreement_level=0.0, recommendation='Manual review required - all AI methods failed', final_concerns=[r.error for r in failed_results], best_method='none', processing_summary={'total_methods': len(method_results), 'failed_methods': len(failed_results)})
    validity_votes = [r.is_valid_report for r in valid_results]
    valid_count = sum(validity_votes)
    agreement_level = max(valid_count, len(validity_votes) - valid_count) / len(validity_votes) * 100
    total_weight = sum((r.confidence or 0.0 for r in valid_results))
    if total_weight > 0:
        consensus_score = sum(((r.quality_score or 0.0) * (r.confidence or 0.0) for r in valid_results)) / total_weight
    else:
        consensus_score = sum((r.quality_score or 0.0 for r in valid_results)) / len(valid_results)
    best_method = max(valid_results, key=lambda x: (x.quality_score or 0.0) * (x.confidence or 0.0)).method
    valid_reports = sum((1 for r in valid_results if r.is_valid_report))
    if valid_reports > len(valid_results) / 2:
        consensus_assessment = f'Consensus: Valid ESG report ({valid_reports}/{len(valid_results)} methods agree)'
    else:
        consensus_assessment = f'Consensus: Not a valid ESG report ({len(valid_results) - valid_reports}/{len(valid_results)} methods agree)'
    if agreement_level >= 80:
        recommendation = f'High confidence - use {best_method} result (best performing method)'
    elif agreement_level >= 60:
        recommendation = f'Moderate confidence - recommend {best_method} result but verify manually'
    else:
        recommendation = 'Low agreement between methods - manual review required'
    all_concerns = []
    for result in valid_results:
        all_concerns.extend(result.concerns)
    if failed_results:
        all_concerns.append(f'{len(failed_results)} AI methods failed')
    return MultiAIValidationResult(consensus_score=consensus_score, consensus_assessment=consensus_assessment, method_results=method_results, agreement_level=agreement_level, recommendation=recommendation, final_concerns=list(set(all_concerns)), best_method=best_method, processing_summary={'total_methods': len(method_results), 'successful_methods': len(valid_results), 'failed_methods': len(failed_results), 'extraction_method': extraction_method, 'agreement_level': agreement_level})
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
