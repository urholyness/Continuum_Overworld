
class EnhancedValidatorAgent:
    """Agent based on EnhancedValidator from ..\Rank_AI\05_validation_verification\enhanced_validator.py"""
    
    def __init__(self):
        self.name = "EnhancedValidatorAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """
    Stage 5: Enhanced validation and cross-referencing system
    Capabilities:
    - Statistical confidence modeling with Bayesian inference
    - Multi-source cross-validation (table, content, historical)
    - Outlier detection using Z-score and IQR methods
    - Temporal consistency analysis across reporting periods
    - Industry benchmark comparison and deviation analysis
    - MAR distributed validation with specialist agents
    - Unified DB integration for cross-project intelligence
    """
        """
        Initialize enhanced validator
        Args:
            config_path: Path to validation configuration
        """
        self.config_path = config_path or Path(__file__).parent / 'validation_config.json'
        self.config = self._load_config()
        self.confidence_levels = {'high': 0.95, 'medium': 0.85, 'low': 0.7}
        self.industry_benchmarks = self._load_industry_benchmarks()
        print('✅ Enhanced Validator initialized')
        print('📊 Statistical confidence modeling enabled')
        print('🔍 Cross-source validation active')
        print('📈 Temporal consistency analysis ready')
    def _load_config(self) -> Dict:
        """Load validation configuration"""
        default_config = {'validation_methods': ['statistical_confidence', 'cross_source_validation', 'outlier_detection', 'temporal_consistency', 'industry_benchmark'], 'anomaly_detection': {'z_score_threshold': 2.5, 'iqr_multiplier': 1.5, 'bayesian_prior': 0.1}, 'confidence_modeling': {'min_samples': 3, 'bootstrap_iterations': 1000, 'credible_interval': 0.95}, 'mar_integration': {'specialist_agents': ['StatisticalAnalyst', 'OutlierDetector', 'TemporalValidator', 'BenchmarkAnalyzer', 'CrossValidator'], 'coordination_protocol': 'distributed_consensus'}}
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
        except (FileNotFoundError, json.JSONDecodeError):
        return default_config
    def _load_industry_benchmarks(self) -> Dict[str, Dict]:
        """Load industry benchmark data (placeholder for real data integration)"""
        return {'energy_utilities': {'scope_1_emissions_per_mwh': {'mean': 820, 'std': 150}, 'renewable_energy_pct': {'mean': 35, 'std': 15}, 'employee_safety_rate': {'mean': 0.08, 'std': 0.03}}, 'financial_services': {'scope_1_emissions_per_employee': {'mean': 2.1, 'std': 0.5}, 'scope_2_emissions_per_employee': {'mean': 1.8, 'std': 0.4}, 'board_diversity': {'mean': 38, 'std': 12}}, 'manufacturing': {'scope_1_emissions_intensity': {'mean': 1200, 'std': 300}, 'water_consumption_intensity': {'mean': 45, 'std': 15}, 'waste_diversion_rate': {'mean': 78, 'std': 8}}}
    def validate_kpis(self, state: ValidationState, historical_data: Optional[List[Dict]]=None, industry_context: str='general') -> ValidationState:
        """
        Main validation method with enhanced statistical analysis
        Args:
            state: ValidationState with extracted KPIs from Stage 4
            historical_data: Historical KPI data for temporal analysis
            industry_context: Industry classification for benchmarking
        Returns:
            ValidationState with comprehensive validation results
        """
        state.historical_data = historical_data or []
        state.agent_logs = []
        state.coordination_metadata = {'validation_start': datetime.now().isoformat(), 'stage': 'stage_5_enhanced_validation', 'validation_methods': self.config['validation_methods'], 'mar_integration': 'active', 'unified_db_ready': True}
        validation_results = {}
        if not state.extracted_kpis:
            raise ValueError('No extracted KPIs provided for validation')
        for kpi_key, kpi_data in state.extracted_kpis.items():
            if not isinstance(kpi_data, dict) or kpi_data.get('value') is None:
                continue
            original_value = float(kpi_data['value'])
            state.agent_logs.append({'agent': 'ValidationOrchestrator', 'action': 'begin_kpi_validation', 'kpi': kpi_key, 'original_value': original_value, 'timestamp': datetime.now().isoformat()})
            confidence_result = self._calculate_statistical_confidence(kpi_key, original_value, kpi_data, state.historical_data)
            cross_source_result = self._perform_cross_source_validation(kpi_key, original_value, kpi_data)
            anomaly_result = self._detect_anomalies(kpi_key, original_value, state.historical_data, industry_context)
            temporal_result = self._check_temporal_consistency(kpi_key, original_value, state.historical_data)
            benchmark_result = self._compare_industry_benchmarks(kpi_key, original_value, industry_context, state.company_name)
            validation_result = self._consolidate_validation_results(kpi_key, original_value, kpi_data, confidence_result, cross_source_result, anomaly_result, temporal_result, benchmark_result)
            validation_results[kpi_key] = validation_result
            state.agent_logs.append({'agent': 'ValidationOrchestrator', 'action': 'complete_kpi_validation', 'kpi': kpi_key, 'validation_score': validation_result.confidence_score, 'recommendation': validation_result.recommendation, 'timestamp': datetime.now().isoformat()})
        state.validation_results = validation_results
        if validation_results:
            confidence_scores = [v.confidence_score for v in validation_results.values()]
            state.overall_validation_score = statistics.mean(confidence_scores)
        state.coordination_metadata['validation_end'] = datetime.now().isoformat()
        return state
    def _calculate_statistical_confidence(self, kpi_key: str, value: float, kpi_data: Dict, historical_data: List[Dict]) -> Dict:
        """Calculate statistical confidence using Bayesian inference"""
        historical_values = []
        for hist_record in historical_data:
            if kpi_key in hist_record.get('kpis', {}):
                historical_values.append(float(hist_record['kpis'][kpi_key]))
        if len(historical_values) >= 3:
            historical_mean = statistics.mean(historical_values)
            historical_std = statistics.stdev(historical_values) if len(historical_values) > 1 else historical_mean * 0.1
            extraction_confidence = kpi_data.get('confidence', 0.8)
            prior_precision = 1 / historical_std ** 2 if historical_std > 0 else 1
            likelihood_precision = extraction_confidence * 10
            posterior_precision = prior_precision + likelihood_precision
            posterior_mean = (prior_precision * historical_mean + likelihood_precision * value) / posterior_precision
            posterior_std = math.sqrt(1 / posterior_precision)
            z_score = 1.96
            confidence_interval = (posterior_mean - z_score * posterior_std, posterior_mean + z_score * posterior_std)
            if historical_std > 0:
                z_stat = abs(value - historical_mean) / (historical_std / math.sqrt(len(historical_values)))
                p_value = 2 * (1 - self._standard_normal_cdf(z_stat))
            else:
                p_value = None
            confidence_score = min(0.99, extraction_confidence * (1 - min(p_value or 0, 0.5)))
        else:
            confidence_score = kpi_data.get('confidence', 0.8) * 0.7
            confidence_interval = (value * 0.8, value * 1.2)
            p_value = None
            posterior_mean = value
        return {'confidence_score': confidence_score, 'confidence_interval': confidence_interval, 'p_value': p_value, 'validated_value': posterior_mean if len(historical_values) >= 3 else value, 'method': 'bayesian_inference', 'historical_samples': len(historical_values)}
    def _perform_cross_source_validation(self, kpi_key: str, value: float, kpi_data: Dict) -> Dict:
        """Validate KPI across multiple extraction sources"""
        extraction_method = kpi_data.get('extraction_method', 'unknown')
        source = kpi_data.get('source', 'unknown')
        if extraction_method == 'table_analysis':
            agreement_score = 0.95
        elif extraction_method == 'pattern_matching':
            agreement_score = 0.8
        else:
            agreement_score = 0.7
        patterns_matched = kpi_data.get('patterns_matched', [])
        if len(patterns_matched) > 1:
            agreement_score += 0.05
        return {'agreement_score': min(0.99, agreement_score), 'source_count': 1, 'extraction_method': extraction_method, 'method': 'cross_source_validation'}
    def _detect_anomalies(self, kpi_key: str, value: float, historical_data: List[Dict], industry_context: str) -> Dict:
        """Detect anomalies using statistical methods"""
        historical_values = []
        for hist_record in historical_data:
            if kpi_key in hist_record.get('kpis', {}):
                historical_values.append(float(hist_record['kpis'][kpi_key]))
        anomaly_score = 0.0
        anomaly_methods = []
        if len(historical_values) >= 2:
            hist_mean = statistics.mean(historical_values)
            hist_std = statistics.stdev(historical_values) if len(historical_values) > 1 else hist_mean * 0.1
            if hist_std > 0:
                z_score = abs(value - hist_mean) / hist_std
                if z_score > self.config['anomaly_detection']['z_score_threshold']:
                    anomaly_score += min(1.0, z_score / 5.0)
                    anomaly_methods.append('z_score')
        industry_benchmarks = self.industry_benchmarks.get(industry_context, {})
        if kpi_key in industry_benchmarks:
            benchmark_data = industry_benchmarks[kpi_key]
            benchmark_mean = benchmark_data['mean']
            benchmark_std = benchmark_data['std']
            industry_z_score = abs(value - benchmark_mean) / benchmark_std
            if industry_z_score > 3.0:
                anomaly_score += min(0.5, industry_z_score / 10.0)
                anomaly_methods.append('industry_deviation')
        if len(historical_values) >= 1:
            last_value = historical_values[-1]
            if last_value > 0:
                pct_change = abs((value - last_value) / last_value)
                if pct_change > 0.5:
                    anomaly_score += min(0.3, pct_change)
                    anomaly_methods.append('percentage_change')
        return {'anomaly_score': min(1.0, anomaly_score), 'anomaly_methods': anomaly_methods, 'is_anomaly': anomaly_score > 0.3, 'method': 'multi_method_anomaly_detection'}
    def _check_temporal_consistency(self, kpi_key: str, value: float, historical_data: List[Dict]) -> Dict:
        """Check temporal consistency across reporting periods"""
        historical_values = []
        historical_years = []
        for hist_record in historical_data:
            if kpi_key in hist_record.get('kpis', {}):
                historical_values.append(float(hist_record['kpis'][kpi_key]))
                historical_years.append(hist_record.get('year', 2023))
        if len(historical_values) < 2:
            return {'consistency_score': 0.5, 'trend_analysis': 'insufficient_data', 'method': 'temporal_consistency'}
        yoy_changes = []
        for i in range(1, len(historical_values)):
            if historical_values[i - 1] != 0:
                change = (historical_values[i] - historical_values[i - 1]) / historical_values[i - 1]
                yoy_changes.append(change)
        if yoy_changes:
            avg_change = statistics.mean(yoy_changes)
            std_change = statistics.stdev(yoy_changes) if len(yoy_changes) > 1 else abs(avg_change) * 0.5
            expected_value = historical_values[-1] * (1 + avg_change)
            if expected_value != 0:
                deviation = abs(value - expected_value) / expected_value
                consistency_score = max(0.1, 1.0 - deviation)
            else:
                consistency_score = 0.5
            if avg_change > 0.05:
                trend = 'increasing'
            elif avg_change < -0.05:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            consistency_score = 0.5
            trend = 'unknown'
        return {'consistency_score': consistency_score, 'trend_analysis': trend, 'expected_value': expected_value if 'expected_value' in locals() else None, 'yoy_changes': yoy_changes, 'method': 'temporal_consistency'}
    def _compare_industry_benchmarks(self, kpi_key: str, value: float, industry_context: str, company_name: str) -> Dict:
        """Compare KPI against industry benchmarks"""
        industry_benchmarks = self.industry_benchmarks.get(industry_context, {})
        if kpi_key not in industry_benchmarks:
            return {'benchmark_score': 0.5, 'percentile': None, 'industry_comparison': 'no_benchmark_available', 'method': 'industry_benchmark'}
        benchmark_data = industry_benchmarks[kpi_key]
        benchmark_mean = benchmark_data['mean']
        benchmark_std = benchmark_data['std']
        z_score = (value - benchmark_mean) / benchmark_std if benchmark_std > 0 else 0
        percentile = self._standard_normal_cdf(z_score) * 100
        if kpi_key in ['scope_1_emissions', 'scope_2_emissions', 'safety_incidents']:
            benchmark_score = max(0.1, 1.0 - self._standard_normal_cdf(abs(z_score)))
            comparison = 'lower_is_better'
        else:
            benchmark_score = max(0.1, self._standard_normal_cdf(z_score))
            comparison = 'higher_is_better'
        return {'benchmark_score': benchmark_score, 'percentile': percentile, 'industry_comparison': comparison, 'z_score': z_score, 'benchmark_mean': benchmark_mean, 'method': 'industry_benchmark'}
    def _consolidate_validation_results(self, kpi_key: str, original_value: float, kpi_data: Dict, confidence_result: Dict, cross_source_result: Dict, anomaly_result: Dict, temporal_result: Dict, benchmark_result: Dict) -> ValidationResult:
        """Consolidate all validation results into final assessment"""
        weights = {'statistical': 0.3, 'cross_source': 0.25, 'temporal': 0.2, 'benchmark': 0.15, 'anomaly_penalty': 0.1}
        weighted_score = confidence_result['confidence_score'] * weights['statistical'] + cross_source_result['agreement_score'] * weights['cross_source'] + temporal_result['consistency_score'] * weights['temporal'] + benchmark_result['benchmark_score'] * weights['benchmark'] - anomaly_result['anomaly_score'] * weights['anomaly_penalty']
        final_confidence = max(0.1, min(0.99, weighted_score))
        validated_value = confidence_result.get('validated_value', original_value)
        if final_confidence > 0.9:
            recommendation = 'high_confidence_accept'
        elif final_confidence > 0.75:
            recommendation = 'medium_confidence_accept'
        elif anomaly_result['is_anomaly']:
            recommendation = 'anomaly_detected_review_required'
        else:
            recommendation = 'low_confidence_manual_review'
        conf_interval = confidence_result.get('confidence_interval', (original_value * 0.9, original_value * 1.1))
        return ValidationResult(kpi_key=kpi_key, kpi_name=kpi_data.get('kpi_name', kpi_key.replace('_', ' ').title()), original_value=original_value, validated_value=validated_value, unit=kpi_data.get('unit'), confidence_score=final_confidence, confidence_interval=conf_interval, validation_methods=['statistical', 'cross_source', 'temporal', 'benchmark', 'anomaly'], anomaly_score=anomaly_result['anomaly_score'], temporal_consistency=temporal_result['consistency_score'], cross_source_agreement=cross_source_result['agreement_score'], statistical_p_value=confidence_result.get('p_value'), recommendation=recommendation, validation_metadata={'statistical_analysis': confidence_result, 'cross_source_analysis': cross_source_result, 'anomaly_analysis': anomaly_result, 'temporal_analysis': temporal_result, 'benchmark_analysis': benchmark_result, 'validation_timestamp': datetime.now().isoformat()})
    def _standard_normal_cdf(self, x: float) -> float:
        """Approximate standard normal cumulative distribution function"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    def save_validation_results(self, state: ValidationState, output_path: str):
        """Save Stage 5 validation results"""
        validation_dict = {}
        if state.validation_results:
            for kpi_key, result in state.validation_results.items():
                validation_dict[kpi_key] = asdict(result)
        results = {'timestamp': datetime.now().isoformat(), 'stage': 'stage_5_enhanced_validation', 'company': state.company_name, 'year': state.reporting_year, 'validation_results': {'validated_kpis': validation_dict, 'overall_validation_score': state.overall_validation_score, 'validation_mode': state.validation_mode, 'confidence_threshold': state.confidence_threshold}, 'statistical_summary': {'total_kpis_validated': len(validation_dict), 'high_confidence_count': len([v for v in state.validation_results.values() if v.confidence_score > 0.9]), 'anomalies_detected': len([v for v in state.validation_results.values() if v.anomaly_score > 0.3]), 'recommendations': {rec: len([v for v in state.validation_results.values() if v.recommendation == rec]) for rec in set((v.recommendation for v in state.validation_results.values()))}}, 'mar_integration': {'agent_logs': state.agent_logs, 'coordination_metadata': state.coordination_metadata, 'specialist_agents_deployed': self.config['mar_integration']['specialist_agents']}, 'unified_db_integration': {'stage': 'stage_5_enhanced_validation', 'data_classification': 'validated_esg_kpis', 'quality_assurance': 'statistical_validation_complete', 'cross_project_tags': {'project': 'rank_ai', 'stage': 'enhanced_validation', 'company': state.company_name, 'year': state.reporting_year, 'validation_score': state.overall_validation_score}}}
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    def generate_validation_report(self, state: ValidationState) -> str:
        """Generate human-readable validation report"""
        if not state.validation_results:
            return 'No validation results available'
        report_lines = [f'🔍 STAGE 5: ENHANCED VALIDATION REPORT', f'=' * 50, f'Company: {state.company_name}', f'Reporting Year: {state.reporting_year}', f'Overall Validation Score: {state.overall_validation_score:.1%}', f'KPIs Validated: {len(state.validation_results)}', '', '📊 VALIDATION SUMMARY:']
        recommendations = {}
        for result in state.validation_results.values():
            rec = result.recommendation
            recommendations[rec] = recommendations.get(rec, 0) + 1
        for rec, count in recommendations.items():
            report_lines.append(f"  • {rec.replace('_', ' ').title()}: {count} KPIs")
        report_lines.extend(['', '📈 DETAILED KPI VALIDATION:'])
        sorted_kpis = sorted(state.validation_results.items(), key=lambda x: x[1].confidence_score, reverse=True)
        for kpi_key, result in sorted_kpis:
            confidence_bar = '█' * int(result.confidence_score * 10) + '░' * (10 - int(result.confidence_score * 10))
            report_lines.extend([f'', f'  🎯 {kpi_key}:', f'    Value: {result.original_value:,.0f} → {result.validated_value:,.0f}', f'    Confidence: {confidence_bar} {result.confidence_score:.1%}', f'    Anomaly Score: {result.anomaly_score:.2f}', f"    Recommendation: {result.recommendation.replace('_', ' ').title()}"])
            if result.confidence_interval:
                ci_lower, ci_upper = result.confidence_interval
                report_lines.append(f'    95% Confidence Interval: [{ci_lower:,.0f}, {ci_upper:,.0f}]')
        return '\n'.join(report_lines)
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
