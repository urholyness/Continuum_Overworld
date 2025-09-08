
class BatchTesting50CompaniesAgent:
    """Agent based on BatchTesting50Companies from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\batch_testing_50_companies.py"""
    
    def __init__(self):
        self.name = "BatchTesting50CompaniesAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Comprehensive testing system for 50 companies with real ESG PDFs"""
        """Initialize batch testing system"""
        self.extractor = ExtractorClass()
        self.results = []
        self.companies_tested = 0
        self.start_time = None
        self.test_companies = {'Apple Inc.': 'https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2023.pdf', 'Microsoft Corporation': 'https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE4RNK5', 'Alphabet Inc.': 'https://sustainability.google/reports/environmental-report-2023.pdf', 'Meta Platforms Inc.': 'https://sustainability.fb.com/wp-content/uploads/2023/06/Meta_2022_Sustainability_Report.pdf', 'Amazon.com Inc.': 'https://sustainability.aboutamazon.com/2022-sustainability-report.pdf', 'Tesla Inc.': 'https://www.tesla.com/ns_videos/2022-tesla-impact-report.pdf', 'NVIDIA Corporation': 'https://images.nvidia.com/aem-dam/Solutions/documents/NVIDIA-CSR-Report-FY2023.pdf', 'Intel Corporation': 'https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2022-23-corporate-responsibility-report.pdf', 'Adobe Inc.': 'https://www.adobe.com/content/dam/cc/en/corporate-responsibility/pdfs/Adobe-CSR-Report-2022.pdf', 'Salesforce Inc.': 'https://www.salesforce.com/content/dam/web/en_us/www/documents/legal/Agreements/sustainability/salesforce-sustainability-report-2023.pdf', 'JPMorgan Chase & Co.': 'https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/documents/jpmc-2022-esg-report.pdf', 'Bank of America Corp.': 'https://about.bankofamerica.com/content/dam/boa/about/delivering-responsible-growth.pdf', 'Wells Fargo & Company': 'https://www08.wellsfargomedia.com/assets/pdf/about/corporate-responsibility/reports/2022-csr-report.pdf', 'Goldman Sachs Group Inc.': 'https://www.goldmansachs.com/our-commitments/sustainability/documents/reports/2022-sustainability-report.pdf', 'Morgan Stanley': 'https://www.morganstanley.com/content/dam/msdotcom/sustainability/Morgan-Stanley-2022-Sustainability-Report.pdf', 'Citigroup Inc.': 'https://www.citigroup.com/citi/about/esg/download/2022/Citi-2022-ESG-Report.pdf', 'American Express Company': 'https://about.americanexpress.com/files/doc_library/file/2022-csr-report.pdf', 'BlackRock Inc.': 'https://www.blackrock.com/corporate/literature/publication/blk-annual-stewardship-report-2022.pdf', 'Johnson & Johnson': 'https://healthforhumanityreport.jnj.com/_document/2022-health-for-humanity-report', 'UnitedHealth Group Inc.': 'https://www.unitedhealthgroup.com/content/dam/UHG/PDFs/investors/2022/UNH-2022-sustainability-report.pdf', 'Pfizer Inc.': 'https://www.pfizer.com/sites/default/files/investors/financial_reports/annual_reports/2022/pfizer-2022-esg-report.pdf', 'AbbVie Inc.': 'https://www.abbvie.com/content/dam/abbvie-dotcom/uploads/PDFs/our-science/abbvie-2022-esg-action-report.pdf', 'Merck & Co. Inc.': 'https://www.merck.com/wp-content/uploads/sites/5/2023/06/Merck-2022-Responsibility-Report-2.pdf', 'Bristol-Myers Squibb Co.': 'https://www.bms.com/assets/bms/us/en-us/pdf/our-company/2022-bms-esg-report.pdf', 'Medtronic plc': 'https://www.medtronic.com/content/dam/medtronic-com/global/Corporate/documents/medtronic-integrated-report-2023.pdf', 'Procter & Gamble Co.': 'https://us.pg.com/policies-and-practices/sustainability/pg-2022-citizenship-report.pdf', 'Coca-Cola Company': 'https://www.coca-colacompany.com/content/dam/journey/us/en/reports/coca-cola-business-environmental-social-governance-report-2022.pdf', 'PepsiCo Inc.': 'https://www.pepsico.com/docs/default-source/sustainability-and-esg-topics/2022-pepsico-esg-summary.pdf', 'Nike Inc.': 'https://s3-us-west-2.amazonaws.com/purpose-cms-production01/wp-content/uploads/2023/06/14194404/FY22-Nike-Inc-Impact-Report.pdf', 'Walmart Inc.': 'https://corporate.walmart.com/media-library/document/fy2023-walmart-esg-report/_proxyDocument?id=00000187-a92b-d119-ad8f-bb6b5f8b0000', 'Home Depot Inc.': 'https://corporate.homedepot.com/sites/default/files/2023-04/THD_2022_ESG_Report.pdf', "McDonald's Corporation": 'https://corporate.mcdonalds.com/corpmcd/scale-for-good/our-planet/purpose-led-brands-report.pdf', 'Exxon Mobil Corporation': 'https://corporate.exxonmobil.com/-/media/Global/Files/sustainability-report/publication/2023/2023-sustainability-report.pdf', 'Chevron Corporation': 'https://www.chevron.com/-/media/chevron/sustainability/documents/Chevron_Sustainability_Report_2022.pdf', 'ConocoPhillips': 'https://static.conocophillips.com/files/resources/conocophillips-2022-sustainability-report.pdf', 'Kinder Morgan Inc.': 'https://ir.kindermorgan.com/static-files/c8f3b3e5-d8b7-4b5a-8e7d-9f8f7a8f8e6f', 'NextEra Energy Inc.': 'https://www.nexteraenergy.com/content/dam/nee/us/en/pdf/NextEra_Energy_2022_Sustainability_Report.pdf', 'General Electric Company': 'https://www.ge.com/sites/default/files/GE_Sustainability_Report_2022.pdf', 'Boeing Company': 'https://www.boeing.com/resources/boeingdotcom/principles/environment/pdf/2022-boeing-environmental-report.pdf', 'Caterpillar Inc.': 'https://www.caterpillar.com/en/company/sustainability/sustainability-report.html', '3M Company': 'https://multimedia.3m.com/mws/media/2145503O/3m-2022-sustainability-report.pdf', 'Honeywell International Inc.': 'https://www.honeywell.com/content/dam/honeywell/files/doc/Honeywell_2022_Sustainability_Report.pdf', 'Verizon Communications Inc.': 'https://www.verizon.com/about/sites/default/files/2023-04/Verizon_2022_Responsible_Business_Report.pdf', 'AT&T Inc.': 'https://about.att.com/content/dam/csr/2023/ATT-2022-CSR-Report.pdf', 'T-Mobile US Inc.': 'https://www.t-mobile.com/content/dam/t-mobile/corporate/newsroom/articles/2023/t-mobile-2022-sustainability-report.pdf', 'Amazon.com Inc.': 'https://sustainability.aboutamazon.com/2022-sustainability-report.pdf', 'Costco Wholesale Corporation': 'https://investor.costco.com/static-files/e4b4f2c5-d8b7-4b5a-8e7d-9f8f7a8f8e6f', 'Target Corporation': 'https://corporate.target.com/corporate-responsibility/planet/2022-corporate-responsibility-report', 'General Motors Company': 'https://www.gmsustainability.com/_pdf/resources_and_downloads/GM_2022_SR.pdf', 'Ford Motor Company': 'https://corporate.ford.com/content/dam/corporate/us/en-us/documents/reports/integrated-sustainability-and-financial-report-2022.pdf', 'Lockheed Martin Corporation': 'https://www.lockheedmartin.com/content/dam/lockheed-martin/eo/documents/sustainability/LMT-2022-Sustainability-Report.pdf', 'Raytheon Technologies Corp.': 'https://www.rtx.com/docs/default-source/corporate-responsibility/2022-esg-report.pdf'}
    def process_single_company(self, company: str, pdf_url: str, year: int=None) -> Dict[str, Any]:
        """Process a single company's ESG report with year support"""
        start_time = time.time()
        result = {'company': company, 'pdf_url': pdf_url, 'year': year, 'success': False, 'kpis_extracted': 0, 'greenwashing_score': 0.0, 'flagged_sections': 0, 'processing_time': 0.0, 'error': None, 'metadata': {}}
        try:
            print(f'🔄 Processing {company} for year {year}...')
            ticker = ''.join([c for c in company.upper() if c.isalpha()])[:4]
            kpis, greenwashing = self.extractor.process_pdf_with_metadata(pdf_url, company, ticker, year)
            result['success'] = True
            result['kpis_extracted'] = len(kpis)
            result['processing_time'] = time.time() - start_time
            if greenwashing:
                result['greenwashing_score'] = greenwashing.overall_score
                result['flagged_sections'] = len(greenwashing.flagged_sections)
                result['metadata']['indicator_scores'] = greenwashing.indicator_scores
                result['metadata']['report_name'] = greenwashing.report_name
                result['metadata']['analysis_year'] = greenwashing.analysis_year
            if kpis:
                result['metadata']['sample_kpis'] = [{'name': kpi.kpi_name, 'value': kpi.kpi_value, 'unit': kpi.kpi_unit, 'year': kpi.kpi_year, 'page': kpi.page_number, 'confidence': kpi.confidence_score} for kpi in kpis[:5]]
                avg_confidence = sum((kpi.confidence_score for kpi in kpis)) / len(kpis)
                result['metadata']['avg_confidence'] = avg_confidence
                env_kpis = len([k for k in kpis if 'carbon' in k.kpi_name.lower() or 'energy' in k.kpi_name.lower() or 'water' in k.kpi_name.lower()])
                social_kpis = len([k for k in kpis if 'diversity' in k.kpi_name.lower() or 'safety' in k.kpi_name.lower()])
                governance_kpis = len([k for k in kpis if 'board' in k.kpi_name.lower() or 'ethics' in k.kpi_name.lower()])
                result['metadata']['kpi_categories'] = {'environmental': env_kpis, 'social': social_kpis, 'governance': governance_kpis}
            self.extractor.save_results_to_database(kpis, greenwashing)
            print(f"✅ {company} ({year}): {len(kpis)} KPIs, GW Score: {result['greenwashing_score']:.1f}")
        except Exception as e:
            result['error'] = str(e)
            result['processing_time'] = time.time() - start_time
            print(f'❌ {company} ({year}): Error - {str(e)[:100]}...')
        return result
    def run_batch_testing_with_years(self, max_workers: int=3, test_subset: int=None) -> List[Dict[str, Any]]:
        """Run batch testing on companies with multi-year support using CSV data"""
        print('🚀 Starting Batch Testing with Multi-Year Support')
        print('=' * 60)
        self.start_time = time.time()
        import pandas as pd
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_companies.csv')
        df = pd.read_csv(csv_path)
        test_items = []
        for _, row in df.iterrows():
            company = row['company']
            years = row.get('report_years', '2024').split(',')
            for year in years:
                year = int(year.strip())
                test_items.append({'company': company, 'year': year, 'url': row['esg_report_url']})
        if test_subset:
            test_items = test_items[:test_subset]
            print(f'📊 Testing subset: {test_subset} items')
        print(f'📊 Total test items (company-year pairs): {len(test_items)}')
        print(f'🔧 Max concurrent workers: {max_workers}')
        print()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {executor.submit(self.process_single_company, item['company'], item['url'], item['year']): item for item in test_items}
            for future in concurrent.futures.as_completed(future_to_item):
                result = future.result()
                self.results.append(result)
                self.companies_tested += 1
                progress = self.companies_tested / len(test_items) * 100
                elapsed = time.time() - self.start_time
                eta = elapsed / self.companies_tested * (len(test_items) - self.companies_tested)
                print(f'📈 Progress: {self.companies_tested}/{len(test_items)} ({progress:.1f}%) | ETA: {eta / 60:.1f}m | Elapsed: {elapsed / 60:.1f}m')
        return self.results
    def run_batch_testing(self, max_workers: int=3, test_subset: int=None) -> List[Dict[str, Any]]:
        """Run batch testing on all companies (legacy method)"""
        print('🚀 Starting Batch Testing of 50 Companies')
        print('=' * 60)
        self.start_time = time.time()
        companies_to_test = list(self.test_companies.items())
        if test_subset:
            companies_to_test = companies_to_test[:test_subset]
            print(f'📊 Testing subset: {test_subset} companies')
        print(f'📊 Total companies to test: {len(companies_to_test)}')
        print(f'🔧 Max concurrent workers: {max_workers}')
        print()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_company = {executor.submit(self.process_single_company, company, url): company for company, url in companies_to_test}
            for future in concurrent.futures.as_completed(future_to_company):
                result = future.result()
                self.results.append(result)
                self.companies_tested += 1
                progress = self.companies_tested / len(companies_to_test) * 100
                elapsed = time.time() - self.start_time
                eta = elapsed / self.companies_tested * (len(companies_to_test) - self.companies_tested)
                print(f'📈 Progress: {self.companies_tested}/{len(companies_to_test)} ({progress:.1f}%) | ETA: {eta / 60:.1f}m | Elapsed: {elapsed / 60:.1f}m')
        return self.results
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive testing report"""
        if not self.results:
            return {'error': 'No results to analyze'}
        total_time = time.time() - self.start_time if self.start_time else 0
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        success_rate = len(successful_tests) / len(self.results) * 100
        total_kpis = sum((r['kpis_extracted'] for r in successful_tests))
        avg_processing_time = sum((r['processing_time'] for r in self.results)) / len(self.results)
        avg_greenwashing_score = sum((r['greenwashing_score'] for r in successful_tests)) / len(successful_tests) if successful_tests else 0
        kpi_distribution = {}
        confidence_scores = []
        greenwashing_scores = []
        for result in successful_tests:
            if 'sample_kpis' in result.get('metadata', {}):
                for kpi in result['metadata']['sample_kpis']:
                    kpi_name = kpi['name']
                    kpi_distribution[kpi_name] = kpi_distribution.get(kpi_name, 0) + 1
                    confidence_scores.append(kpi['confidence'])
            if result['greenwashing_score'] > 0:
                greenwashing_scores.append(result['greenwashing_score'])
        high_risk_companies = len([r for r in successful_tests if r['greenwashing_score'] > 75])
        medium_risk_companies = len([r for r in successful_tests if 50 <= r['greenwashing_score'] <= 75])
        low_risk_companies = len([r for r in successful_tests if r['greenwashing_score'] < 50])
        top_kpi_extractors = sorted(successful_tests, key=lambda x: x['kpis_extracted'], reverse=True)[:5]
        highest_greenwashing = sorted(successful_tests, key=lambda x: x['greenwashing_score'], reverse=True)[:5]
        fastest_processing = sorted(successful_tests, key=lambda x: x['processing_time'])[:5]
        error_types = {}
        for result in failed_tests:
            error = result.get('error', 'Unknown error')
            error_type = error.split(':')[0] if ':' in error else error[:50]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        report = {'timestamp': datetime.now().isoformat(), 'execution_summary': {'total_companies_tested': len(self.results), 'successful_tests': len(successful_tests), 'failed_tests': len(failed_tests), 'success_rate_percentage': success_rate, 'total_processing_time_minutes': total_time / 60, 'average_processing_time_seconds': avg_processing_time}, 'kpi_analysis': {'total_kpis_extracted': total_kpis, 'average_kpis_per_company': total_kpis / len(successful_tests) if successful_tests else 0, 'kpi_type_distribution': dict(sorted(kpi_distribution.items(), key=lambda x: x[1], reverse=True)[:10]), 'average_confidence_score': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0, 'confidence_range': {'min': min(confidence_scores) if confidence_scores else 0, 'max': max(confidence_scores) if confidence_scores else 0}}, 'greenwashing_analysis': {'average_greenwashing_score': avg_greenwashing_score, 'score_distribution': {'high_risk_companies': high_risk_companies, 'medium_risk_companies': medium_risk_companies, 'low_risk_companies': low_risk_companies}, 'score_range': {'min': min(greenwashing_scores) if greenwashing_scores else 0, 'max': max(greenwashing_scores) if greenwashing_scores else 0}}, 'performance_metrics': {'top_kpi_extractors': [{'company': r['company'], 'kpis': r['kpis_extracted']} for r in top_kpi_extractors], 'highest_greenwashing_risk': [{'company': r['company'], 'score': r['greenwashing_score']} for r in highest_greenwashing], 'fastest_processing': [{'company': r['company'], 'time_seconds': r['processing_time']} for r in fastest_processing]}, 'error_analysis': {'error_types': error_types, 'failed_companies': [{'company': r['company'], 'error': r['error'][:100]} for r in failed_tests[:10]]}, 'detailed_results': self.results}
        return report
    def save_results(self, filename: str=None):
        """Save comprehensive results to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'batch_testing_50_companies_{timestamp}.json'
        report = self.generate_comprehensive_report()
        filepath = os.path.join(os.path.dirname(__file__), '..', 'tests', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f'📄 Comprehensive report saved to: {filepath}')
        return filepath
    def print_summary(self):
        """Print testing summary"""
        if not self.results:
            print('No results to summarize')
            return
        report = self.generate_comprehensive_report()
        print('\n' + '=' * 60)
        print('📊 BATCH TESTING SUMMARY - 50 COMPANIES')
        print('=' * 60)
        exec_summary = report['execution_summary']
        print(f"✅ Success Rate: {exec_summary['success_rate_percentage']:.1f}% ({exec_summary['successful_tests']}/{exec_summary['total_companies_tested']})")
        print(f"⏱️  Total Time: {exec_summary['total_processing_time_minutes']:.1f} minutes")
        print(f"📊 Avg Processing: {exec_summary['average_processing_time_seconds']:.1f} seconds/company")
        kpi_analysis = report['kpi_analysis']
        print(f'\n📋 KPI EXTRACTION:')
        print(f"   Total KPIs: {kpi_analysis['total_kpis_extracted']}")
        print(f"   Avg per Company: {kpi_analysis['average_kpis_per_company']:.1f}")
        print(f"   Avg Confidence: {kpi_analysis['average_confidence_score']:.2f}")
        gw_analysis = report['greenwashing_analysis']
        print(f'\n🚨 GREENWASHING ANALYSIS:')
        print(f"   Avg Score: {gw_analysis['average_greenwashing_score']:.1f}")
        print(f"   High Risk: {gw_analysis['score_distribution']['high_risk_companies']} companies")
        print(f"   Medium Risk: {gw_analysis['score_distribution']['medium_risk_companies']} companies")
        print(f"   Low Risk: {gw_analysis['score_distribution']['low_risk_companies']} companies")
        print(f'\n🏆 TOP PERFORMERS:')
        for i, company in enumerate(report['performance_metrics']['top_kpi_extractors'][:3], 1):
            print(f"   {i}. {company['company']}: {company['kpis']} KPIs")
        if report['error_analysis']['error_types']:
            print(f"\n⚠️  ERRORS ({len(report['error_analysis']['failed_companies'])} companies):")
            for error_type, count in list(report['error_analysis']['error_types'].items())[:3]:
                print(f'   {error_type}: {count} occurrences')
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
