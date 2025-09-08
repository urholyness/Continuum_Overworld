// server.js - Your API monitoring backend
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public')); // Serve static files

// API Configuration
const API_CONFIGS = {
    anthropic: {
        name: "Claude (Anthropic)",
        baseURL: "https://api.anthropic.com/v1",
        usageEndpoint: "/messages", // You'd typically have a usage endpoint
        headers: {
            'x-api-key': process.env.ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        },
        icon: "🤖",
        color: "#ff6b6b"
    },
    openai: {
        name: "OpenAI GPT",
        baseURL: "https://api.openai.com/v1",
        usageEndpoint: "/usage",
        headers: {
            'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
            'content-type': 'application/json'
        },
        icon: "🧠",
        color: "#4ecdc4"
    },
    xai: {
        name: "Grok (xAI)",
        baseURL: "https://api.x.ai/v1",
        usageEndpoint: "/usage",
        headers: {
            'Authorization': `Bearer ${process.env.XAI_API_KEY}`,
            'content-type': 'application/json'
        },
        icon: "⚡",
        color: "#feca57"
    },
    cohere: {
        name: "Cohere",
        baseURL: "https://api.cohere.ai/v1",
        usageEndpoint: "/usage",
        headers: {
            'Authorization': `Bearer ${process.env.COHERE_API_KEY}`,
            'content-type': 'application/json'
        },
        icon: "🎯",
        color: "#ff9ff3"
    },
    huggingface: {
        name: "Hugging Face",
        baseURL: "https://api-inference.huggingface.co",
        usageEndpoint: "/usage",
        headers: {
            'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
            'content-type': 'application/json'
        },
        icon: "🤗",
        color: "#54a0ff"
    }
};

// Store usage data in memory (you might want to use Redis or a DB later)
let usageCache = {};
let lastFetch = {};

// Helper function to generate mock data (for APIs that don't have usage endpoints)
function generateMockData(apiName) {
    const baseUsage = Math.floor(Math.random() * 100000) + 10000;
    const dailyLimit = Math.floor(baseUsage * (1.2 + Math.random() * 0.8));
    
    return {
        tokensUsed: baseUsage,
        tokensLimit: dailyLimit,
        requestsToday: Math.floor(Math.random() * 500) + 50,
        requestsLimit: 1000,
        costToday: (baseUsage * 0.002 * (0.5 + Math.random())).toFixed(2),
        avgResponseTime: (Math.random() * 2000 + 500).toFixed(0),
        errorRate: (Math.random() * 5).toFixed(2),
        status: Math.random() > 0.2 ? 'active' : (Math.random() > 0.5 ? 'warning' : 'error'),
        lastUsed: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        dailyHistory: Array.from({length: 7}, () => Math.floor(Math.random() * baseUsage * 0.3) + baseUsage * 0.7)
    };
}

// Fetch usage data from specific APIs
async function fetchAnthropicUsage() {
    try {
        // Anthropic doesn't have a public usage endpoint, so we'll simulate
        // In practice, you'd track this in your app or use their billing API if available
        return generateMockData('anthropic');
    } catch (error) {
        console.error('Error fetching Anthropic usage:', error);
        throw error;
    }
}

async function fetchOpenAIUsage() {
    try {
        // OpenAI has a usage endpoint, but it requires specific date ranges
        const today = new Date().toISOString().split('T')[0];
        const response = await axios.get(
            `${API_CONFIGS.openai.baseURL}/usage?date=${today}`,
            { headers: API_CONFIGS.openai.headers }
        );
        
        // Transform OpenAI response to our format
        const data = response.data;
        return {
            tokensUsed: data.total_tokens || 0,
            tokensLimit: 1000000, // You'd set this based on your plan
            requestsToday: data.n_requests || 0,
            requestsLimit: 1000,
            costToday: (data.total_tokens * 0.002).toFixed(2),
            avgResponseTime: Math.floor(Math.random() * 1000 + 500),
            errorRate: '0.1',
            status: 'active',
            lastUsed: new Date().toISOString(),
            dailyHistory: Array.from({length: 7}, () => Math.floor(Math.random() * 50000))
        };
    } catch (error) {
        console.error('Error fetching OpenAI usage:', error);
        // Fallback to mock data if API call fails
        return generateMockData('openai');
    }
}

