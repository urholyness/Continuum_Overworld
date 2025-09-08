# Farm 5.0 Agent System - Orion

## 🌾 Overview
The Farm 5.0 Agent System is a sophisticated AI-powered platform designed to automate and optimize agricultural business operations through intelligent agent employees.

## 🚀 Quick Start
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Set Environment**: Copy `.env.example` to `.env` and configure
3. **Start API**: `uvicorn api.main:app --reload`
4. **Access Dashboard**: http://localhost:8000

## 📁 Project Structure
```
farm5-orion-system/
├── 📁 core/                    # Core framework and base classes
├── 📁 agents/                  # Individual agent implementations
├── 📁 api/                     # FastAPI backend service
├── 📁 dashboard/               # React frontend dashboard
├── 📁 config/                  # Configuration files and templates
├── 📁 docs/                    # Documentation and guides
├── 📁 tests/                   # Test files
├── 📁 scripts/                 # Utility scripts
├── 📁 deployment/              # Deployment configurations
├── 📁 data/                    # Data files and databases
└── 📁 logs/                    # Application logs
```

## 🤖 Available Agents
- **Email Management Agent** - Email classification and auto-response
- **Sales Outreach Agent (Orion)** - Automated lead generation and outreach
- **Market Research Agent** - Competitive analysis and trend monitoring
- **Customer Support Agent** - Ticket routing and automated support
- **Finance Management Agent** - Expense tracking and reporting
- **Data Analytics Agent** - Performance metrics and insights
- **Growth Strategy Agent** - Meta-coordination of all agents

## 🔧 Development
- **Python 3.8+** required
- **Node.js 16+** for dashboard
- **OpenAI API key** for AI functionality
- **Gmail API credentials** for email agents

## 📚 Documentation
- [Deployment Guide](docs/deployment/deployment-guide.md)
- [API Documentation](docs/api/)
- [User Guides](docs/user_guides/)
- [Complete Implementation Guide](Farm5-Agent-System-Guide.md)

## 🎯 Current Status
**Foundation Complete (40%)** - Ready for deployment with Email Management and Sales Outreach agents fully implemented.

## 📞 Support
- **Email**: tech@greenstem.global
- **Documentation**: [Complete Guide](Farm5-Agent-System-Guide.md)
- **Issues**: Use project issue tracker

---
*Built with ❤️ for Farm 5.0 by the Greenstem Technical Team*