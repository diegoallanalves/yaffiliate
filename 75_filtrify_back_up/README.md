# Filtrify AI Affiliate Platform — Starter

A modular Python/Streamlit project designed to grow into one platform:

- Month 1: profitability calculator, dashboard, landing-page generator
- Month 2: product finder, compliant data import/scrapers, keyword engine
- Month 3: AI copywriter, SEO tools, email generator
- Month 4: recommendations, forecasting, analytics
- Month 5: agents, automation, integrations
- Month 6: authentication, payments, deployment, beta launch

## Important

This starter does **not** log in to, scrape, clone, or automate Filtrify. Begin with
manual CSV imports and approved APIs. Only add browser automation when the relevant
platform explicitly permits it.

## Installation on Windows

Open PowerShell:

```powershell
cd "C:\Users\diego\OneDrive\Área de Trabalho\python"
Expand-Archive -Path .\75_filtrify_starter.zip -DestinationPath .
cd .\75_filtrify_starter

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Alternatively, copy the contents into your existing `75_filtrify` folder.

## First run

1. Open **Calculator** and test a campaign.
2. Save the result.
3. Open **Dashboard** to see saved scenarios.
4. Open **Landing Page Generator** and export a simple HTML presell.
5. Keep all claims truthful and comply with affiliate-network and ad-platform rules.

## Environment variables

Add an API key to `.env` only when you are ready to enable AI generation:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

The application works without an AI key by using a deterministic template.

## Project structure

```text
75_filtrify_starter/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── database.py
│   ├── features/
│   │   ├── calculator.py
│   │   ├── dashboard.py
│   │   └── landing_page.py
│   └── services/
│       └── ai_service.py
├── outputs/landing_pages/
└── tests/test_calculator.py
```

## Core formulas

- Clicks = budget / CPC
- Sales = clicks × conversion rate
- Revenue = sales × commission
- Profit = revenue − budget
- ROAS = revenue / budget
- ROI = profit / budget
- Break-even conversion rate = CPC / commission

## Next development sprint

- Add CSV import for product research.
- Create a product table with commission, price, niche, language, CPC and volume.
- Add a transparent scoring model.
- Add UTM builder and campaign journal.
- Connect approved APIs rather than relying on fragile scraping.
