"""
Configuration for the Healthcare Intelligence Digest Newsletter App.
Fill in your API keys below or set them as environment variables.
"""

import os
from pathlib import Path

# Load .env file if it exists
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# ── Groq API (free, fast) ────────────────────────────────────
# Get your free key at: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── HubSpot API ─────────────────────────────────────────────
# Create a Private App in HubSpot with "Marketing Email" scope
# Settings > Integrations > Private Apps > Create
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")

# HubSpot Blog ID — we'll auto-detect this on first run
_hubspot_blog_id = os.getenv("HUBSPOT_BLOG_ID", "").strip()
HUBSPOT_BLOG_ID = int(_hubspot_blog_id) if _hubspot_blog_id.isdigit() else None

# ── Newsletter Settings ─────────────────────────────────────
# Max articles per sub-segment to include in the newsletter
MAX_ARTICLES_PER_SEGMENT = 5

# Max total articles in the newsletter
MAX_TOTAL_ARTICLES = 30

# Relevance score threshold (0-10). Articles below this are excluded.
RELEVANCE_THRESHOLD = 6

# KOR relevance keywords — based on Korcomptenz's actual services & capabilities
# tailored for the Healthcare industry
KOR_KEYWORDS = [
    # Core Services (KOR offerings relevant to healthcare)
    "ERP", "ERP implementation", "ERP migration", "ERP modernization",
    "Microsoft Dynamics", "Dynamics 365", "D365", "Business Central",
    "SAP", "S/4HANA", "SAP migration", "Oracle ERP", "Oracle Health",
    "Salesforce", "Salesforce Health Cloud", "CRM", "CRM implementation",
    # Cloud & Infrastructure
    "Azure", "AWS", "cloud migration", "cloud transformation",
    "hybrid cloud", "cloud managed services", "DevOps",
    "cloud-based healthcare", "cloud EHR",
    # AI & Data Analytics in Healthcare
    "artificial intelligence", "AI in healthcare", "machine learning",
    "Power BI", "data analytics", "business intelligence", "data warehouse",
    "Microsoft Fabric", "predictive analytics", "generative AI", "Copilot",
    "agentic AI", "clinical AI", "AI diagnostics", "AI drug discovery",
    "healthcare analytics", "population health analytics",
    "real-world data", "real-world evidence",
    # Digital Health & Health IT
    "digital transformation", "digital health", "health IT",
    "EHR", "electronic health record", "EMR", "electronic medical record",
    "Epic", "Cerner", "Oracle Health", "MEDITECH",
    "interoperability", "FHIR", "HL7", "health information exchange", "HIE",
    "telehealth", "telemedicine", "remote patient monitoring", "RPM",
    "patient portal", "patient engagement", "patient experience",
    "clinical decision support", "CDSS",
    "health data", "healthcare data", "clinical data",
    # Automation & Process Improvement
    "robotic process automation", "RPA", "process automation",
    "workflow automation", "revenue cycle automation",
    "prior authorization automation", "claims automation",
    # Cybersecurity & Compliance
    "cybersecurity", "healthcare cybersecurity", "HIPAA",
    "data security", "data privacy", "data breach",
    "compliance", "regulatory compliance", "zero trust",
    "ransomware", "phishing",
    # Operations & Business
    "revenue cycle management", "RCM", "claims management",
    "supply chain", "healthcare supply chain",
    "operational excellence", "operational efficiency",
    "cost reduction", "margin improvement",
    "value-based care", "value-based payment",
    "accountable care", "ACO", "population health",
    "care coordination", "care management",
    "healthcare mergers", "healthcare acquisitions",
    # Payer / Provider / Life Sciences
    "payer", "health plan", "health insurance",
    "provider", "hospital", "health system",
    "pharmacy", "pharmacy benefit", "PBM",
    "life sciences", "pharmaceutical", "pharma",
    "medical device", "biotech", "clinical trial",
    # Regulatory & Policy
    "CMS", "Medicare", "Medicaid", "ACA",
    "healthcare policy", "healthcare regulation",
    "price transparency", "No Surprises Act",
    "healthcare reform", "healthcare legislation",
    # Workforce & Leadership
    "healthcare workforce", "staffing shortage", "nurse staffing",
    "physician burnout", "healthcare leadership",
    "chief digital officer", "CIO", "CMIO", "CTO",
]

# ── KOR Company Context (used in AI prompts) ────────────────
KOR_CONTEXT = """
Korcomptenz (KOR) is a total technology transformation provider specializing in
digital transformation for healthcare and other industries. Key capabilities:

CORE SERVICES: ERP (Microsoft Dynamics 365, SAP S/4HANA, Oracle Fusion),
CRM (Salesforce, Dynamics 365 CE), Cloud Services (Azure, AWS migration & managed),
Data Analytics & AI (Power BI, Microsoft Fabric, predictive analytics, Generative AI),
Application Modernization (legacy-to-cloud, microservices, cloud-native),
Cybersecurity & Compliance (ISO 27001 certified, HIPAA-aligned solutions).

PROPRIETARY IP: KOR SmartForge (100+ analytics dashboards),
KOR BankIQ (banking insights), KOR ESGenius (ESG reporting).
Global AI Innovation Center for Agentic AI initiatives.

TARGET INDUSTRIES IN HEALTHCARE: Hospitals & Health Systems, Health Plans/Payers,
Life Sciences & Pharma, Medical Devices, Behavioral Health, Post-Acute Care,
Healthcare IT Vendors, Ambulatory/Outpatient Networks.

HEALTHCARE RELEVANCE: KOR helps healthcare organizations modernize legacy systems,
migrate to cloud-based platforms, implement ERP/CRM, build data analytics capabilities,
and leverage AI — enabling better patient outcomes, operational efficiency,
regulatory compliance (HIPAA, CMS mandates), and value-based care readiness.

PARTNERSHIPS: Microsoft Gold Partner, Salesforce Partner, AWS Partner.
Featured in ISG Provider Lens report for AI & Cloud Services.

POSITIONING: Mid-market focus with enterprise-grade expertise.
Customer-centric approach (#FocusOnYou). Global delivery (US, India, UAE, Canada).
"""


# ── Ollama Settings (local LLM) ──────────────────────────────
# Set USE_OLLAMA=true to use local Ollama instead of Groq cloud
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
# Recommended: qwen2.5:7b or llama3.1:8b for 16GB RAM systems
# Pull with: ollama pull qwen2.5:7b
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

# ── Flask Settings ──────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "healthcare-newsletter-local-dev")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", "5123"))
