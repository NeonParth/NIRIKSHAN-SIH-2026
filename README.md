# NIRIKSHAN — MPLADS Risk Intelligence & Monitoring System

> **AI-assisted project monitoring, spatial analysis, anomaly detection, and evidence-based verification for MPLADS implementation.**

NIRIKSHAN is a monitoring and risk-intelligence prototype designed to help authorities prioritize MPLADS projects that require verification. Instead of treating every project equally, the system combines project data, spatial relationships, cost signals, tender/competition indicators, image-evidence similarity, and explainable rule-based risk scoring to surface projects for human review.

> **Demo note:** The current prototype uses synthetic demonstration data. Risk signals are indicators for verification and **do not by themselves establish fraud or wrongdoing**.

---

## 🎯 Problem

Monitoring large numbers of development projects manually can make it difficult to identify which projects deserve immediate attention.

NIRIKSHAN addresses this by providing a centralized workflow to:

- monitor project-level risk,
- prioritize anomalies for verification,
- visualize projects geographically,
- explain why a project received a risk score,
- inspect supporting evidence,
- record human verification outcomes, and
- generate investigation reports.

---

## 💡 Solution

NIRIKSHAN follows an **explainable, human-in-the-loop** approach:

```text
Project & Evidence Data
          │
          ├── Spatial Analysis
          ├── Cost Deviation
          ├── Tender / Competition Signals
          ├── Image Similarity Signals
          └── Other Rule-Based Indicators
                    │
                    ▼
          Explainable Risk Engine
                    │
                    ▼
             Risk Score / Level
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 Risk Analysis Queue      Risk Map
        │                       │
        └───────────┬───────────┘
                    ▼
        Authority Investigation
                    │
                    ▼
       Human Verification / Audit
                    │
                    ▼
          Investigation Report
```

---

## ✨ Key Features

### 📊 Risk Intelligence Dashboard
A centralized overview of monitored projects with:

- total projects,
- total project value,
- high/critical-risk projects,
- projects under review,
- risk-level distribution,
- project risk map preview, and
- recent anomaly assessments.

### ⚠️ Explainable Risk Analysis
Projects are prioritized using contributing signals rather than an unexplained black-box score.

Example signals demonstrated in the prototype:

- **Similar project nearby**
- **Image similarity**
- **Cost deviation**
- **Low tender competition**

Each signal shows its observed value, explanation, and contribution to the overall score.

### 🗺️ Geospatial Risk Mapping
The system provides a map-based view of projects with risk filters for:

- Low
- Medium
- High
- Critical

The prototype uses **Leaflet with OpenStreetMap** map data.

### 🔎 Authority Investigation Workspace
Authorized reviewers can:

- open prioritized projects,
- inspect risk signals,
- view verification status,
- inspect evidence metadata,
- record human verification outcomes, and
- export an investigation report.

### 🧾 Evidence & Provenance
The interface distinguishes synthetic demonstration data and verification states to maintain an auditable workflow.

### 🧠 Human-in-the-Loop Verification
NIRIKSHAN does not automatically declare fraud. It identifies **potential risk/anomaly signals** and routes them to an authority for verification.

---

# 🖥️ Prototype Screenshots

## Authority Login

![NIRIKSHAN Authority Login](docs/screenshots/03-login.png)

The prototype provides a dedicated authority login screen for accessing the monitoring and investigation workflow.

## Risk Intelligence Dashboard

![NIRIKSHAN Dashboard](docs/screenshots/01-dashboard.png)

The dashboard provides an at-a-glance view of project volume, project value, risk distribution, geographic risk, and recent anomaly assessments.

## Risk Priority Analysis

![Risk Priority Analysis](docs/screenshots/02-risk-analysis.png)

The risk analysis queue prioritizes projects and explains the contributing signals behind each risk score.

## Authority Investigation Workspace

![Investigation Workspace](docs/screenshots/04-investigation-workspace.png)

The investigation workspace allows reviewers to inspect evidence, review risk signals, record verification outcomes, and export investigation reports.

---

# 🧩 Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| UI / Visualization | React components, charts, Leaflet maps |
| Backend | Python, FastAPI |
| Database | PostgreSQL, PostGIS |
| ORM / Data Layer | SQLAlchemy |
| Migrations | Alembic |
| Risk Engine | Explainable rule-based risk scoring |
| Geospatial | PostGIS, GIS service, Leaflet, OpenStreetMap |
| Evidence / Image Processing | Python image-processing services and similarity metadata |
| Testing | Pytest, frontend UI tests |
| Containers | Docker, Docker Compose |
| Automation | GitHub Actions |
| Configuration | YAML / environment-based configuration |

---

# 📊 Analytics & Visualizations

The prototype includes multiple forms of analytical visualization.

### 1. Risk Level Distribution

A donut chart summarizes the distribution of assessed projects across:

- Low
- Medium
- High
- Critical

### 2. Risk Contribution Analysis

Individual risk signals are displayed with their contribution to the total risk score, making the assessment explainable.

Example prototype scoring:

```text
Similar project nearby   +25
Image similarity         +25
Cost deviation           +20
Low competition          +10
                         ───
                          80+
```

The exact score and signals depend on the project data and configured risk rules.

### 3. Risk Priority Queue

Projects are ranked by risk level and verification status so reviewers can focus on the highest-priority cases first.

### 4. Geographic Risk Visualization

Project locations are plotted on an interactive map and can be filtered by risk level.

### 5. Signal-Based Investigation View

The investigation workspace presents each contributing signal with:

