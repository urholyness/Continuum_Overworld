
class SurveyAutomationSystemAgent:
    """Agent based on SurveyAutomationSystem from ..\Archieves\Stat-R_AI\esg_kpi_mvp\src\survey_automation.py"""
    
    def __init__(self):
        self.name = "SurveyAutomationSystemAgent"
        self.category = "automation"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """Complete survey automation system for ESG opinion collection"""
        """Initialize the survey automation system"""
        self.redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=int(os.getenv('REDIS_DB', 0)))
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.openai_available = bool(openai.api_key)
        self.nlp_available = False
        try:
            self.nlp = spacy.load('en_core_web_sm')
            self.nlp_available = True
            logger.info('spaCy NLP model loaded successfully')
        except OSError:
            logger.warning('spaCy model not found. Install with: python -m spacy download en_core_web_sm')
            self.nlp = None
        self.adult_search_queries = ['site:linkedin.com ESG professional sustainability -student -intern -kids -teen', 'site:reddit.com/r/investing ESG discussion adult professional -teenager', 'ESG analyst professional adult opinion -student -child -teen', 'sustainable investing professional adult -college -university', 'corporate responsibility professional adult opinion']
        self.bot_patterns = ['^(..)\\1{3,}', '^(.)\\1{10,}', '\\b(test|spam|fake)\\b', '^[a-z]{1,3}$']
        self.app = Flask(__name__)
        self.setup_routes()
        self.init_database()
        self.esg_questions = [SurveyQuestion(id='esg_overall', question_type='likert', question_text="How would you rate this company's overall ESG performance?", options=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'], category='overall'), SurveyQuestion(id='environmental_impact', question_type='likert', question_text='How environmentally responsible is this company?', options=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'], category='environmental'), SurveyQuestion(id='social_impact', question_type='likert', question_text='How well does this company treat its employees and communities?', options=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'], category='social'), SurveyQuestion(id='governance_quality', question_type='likert', question_text="How would you rate this company's leadership and governance?", options=['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'], category='governance'), SurveyQuestion(id='investment_likelihood', question_type='rating', question_text='How likely are you to invest in this company based on ESG factors?', options=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], category='investment'), SurveyQuestion(id='additional_comments', question_type='text', question_text="Any additional comments about this company's ESG practices?", required=False, category='feedback')]
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    def init_database(self):
        """Initialize database tables for survey system"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS surveys (\n                    survey_id VARCHAR(50) PRIMARY KEY,\n                    title VARCHAR(255),\n                    description TEXT,\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    questions JSONB,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    active BOOLEAN DEFAULT TRUE,\n                    target_responses INTEGER DEFAULT 100\n                )\n            ')
            cursor.execute("\n                CREATE TABLE IF NOT EXISTS survey_responses (\n                    response_id VARCHAR(50) PRIMARY KEY,\n                    survey_id VARCHAR(50),\n                    company VARCHAR(255),\n                    ticker VARCHAR(50),\n                    respondent_id VARCHAR(50),\n                    responses JSONB,\n                    completion_time FLOAT,\n                    start_time TIMESTAMP,\n                    end_time TIMESTAMP,\n                    quality_score FLOAT,\n                    sentiment_score FLOAT,\n                    cleaned_responses JSONB,\n                    source TEXT DEFAULT 'web',\n                    confidence FLOAT DEFAULT 0.8,\n                    is_duplicate BOOLEAN DEFAULT FALSE,\n                    is_bot BOOLEAN DEFAULT FALSE,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id)\n                )\n            ")
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS survey_targets (\n                    target_id SERIAL PRIMARY KEY,\n                    company VARCHAR(255),\n                    target_platform VARCHAR(100),\n                    target_url TEXT,\n                    target_description TEXT,\n                    contacted BOOLEAN DEFAULT FALSE,\n                    response_received BOOLEAN DEFAULT FALSE,\n                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                )\n            ')
            conn.commit()
            cursor.close()
            conn.close()
            logger.info('Database initialized successfully')
        except Exception as e:
            logger.error(f'Error initializing database: {e}')
    def create_survey(self, company: str, ticker: str=None, custom_questions: Optional[List[SurveyQuestion]]=None) -> str:
        """
        Create a new survey for a company
        Args:
            company (str): Company name
            custom_questions (Optional[List[SurveyQuestion]]): Custom questions (uses default if None)
        Returns:
            str: Survey ID
        """
        survey_id = str(uuid.uuid4())
        questions = custom_questions or self.esg_questions
        survey = Survey(survey_id=survey_id, title=f'ESG Opinion Survey: {company}', description=f"Share your opinion about {company}'s Environmental, Social, and Governance practices", company=company, questions=questions, created_at=datetime.now())
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO surveys (survey_id, title, description, company, ticker, questions)\n                VALUES (%s, %s, %s, %s, %s, %s)\n            ', (survey.survey_id, survey.title, survey.description, survey.company, ticker or self._extract_ticker(company), json.dumps([asdict(q) for q in survey.questions])))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f'Created survey {survey_id} for {company}')
            return survey_id
        except Exception as e:
            logger.error(f'Error creating survey: {e}')
    def find_survey_targets(self, company: str, target_count: int=50) -> List[Dict]:
        """
        Find potential survey respondents using Google Custom Search
        Args:
            company (str): Company name
            target_count (int): Number of targets to find
        Returns:
            List[Dict]: List of potential respondents
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning('Google API credentials not available for targeting')
            return []
        try:
            service = build('customsearch', 'v1', developerKey=self.google_api_key)
            search_queries = self.adult_search_queries.copy()
            company_queries = [f'site:linkedin.com ESG professional {company} -student -intern', f'site:reddit.com/r/investing ESG {company} adult -teenager', f'ESG analyst {company} professional opinion -college']
            search_queries.extend(company_queries)
            targets = []
            for query in search_queries[:3]:
                try:
                    result = service.cse().list(q=query, cx=self.google_cse_id, num=10).execute()
                    for item in result.get('items', []):
                        targets.append({'company': company, 'target_platform': self._extract_platform(item['link']), 'target_url': item['link'], 'target_description': item.get('snippet', ''), 'title': item.get('title', '')})
                    time.sleep(0.1)
                except Exception as e:
                    logger.warning(f'Search query failed: {e}')
                    continue
            if targets:
                self._save_targets_to_db(targets)
            logger.info(f'Found {len(targets)} potential respondents for {company}')
            return targets[:target_count]
        except Exception as e:
            logger.error(f'Error finding survey targets: {e}')
            return []
    def _extract_platform(self, url: str) -> str:
        """Extract platform name from URL"""
        if 'linkedin.com' in url:
            return 'linkedin'
        elif 'reddit.com' in url:
            return 'reddit'
        elif 'twitter.com' in url:
            return 'twitter'
        else:
            return 'other'
    def _save_targets_to_db(self, targets: List[Dict]):
        """Save targets to database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            for target in targets:
                cursor.execute('\n                    INSERT INTO survey_targets (company, target_platform, target_url, target_description)\n                    VALUES (%s, %s, %s, %s)\n                    ON CONFLICT DO NOTHING\n                ', (target['company'], target['target_platform'], target['target_url'], target['target_description']))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f'Error saving targets to database: {e}')
    def _extract_ticker(self, company: str) -> str:
        """Extract or generate ticker symbol from company name"""
        if 'Inc.' in company:
            ticker = company.replace(' Inc.', '').replace(' ', '')[:4].upper()
        elif 'Corp' in company:
            ticker = company.replace(' Corp', '').replace(' ', '')[:4].upper()
        elif 'Corporation' in company:
            ticker = company.replace(' Corporation', '').replace(' ', '')[:4].upper()
        else:
            ticker = company.replace(' ', '')[:4].upper()
        return ticker
    def _detect_bot_response(self, responses: Dict[str, Any]) -> bool:
        """Detect if response is likely from a bot"""
        for response_text in responses.values():
            if isinstance(response_text, str):
                for pattern in self.bot_patterns:
                    if re.search(pattern, response_text.lower()):
                        return True
                if len(response_text.strip()) < 5:
                    return True
                words = response_text.lower().split()
                if len(words) > 3 and len(set(words)) <= 2:
                    return True
        return False
    def _detect_duplicate_response(self, responses: Dict[str, Any], survey_id: str) -> bool:
        """Detect if response is a duplicate"""
        try:
            response_hash = hashlib.md5(json.dumps(responses, sort_keys=True).encode()).hexdigest()
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                SELECT COUNT(*) FROM survey_responses \n                WHERE survey_id = %s AND MD5(responses::text) = %s\n            ', (survey_id, response_hash))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count > 0
        except Exception as e:
            logger.error(f'Error checking for duplicates: {e}')
            return False
    def _calculate_sentiment_score(self, responses: Dict[str, Any]) -> float:
        """Calculate sentiment score for responses using local NLP or OpenAI"""
        try:
            text_responses = []
            for value in responses.values():
                if isinstance(value, str) and len(value) > 10:
                    text_responses.append(value)
            if not text_responses:
                return 0.5
            combined_text = ' '.join(text_responses)
            if self.openai_available:
                try:
                    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': f'Analyze sentiment of this ESG survey response (0.0=very negative, 0.5=neutral, 1.0=very positive): {combined_text}'}], max_tokens=10, temperature=0.1)
                    sentiment_text = response.choices[0].message.content.strip()
                    sentiment_score = float(re.findall('\\d+\\.\\d+', sentiment_text)[0])
                    return max(0.0, min(1.0, sentiment_score))
                except Exception as e:
                    logger.warning(f'OpenAI sentiment analysis failed: {e}')
            blob = TextBlob(combined_text)
            sentiment_score = (blob.sentiment.polarity + 1) / 2
            return sentiment_score
        except Exception as e:
            logger.error(f'Error calculating sentiment: {e}')
            return 0.5
    def _clean_responses_enhanced(self, responses: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhanced response cleaning with local NLP fallback"""
        if not responses:
        try:
            if self.openai_available:
                return self._clean_responses(responses)
            cleaned = {}
            for key, value in responses.items():
                if isinstance(value, str) and len(value) > 10:
                    cleaned_text = re.sub('[^\\w\\s]', ' ', value)
                    cleaned_text = re.sub('\\s+', ' ', cleaned_text)
                    cleaned_text = cleaned_text.strip().title()
                    cleaned[key] = {'original': value, 'cleaned': cleaned_text, 'length': len(cleaned_text), 'confidence': 0.7}
                else:
                    cleaned[key] = value
            return cleaned
        except Exception as e:
            logger.error(f'Error in enhanced cleaning: {e}')
            return responses
    def setup_routes(self):
        """Setup Flask routes for survey serving"""
        @self.app.route('/survey/<survey_id>')
        def serve_survey(survey_id):
            """Serve survey to respondents"""
            try:
                survey_data = self.get_survey(survey_id)
                if not survey_data:
                    return ('Survey not found', 404)
                html = self._generate_survey_html(survey_data)
                return html
            except Exception as e:
                logger.error(f'Error serving survey: {e}')
                return ('Error loading survey', 500)
        @self.app.route('/submit/<survey_id>', methods=['POST'])
        def submit_response(survey_id):
            """Handle survey response submission"""
            try:
                response_data = request.json
                response_id = self.save_response(survey_id, response_data)
                if response_id:
                    return jsonify({'status': 'success', 'response_id': response_id})
                else:
                    return (jsonify({'status': 'error', 'message': 'Failed to save response'}), 400)
            except Exception as e:
                logger.error(f'Error submitting response: {e}')
                return (jsonify({'status': 'error', 'message': str(e)}), 500)
    def get_survey(self, survey_id: str) -> Optional[Dict]:
        """Get survey data by ID"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('\n                SELECT * FROM surveys WHERE survey_id = %s AND active = TRUE\n            ', (survey_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                return dict(result)
        except Exception as e:
            logger.error(f'Error getting survey: {e}')
    def _generate_survey_html(self, survey_data: Dict) -> str:
        """Generate HTML for survey presentation"""
        questions_json = json.loads(survey_data['questions'])
        html_template = '\n        <!DOCTYPE html>\n        <html>\n        <head>\n            <title>{{ title }}</title>\n            <style>\n                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }\n                .question { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }\n                .question h3 { margin-top: 0; }\n                .likert { display: flex; justify-content: space-between; align-items: center; }\n                .likert label { margin: 0 10px; text-align: center; }\n                input[type="radio"] { margin: 5px; }\n                textarea { width: 100%; height: 100px; }\n                button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }\n                button:hover { background: #005a8b; }\n                .progress { background: #f0f0f0; height: 20px; border-radius: 10px; margin: 20px 0; }\n                .progress-bar { background: #007cba; height: 100%; border-radius: 10px; width: 0%; }\n            </style>\n        </head>\n        <body>\n            <h1>{{ title }}</h1>\n            <p>{{ description }}</p>\n            \n            <div class="progress">\n                <div class="progress-bar" id="progress-bar"></div>\n            </div>\n            \n            <form id="survey-form">\n                {% for question in questions %}\n                <div class="question">\n                    <h3>{{ question.question_text }}</h3>\n                    \n                    {% if question.question_type == \'likert\' %}\n                    <div class="likert">\n                        {% for option in question.options %}\n                        <label>\n                            <input type="radio" name="{{ question.id }}" value="{{ option }}" \n                                   {% if question.required %}required{% endif %}>\n                            {{ option }}\n                        </label>\n                        {% endfor %}\n                    </div>\n                    \n                    {% elif question.question_type == \'text\' %}\n                    <textarea name="{{ question.id }}" placeholder="Enter your response..."\n                              {% if question.required %}required{% endif %}></textarea>\n                    \n                    {% elif question.question_type == \'rating\' %}\n                    <div class="likert">\n                        {% for option in question.options %}\n                        <label>\n                            <input type="radio" name="{{ question.id }}" value="{{ option }}"\n                                   {% if question.required %}required{% endif %}>\n                            {{ option }}\n                        </label>\n                        {% endfor %}\n                    </div>\n                    {% endif %}\n                </div>\n                {% endfor %}\n                \n                <button type="submit">Submit Survey</button>\n            </form>\n            \n            <script>\n                const form = document.getElementById(\'survey-form\');\n                const progressBar = document.getElementById(\'progress-bar\');\n                const questions = document.querySelectorAll(\'.question\');\n                \n                // Track progress\n                function updateProgress() {\n                    const totalQuestions = questions.length;\n                    let answeredQuestions = 0;\n                    \n                    questions.forEach(question => {\n                        const inputs = question.querySelectorAll(\'input, textarea\');\n                        for (let input of inputs) {\n                            if (input.type === \'radio\' && input.checked) {\n                                answeredQuestions++;\n                                break;\n                            } else if (input.type === \'textarea\' && input.value.trim()) {\n                                answeredQuestions++;\n                                break;\n                            }\n                        }\n                    });\n                    \n                    const progress = (answeredQuestions / totalQuestions) * 100;\n                    progressBar.style.width = progress + \'%\';\n                }\n                \n                // Add event listeners\n                form.addEventListener(\'input\', updateProgress);\n                form.addEventListener(\'change\', updateProgress);\n                \n                // Handle form submission\n                form.addEventListener(\'submit\', async (e) => {\n                    e.preventDefault();\n                    \n                    const formData = new FormData(form);\n                    const responses = {};\n                    \n                    for (let [key, value] of formData.entries()) {\n                        responses[key] = value;\n                    }\n                    \n                    try {\n                        const response = await fetch(\'/submit/{{ survey_id }}\', {\n                            method: \'POST\',\n                            headers: {\n                                \'Content-Type\': \'application/json\',\n                            },\n                            body: JSON.stringify({\n                                responses: responses,\n                                start_time: sessionStorage.getItem(\'survey_start_time\'),\n                                end_time: new Date().toISOString()\n                            })\n                        });\n                        \n                        if (response.ok) {\n                            document.body.innerHTML = \'<h2>Thank you for your participation!</h2><p>Your responses have been recorded.</p>\';\n                        } else {\n                            alert(\'Error submitting survey. Please try again.\');\n                        }\n                    } catch (error) {\n                        alert(\'Error submitting survey. Please try again.\');\n                    }\n                });\n                \n                // Record start time\n                if (!sessionStorage.getItem(\'survey_start_time\')) {\n                    sessionStorage.setItem(\'survey_start_time\', new Date().toISOString());\n                }\n            </script>\n        </body>\n        </html>\n        '
        html = html_template.replace('{{ title }}', survey_data['title'])
        html = html.replace('{{ description }}', survey_data['description'])
        html = html.replace('{{ survey_id }}', survey_data['survey_id'])
        questions_html = ''
        for question in questions_json:
            questions_html += f"""<div class="question"><h3>{question['question_text']}</h3>"""
            if question['question_type'] == 'likert':
                questions_html += '<div class="likert">'
                for option in question['options']:
                    required = 'required' if question['required'] else ''
                    questions_html += f'''\n                    <label>\n                        <input type="radio" name="{question['id']}" value="{option}" {required}>\n                        {option}\n                    </label>\n                    '''
                questions_html += '</div>'
            elif question['question_type'] == 'text':
                required = 'required' if question['required'] else ''
                questions_html += f'''<textarea name="{question['id']}" placeholder="Enter your response..." {required}></textarea>'''
            questions_html += '</div>'
        html = html.replace('{% for question in questions %}{% endfor %}', questions_html)
        return html
    def save_response(self, survey_id: str, response_data: Dict) -> Optional[str]:
        """Save survey response to database"""
        try:
            response_id = str(uuid.uuid4())
            start_time = datetime.fromisoformat(response_data.get('start_time', '').replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(response_data.get('end_time', '').replace('Z', '+00:00'))
            completion_time = (end_time - start_time).total_seconds()
            responses = response_data['responses']
            is_bot = self._detect_bot_response(responses)
            is_duplicate = self._detect_duplicate_response(responses, survey_id)
            quality_score = self._calculate_quality_score(responses, completion_time)
            sentiment_score = self._calculate_sentiment_score(responses)
            survey_data = self.get_survey(survey_id)
            if not survey_data:
            cleaned_responses = self._clean_responses_enhanced(responses)
            ticker = survey_data.get('ticker') or self._extract_ticker(survey_data['company'])
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO survey_responses \n                (response_id, survey_id, company, ticker, respondent_id, responses, completion_time, \n                 start_time, end_time, quality_score, sentiment_score, cleaned_responses, \n                 source, confidence, is_duplicate, is_bot)\n                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)\n            ', (response_id, survey_id, survey_data['company'], ticker, request.remote_addr, json.dumps(responses), completion_time, start_time, end_time, quality_score, sentiment_score, json.dumps(cleaned_responses) if cleaned_responses else None, 'web', min(quality_score, sentiment_score), is_duplicate, is_bot))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f'Saved response {response_id} for survey {survey_id}')
            return response_id
        except Exception as e:
            logger.error(f'Error saving response: {e}')
    def _calculate_quality_score(self, responses: Dict, completion_time: float) -> float:
        """Calculate quality score for responses"""
        score = 1.0
        if completion_time < 60:
            score *= 0.5
        elif completion_time < 120:
            score *= 0.8
        numeric_responses = []
        for key, value in responses.items():
            if value.isdigit():
                numeric_responses.append(int(value))
        if len(set(numeric_responses)) == 1 and len(numeric_responses) > 2:
            score *= 0.3
        text_responses = [v for v in responses.values() if isinstance(v, str) and len(v) > 10]
        if text_responses:
            avg_length = sum((len(r) for r in text_responses)) / len(text_responses)
            if avg_length > 50:
                score *= 1.2
        return min(score, 1.0)
    def _clean_responses(self, responses: Dict) -> Optional[Dict]:
        """Clean and enhance responses using OpenAI"""
        if not self.openai_available:
        try:
            text_responses = {k: v for k, v in responses.items() if isinstance(v, str) and len(v) > 10}
            if not text_responses:
                return responses
            cleaned = {}
            for key, response in text_responses.items():
                prompt = f'\n                Clean and categorize this ESG survey response. Extract key themes and sentiment.\n                \n                Response: {response}\n                \n                Provide:\n                1. Cleaned text (remove profanity, fix grammar)\n                2. Sentiment (positive/negative/neutral)\n                3. Key themes (environmental, social, governance)\n                4. Confidence score (0-1)\n                \n                Format as JSON.\n                '
                result = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role': 'system', 'content': 'You are an expert at analyzing ESG survey responses.'}, {'role': 'user', 'content': prompt}], max_tokens=200, temperature=0.1)
                cleaned[key] = result.choices[0].message.content.strip()
            final_responses = {**responses, **cleaned}
            return final_responses
        except Exception as e:
            logger.error(f'Error cleaning responses with OpenAI: {e}')
            return responses
    def get_survey_results(self, survey_id: str) -> Dict:
        """Get aggregated survey results"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM surveys WHERE survey_id = %s', (survey_id,))
            survey_data = cursor.fetchone()
            if not survey_data:
                return {}
            cursor.execute('\n                SELECT * FROM survey_responses \n                WHERE survey_id = %s AND quality_score > 0.5\n                ORDER BY created_at DESC\n            ', (survey_id,))
            responses = cursor.fetchall()
            cursor.close()
            conn.close()
            results = {'survey_info': dict(survey_data), 'total_responses': len(responses), 'avg_quality_score': sum((r['quality_score'] for r in responses)) / len(responses) if responses else 0, 'avg_completion_time': sum((r['completion_time'] for r in responses)) / len(responses) if responses else 0, 'response_summary': self._aggregate_responses(responses)}
            return results
        except Exception as e:
            logger.error(f'Error getting survey results: {e}')
            return {}
    def _aggregate_responses(self, responses: List[Dict]) -> Dict:
        """Aggregate survey responses for analysis"""
        if not responses:
            return {}
        aggregated = {}
        for response in responses:
            response_data = json.loads(response['responses'])
            for question_id, answer in response_data.items():
                if question_id not in aggregated:
                    aggregated[question_id] = {}
                if answer not in aggregated[question_id]:
                    aggregated[question_id][answer] = 0
                aggregated[question_id][answer] += 1
        return aggregated
    def integrate_with_esg_rankings(self) -> Dict:
        """Integrate survey data with ESG KPI rankings"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("\n                SELECT \n                    company,\n                    AVG(quality_score) as avg_quality,\n                    COUNT(*) as response_count,\n                    AVG(\n                        CASE \n                            WHEN responses->>'esg_overall' = 'Excellent' THEN 5\n                            WHEN responses->>'esg_overall' = 'Good' THEN 4\n                            WHEN responses->>'esg_overall' = 'Fair' THEN 3\n                            WHEN responses->>'esg_overall' = 'Poor' THEN 2\n                            WHEN responses->>'esg_overall' = 'Very Poor' THEN 1\n                            ELSE 3\n                        END\n                    ) as opinion_score\n                FROM survey_responses\n                WHERE quality_score > 0.5\n                GROUP BY company\n            ")
            survey_scores = cursor.fetchall()
            cursor.execute('\n                SELECT \n                    company,\n                    AVG(kpi_value) as avg_kpi_value,\n                    COUNT(*) as kpi_count\n                FROM extracted_kpis\n                WHERE confidence_score > 0.7\n                GROUP BY company\n            ')
            kpi_scores = cursor.fetchall()
            cursor.close()
            conn.close()
            combined_rankings = {}
            for survey in survey_scores:
                company = survey['company']
                combined_rankings[company] = {'opinion_score': float(survey['opinion_score']) if survey['opinion_score'] else 0, 'response_count': survey['response_count'], 'quality_score': float(survey['avg_quality']) if survey['avg_quality'] else 0, 'kpi_score': 0, 'kpi_count': 0}
            for kpi in kpi_scores:
                company = kpi['company']
                if company not in combined_rankings:
                    combined_rankings[company] = {'opinion_score': 0, 'response_count': 0, 'quality_score': 0, 'kpi_score': 0, 'kpi_count': 0}
                combined_rankings[company]['kpi_score'] = float(kpi['avg_kpi_value']) if kpi['avg_kpi_value'] else 0
                combined_rankings[company]['kpi_count'] = kpi['kpi_count']
            for company, scores in combined_rankings.items():
                opinion_weight = 0.5
                kpi_weight = 0.5
                normalized_opinion = scores['opinion_score'] / 5.0
                normalized_kpi = min(scores['kpi_score'] / 100.0, 1.0)
                combined_rankings[company]['final_score'] = opinion_weight * normalized_opinion + kpi_weight * normalized_kpi
            sorted_rankings = dict(sorted(combined_rankings.items(), key=lambda x: x[1]['final_score'], reverse=True))
            logger.info(f'Generated combined rankings for {len(sorted_rankings)} companies')
            return sorted_rankings
        except Exception as e:
            logger.error(f'Error integrating survey data with ESG rankings: {e}')
            return {}
    def start_survey_server(self, port: int=5000, debug: bool=False):
        """Start the survey server"""
        logger.info(f'Starting survey server on port {port}')
        self.app.run(host='0.0.0.0', port=port, debug=debug)
    def deploy_surveys_for_companies(self, companies: List[str]) -> List[str]:
        """Deploy surveys for multiple companies"""
        survey_ids = []
        for company in companies:
            survey_id = self.create_survey(company)
            if survey_id:
                survey_ids.append(survey_id)
                targets = self.find_survey_targets(company)
                logger.info(f'Created survey {survey_id} for {company} with {len(targets)} targets')
        return survey_ids
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
