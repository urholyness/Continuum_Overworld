
class _save_extraction_resultAgent:
    """Agent based on _save_extraction_result from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\kpi_extractor.py"""
    
    def __init__(self):
        self.name = "_save_extraction_resultAgent"
        self.category = "extraction"
        self.status = "active"
    
    def extract(self, data, **kwargs):
        """Extraction functionality"""
            """Save extraction result to database"""
    try:
        conn = self.get_db_connection()
        cursor = conn.cursor()
        if self.is_sqlite:
            cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extracted_kpis (\n                        id INTEGER PRIMARY KEY AUTOINCREMENT,\n                        company TEXT,\n                        ticker TEXT,\n                        kpi_name TEXT,\n                        kpi_value REAL,\n                        kpi_unit TEXT,\n                        kpi_year INTEGER,\n                        confidence_score REAL,\n                        source_url TEXT,\n                        extraction_method TEXT,\n                        raw_text TEXT,\n                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
        else:
            cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extracted_kpis (\n                        id SERIAL PRIMARY KEY,\n                        company VARCHAR(255),\n                        ticker VARCHAR(50),\n                        kpi_name VARCHAR(255),\n                        kpi_value FLOAT,\n                        kpi_unit VARCHAR(100),\n                        kpi_year INTEGER,\n                        confidence_score FLOAT,\n                        source_url TEXT,\n                        extraction_method VARCHAR(50),\n                        raw_text TEXT,\n                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
        for kpi in result.kpis_extracted:
            if self.is_sqlite:
                cursor.execute('\n                        INSERT INTO extracted_kpis \n                        (company, ticker, kpi_name, kpi_value, kpi_unit, kpi_year, \n                         confidence_score, source_url, extraction_method, raw_text)\n                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n                    ', (kpi.company, kpi.ticker, kpi.kpi_name, kpi.kpi_value, kpi.kpi_unit, kpi.kpi_year, kpi.confidence_score, kpi.source_url, kpi.extraction_method, kpi.raw_text))
            else:
                cursor.execute('\n                        INSERT INTO extracted_kpis \n                        (company, ticker, kpi_name, kpi_value, kpi_unit, kpi_year, \n                         confidence_score, source_url, extraction_method, raw_text)\n                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n                    ', (kpi.company, kpi.ticker, kpi.kpi_name, kpi.kpi_value, kpi.kpi_unit, kpi.kpi_year, kpi.confidence_score, kpi.source_url, kpi.extraction_method, kpi.raw_text))
        if self.is_sqlite:
            cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extraction_log (\n                        id INTEGER PRIMARY KEY AUTOINCREMENT,\n                        company TEXT,\n                        ticker TEXT,\n                        source_url TEXT,\n                        kpis_count INTEGER,\n                        processing_time REAL,\n                        success INTEGER,\n                        error_message TEXT,\n                        document_pages INTEGER,\n                        text_length INTEGER,\n                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
            cursor.execute('\n                    INSERT INTO extraction_log \n                    (company, ticker, source_url, kpis_count, processing_time, \n                     success, error_message, document_pages, text_length)\n                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)\n                ', (result.company, result.ticker, result.source_url, len(result.kpis_extracted), result.processing_time, 1 if result.success else 0, result.error_message, result.document_pages, result.text_length))
        else:
            cursor.execute('\n                    CREATE TABLE IF NOT EXISTS extraction_log (\n                        id SERIAL PRIMARY KEY,\n                        company VARCHAR(255),\n                        ticker VARCHAR(50),\n                        source_url TEXT,\n                        kpis_count INTEGER,\n                        processing_time FLOAT,\n                        success BOOLEAN,\n                        error_message TEXT,\n                        document_pages INTEGER,\n                        text_length INTEGER,\n                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                    )\n                ')
            cursor.execute('\n                    INSERT INTO extraction_log \n                    (company, ticker, source_url, kpis_count, processing_time, \n                     success, error_message, document_pages, text_length)\n                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)\n                ', (result.company, result.ticker, result.source_url, len(result.kpis_extracted), result.processing_time, result.success, result.error_message, result.document_pages, result.text_length))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f'Error saving extraction result: {e}')
        
    def run(self, data, **kwargs):
        """Main execution method"""
        return self.extract(data, **kwargs)