async function fetchXAIUsage() {
    try {
        // Grok/xAI usage endpoint (adjust based on their actual API)
        return generateMockData('xai'); // Replace with actual API call when available
    } catch (error) {
        console.error('Error fetching xAI usage:', error);
        return generateMockData('xai');
    }
}

async function fetchCohereUsage() {
    try {
        // Cohere usage endpoint
        return generateMockData('cohere'); // Replace with actual API call
    } catch (error) {
        console.error('Error fetching Cohere usage:', error);
        return generateMockData('cohere');
    }
}

async function fetchHuggingFaceUsage() {
    try {
        // HuggingFace doesn't have a standard usage API, so we simulate
        return generateMockData('huggingface');
    } catch (error) {
        console.error('Error fetching HuggingFace usage:', error);
        return generateMockData('huggingface');
    }
}

// API Routes
app.get('/api/usage/:provider', async (req, res) => {
    const { provider } = req.params;
    
    // Check if we have cached data (refresh every 5 minutes)
    const now = Date.now();
    if (usageCache[provider] && lastFetch[provider] && 
        (now - lastFetch[provider]) < 5 * 60 * 1000) {
        return res.json(usageCache[provider]);
    }
    
    try {
        let usage;
        
        switch (provider) {
            case 'anthropic':
                usage = await fetchAnthropicUsage();
                break;
            case 'openai':
                usage = await fetchOpenAIUsage();
                break;
            case 'xai':
                usage = await fetchXAIUsage();
                break;
            case 'cohere':
                usage = await fetchCohereUsage();
                break;
            case 'huggingface':
                usage = await fetchHuggingFaceUsage();
                break;
            default:
                return res.status(400).json({ error: 'Unknown provider' });
        }
        
        // Cache the result
        usageCache[provider] = usage;
        lastFetch[provider] = now;
        
        res.json(usage);
    } catch (error) {
        console.error(`Error fetching usage for ${provider}:`, error);
        res.status(500).json({ error: 'Failed to fetch usage data', details: error.message });
    }
});

// Get all usage data
app.get('/api/usage', async (req, res) => {
    try {
        const providers = Object.keys(API_CONFIGS);
        const usagePromises = providers.map(async (provider) => {
            try {
                const response = await axios.get(`http://localhost:${PORT}/api/usage/${provider}`);
                return { provider, data: response.data, success: true };
            } catch (error) {
                return { provider, error: error.message, success: false };
            }
        });
        
        const results = await Promise.all(usagePromises);
        const usageData = {};
        
        results.forEach(result => {
            if (result.success) {
                usageData[result.provider] = result.data;
            } else {
                usageData[result.provider] = { error: result.error };
            }
        });
        
        res.json(usageData);
    } catch (error) {
        console.error('Error fetching all usage data:', error);
        res.status(500).json({ error: 'Failed to fetch usage data' });
    }
});

// Get API configurations (without sensitive data)
app.get('/api/configs', (req, res) => {
    const publicConfigs = {};
    
    Object.keys(API_CONFIGS).forEach(key => {
        publicConfigs[key] = {
            name: API_CONFIGS[key].name,
            icon: API_CONFIGS[key].icon,
            color: API_CONFIGS[key].color
        };
    });
    
    res.json(publicConfigs);
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Serve the dashboard
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server Error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// Start the server
app.listen(PORT, () => {
    console.log(`🚀 API Dashboard Server running on http://localhost:${PORT}`);
    console.log(`📊 Dashboard available at http://localhost:${PORT}`);
    console.log(`🔧 Health check: http://localhost:${PORT}/api/health`);
    
    // Log which API keys are configured
    const configuredAPIs = Object.keys(API_CONFIGS).filter(key => {
        const envKey = `${key.toUpperCase()}_API_KEY`;
        return process.env[envKey];
    });
    
    console.log(`🔑 Configured APIs: ${configuredAPIs.join(', ')}`);
    console.log(`⚠️  Missing API keys: ${Object.keys(API_CONFIGS).filter(key => !configuredAPIs.includes(key)).join(', ')}`);
});

module.exports = app;