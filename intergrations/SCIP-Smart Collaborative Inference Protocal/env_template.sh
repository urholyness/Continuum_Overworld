# API Usage Dashboard - Environment Configuration
# Copy this file to .env and add your actual API keys

# Server Configuration
PORT=3000
NODE_ENV=development

# API Keys - Add your actual keys here
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
XAI_API_KEY=your_xai_grok_key_here
COHERE_API_KEY=your_cohere_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Optional: Database connection (for future persistence)
# DATABASE_URL=your_database_url_here

# Optional: Redis for caching (for scaling)
# REDIS_URL=your_redis_url_here

# Dashboard Configuration
REFRESH_INTERVAL=300000  # 5 minutes in milliseconds
CACHE_DURATION=300000    # 5 minutes in milliseconds

# Logging
LOG_LEVEL=info