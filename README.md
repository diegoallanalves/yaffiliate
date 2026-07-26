# Filtrify AI
## Affiliate Intelligence Platform

An AI-powered Affiliate Marketing Intelligence Platform built with Python, Streamlit, SQL Server, SQLAlchemy and OpenAI.

The objective of this project is to build a professional SaaS application capable of helping affiliate marketers research products, analyze opportunities, generate marketing content and automate digital marketing workflows using Artificial Intelligence.

---

# Vision

Rather than being just another AI copywriting tool, Filtrify AI aims to become a complete Affiliate Intelligence Platform.

The platform will help users:

- Discover profitable affiliate products
- Score product opportunities
- Research keywords
- Track market metrics
- Generate SEO content
- Create Google Ads campaigns
- Generate Email Marketing sequences
- Build Landing Pages
- Forecast profitability
- Automate marketing workflows
- Manage affiliate products in one centralized platform

---

# Current Development Status

## Phase 1 — Foundation (Completed)

### Backend

- SQL Server integration
- SQLAlchemy architecture
- Repository Pattern
- Professional project structure
- ProductRepository CRUD
- Product Metrics repository
- Database normalization
- SQL Views
- Environment configuration (.env)

### Frontend

- Streamlit professional layout
- Modular navigation
- Dashboard
- Product Research
- Keyword Research
- AI Assistant
- Analytics
- Landing Pages
- Email Marketing
- SEO
- Google Ads
- Affiliate Products
- Settings

### Infrastructure

- Python virtual environment
- Git repository
- GitHub version control
- Modular architecture
- Configuration management

---

# Current Architecture

```
                 Streamlit UI
                      │
                      ▼
                 Page Modules
                      │
                      ▼
                Service Layer
                      │
                      ▼
              Repository Pattern
                      │
                      ▼
                 SQLAlchemy ORM
                      │
                      ▼
                  SQL Server
```

---

# Current Project Structure

```
75_filtrify/

app/
│
├── components/
├── models/
├── pages/
│   ├── dashboard.py
│   ├── product_research.py
│   ├── keyword_research.py
│   ├── ai_assistant.py
│   ├── analytics.py
│   ├── landing_pages.py
│   ├── email_marketing.py
│   ├── seo.py
│   ├── google_ads.py
│   ├── affiliate_products.py
│   ├── settings.py
│   └── profit_calculator.py
│
├── repositories/
│   ├── database.py
│   ├── sql_server.py
│   └── product_repository.py
│
├── services/
└── components/

tests/

assets/

outputs/

app.py

requirements.txt

README.md
```

---

# Technology Stack

## Frontend

- Streamlit

## Backend

- Python 3.10+
- SQLAlchemy
- pyodbc

## Database

- Microsoft SQL Server

## AI

- OpenAI API (planned)

## Data Science

- Pandas
- NumPy
- Plotly

## Development

- Git
- GitHub
- PyCharm

---

# Modules

## Dashboard

Executive overview of products, opportunities and business metrics.

---

## Product Research

Affiliate Product CRM

- Product management
- Market metrics
- Opportunity scoring
- Historical metrics
- Affiliate links
- Product notes

---

## Keyword Research

Keyword database linked to products.

---

## AI Assistant

AI-powered affiliate marketing assistant.

---

## Profit Calculator

Campaign profitability simulation.

---

## Analytics

Business Intelligence dashboard.

---

## Landing Pages

Landing page generation.

---

## Email Marketing

AI email sequence generation.

---

## SEO

SEO article generation.

---

## Google Ads

Google Ads campaign generation.

---

## Affiliate Products

Central affiliate product management.

---

## Settings

Application configuration.

---

# Development Roadmap

## Phase 1
Foundation

- Professional architecture
- SQL Server
- Repository Pattern
- Product CRUD

Status:

✅ Completed

---

## Phase 2
Product Intelligence Layer

Current Sprint

- Product CRM
- Product History
- Product Metrics
- Product Dashboard
- Keyword Repository

Status:

🚧 In Progress

---

## Phase 3
Marketing Intelligence

- SEO
- Google Ads
- Email Marketing
- Landing Pages

Status:

⏳ Planned

---

## Phase 4
Artificial Intelligence

- AI Product Analysis
- AI Copywriting
- AI Campaign Generator
- AI SEO
- AI Email Marketing

Status:

⏳ Planned

---

## Phase 5
Automation

- AI Agents
- Workflow Automation
- Integrations
- Scheduling

Status:

⏳ Planned

---

## Phase 6
Commercial SaaS

- Authentication
- User Management
- Stripe Integration
- Subscription Plans
- Deployment
- Beta Launch

Status:

⏳ Planned

---

# Local Installation

```powershell
git clone https://github.com/YOUR_USERNAME/filtrify-ai.git

cd filtrify-ai

python -m venv .venv

.\.venv\Scripts\activate

pip install -r requirements.txt
```

---

Create a `.env` file

```text
OPENAI_API_KEY=your_api_key

OPENAI_MODEL=gpt-4.1-mini

DB_SERVER=YOUR_SERVER

DB_NAME=FiltrifyAI

DB_DRIVER=ODBC Driver 18 for SQL Server

DB_TRUSTED_CONNECTION=yes
```

---

Run

```powershell
streamlit run app.py
```

---

# Project Goals

This project is being developed as:

- A production-quality portfolio project
- A complete AI Engineering learning journey
- A Data Engineering showcase
- A potential commercial SaaS platform

---

# Future Features

- Multi-user authentication
- Stripe subscriptions
- Team workspaces
- AI agents
- RAG knowledge base
- Marketing automation
- Social media automation
- Campaign forecasting
- Revenue prediction
- Machine Learning recommendations
- Cloud deployment

---

# License

Personal educational and portfolio project.