- observed value,
- explanation,
- contribution,
- verification state.

---

# 🤖 AI / ML & Intelligence Layer

NIRIKSHAN is designed as a modular intelligence platform.

The current Phase 1 prototype emphasizes **explainable rule-based risk assessment** so that every flagged project can be traced back to understandable signals.

The repository also contains dedicated modules for future/extended intelligence capabilities:

```text
ml/
├── anomaly_detection/
├── computer_vision/
└── nlp/
```

These modules provide an extensible foundation for incorporating:

- anomaly detection,
- computer vision,
- document/text analysis, and
- additional ML-based project intelligence.

The prototype intentionally keeps the reviewer in the loop rather than presenting an automated risk signal as proof of misconduct.

---

# 🗺️ GIS & Spatial Intelligence

Spatial relationships can reveal patterns that are difficult to identify from tabular project data alone.

NIRIKSHAN's GIS layer supports:

- project coordinates,
- proximity analysis,
- nearby-project signals,
- map-based filtering, and
- spatial risk visualization.

The backend includes a dedicated GIS service, while the frontend provides interactive map visualization.

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│              NIRIKSHAN FRONTEND             │
│                                             │
│ React + TypeScript + Vite + Tailwind CSS    │
│ Dashboard │ Risk Analysis │ Map │           │
│ Investigation │ Projects                    │
└──────────────────────┬──────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────┐
│               FASTAPI BACKEND                │
│                                             │
│ Routers │ Services │ Risk Engine │ Auth     │
│ GIS │ Image Processing │ Cost Analysis      │
│ Tender Analysis │ Nexus / Relationship      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│          POSTGRESQL + POSTGIS               │
│                                             │
│ Project Data │ Risk Data │ Evidence         │
│ Spatial Data │ Verification / Audit Data    │
└─────────────────────────────────────────────┘

Additional infrastructure:
Docker │ Docker Compose │ Alembic │ Pytest │ CI
```

---

# 📁 Project Structure

```text
NIRIKSHAN-SIH-2026/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── services/
│   │   └── utils/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
│
├── config/
│   └── risk_weights.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
│
├── database/
│   ├── init/
│   └── seeds/
│
├── docs/
│   ├── API.md
│   ├── DATA_MODEL.md
│   ├── DEVELOPMENT.md
│   ├── PROJECT_ARCHITECTURE.md
│   └── RISK_ENGINE.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
│
├── ml/
│   ├── anomaly_detection/
│   ├── computer_vision/
│   └── nlp/
│
├── scripts/
├── tests/
├── docker-compose.yml
├── Makefile
├── .dockerignore
├── .gitignore
└── README.md
```

---

# 🔐 Security & Data Handling

The repository is configured to keep sensitive/local configuration out of source control.

The `.gitignore` excludes items such as:

```text
.env
.env.local
.venv/
venv/
__pycache__/
node_modules/
postgres_data/
uploads/
```

A `.env.example` file is included for documenting required environment variables without exposing local secrets.

> Never commit real API keys, database passwords, tokens, or other credentials.

---

# 🐳 Running the Prototype

The project is containerized using Docker Compose.

### Prerequisites

- Git
- Docker Desktop
- Docker Compose

### Clone

```bash
git clone https://github.com/NeonParth/NIRIKSHAN-SIH-2026.git
cd NIRIKSHAN-SIH-2026
```

### Environment

Create your local environment file from the example:

```bash
copy .env.example .env
```

Then configure the required local values in `.env`.

### Start services

```bash
docker compose up -d
```

The frontend can then be accessed through the configured local frontend port.

---

# 🧪 Testing

The project includes automated tests for backend functionality and frontend UI behavior.

Backend tests:

```bash
cd backend
pytest
```

Frontend tests are configured in the frontend project.

CI configuration is available under:

```text
.github/workflows/ci.yml
```

---

# 📚 Documentation

Additional technical documentation is available in:

```text
docs/
├── API.md
├── DATA_MODEL.md
├── DEVELOPMENT.md
├── PROJECT_ARCHITECTURE.md
└── RISK_ENGINE.md
```

---

# 🔄 Development Workflow

The project is designed for collaborative development using Git.

Recommended workflow:

```text
Issue / Task
     ↓
Feature Branch
     ↓
Development
     ↓
Testing
     ↓
Pull Request
     ↓
Review
     ↓
Merge into main
```

Collaborators and branch protections can be configured as the team moves into the next development phase.

---

# 🚀 Future Scope

Potential extensions include:

- stronger ML-based anomaly detection,
- advanced computer-vision evidence comparison,
- NLP-based document analysis,
- automated cross-project relationship discovery,
- richer GIS/spatial analytics,
- external data-source integration,
- advanced audit trails,
- role-based access control,
- model monitoring and evaluation, and
- deployment to a production infrastructure.

---

# ⚠️ Prototype Disclaimer

NIRIKSHAN is an SIH prototype demonstrating a risk-intelligence and verification workflow.

The prototype's risk scores identify **potential anomalies or risk signals requiring verification**. They should not be interpreted as automatic proof of fraud, corruption, or wrongdoing.

The current demonstration uses synthetic data.

---

# 👥 Team

**NIRIKSHAN — SIH 2026**

Team collaboration and individual contribution details can be added here as the project moves into the collaborative development phase.

---

## 📌 Repository

**NIRIKSHAN-SIH-2026**

The repository contains the frontend, backend, database, GIS, risk-engine, ML module structure, tests, documentation, Docker configuration, and CI workflow for the prototype.
