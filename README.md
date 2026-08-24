# Nepal Agricultural Intelligence Dashboard

Version: 0.1.0 (development)

Real-time agricultural analytics dashboard analyzing yield, climate, export crop performance, and commercialization trends across Nepal's 77 districts.

**Report Issues:** [GitHub Issues](https://github.com/Aashish-po/nepal-ag-dashboard/issues)

---

## What It Does

The Nepal Agricultural Intelligence Dashboard provides data-driven insights into Nepal's agricultural sector by combining crop yield data (FAOSTAT), climate data (NASA POWER, CHIRPS), export crop analysis, and commercialization metrics into a single interactive interface.

**Target users:** Data analysts, agricultural researchers, and development organizations (ADB, World Bank, UNDP, FAO) who need to correlate crop productivity with climate factors and identify regional commercialization gaps.

### Screens

| # | Screen | What You Can Do |
| --- | -------- | ----------------- |
| 1 | **Home** | Browse featured insights and navigate to any analysis |
| 2 | **Yield Analysis** | Filter by district/crop/year; view yield timeseries, trends, and CAGR |
| 3 | **Climate Intelligence** | Explore rainfall, temperature, and solar radiation by district and date range |
| 4 | **Correlation Analysis** | Heatmaps and scatter plots showing yield-climate relationships |
| 5 | **Export Crops** | Analyze cardamom, ginger, and tea production, revenue, and export seasons |
| 6 | **Commercialization Dashboard** | View subsistence vs. commercial farming gaps across districts |
| 7 | **Forecasts** | 12–36 month yield predictions using ARIMA and Exponential Smoothing |
| 8 | **District Map** | Interactive choropleth map; click districts to drill into details |
| 9 | **Compare Districts** | Side-by-side yield trends across up to 5 districts |
| 10 | **About** | Data sources, methodologies, and contact information |

---

## Tech Stack

| Layer | Technology |
| ------- | ----------- |
| Frontend | React 18 + TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts, react-leaflet, Vitest (testing) |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Statsmodels, with dev dependencies: ruff, mypy, bandit, pip-audit, httpx (for integration tests) |
| Database | PostgreSQL (Supabase) |
| Data Processing | Pandas, NumPy, SciPy, GeoPandas |
| Caching | Redis (Upstash) |
| Deployment | Render (backend), Vercel (frontend) |
| Monitoring | Sentry (error tracking), PostHog (analytics) |
| CI/CD | GitHub Actions |

---

## Quick Start (Local Development)

### Prerequisites

- Git 2.30+
- Python 3.12+
- Node.js 18+ (pnpm 10+)

### 1. Clone and set up the backend

```bash
git clone https://github.com/Aashish-po/nepal-ag-dashboard.git
cd nepal-ag-dashboard/backend

python3.12 -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
source venv/bin/activate        # macOS/Linux

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env.local
# Edit .env.local to set your DATABASE_URL, CORS_ORIGINS, etc.
```

### 2. Set up a local database

```bash
docker run --name nepal-ag-db \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=nepal_ag_dev \
  -p 5432:5432 -d postgres:15
```

### 3. Seed data and start the backend

```bash
python scripts/seed_db.py --load-all
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### 4. Set up and start the frontend

```bash
cd ../frontend
pnpm install

cp .env.example .env.local
# VITE_API_BASE_URL should point to your backend: http://localhost:8000

pnpm dev
```

- Frontend: [http://localhost:5173](http://localhost:5173)

---

## API

The backend exposes a REST API at `/api/v1/`. Full endpoint documentation is available via Swagger UI at `http://localhost:8000/docs` when running locally, or at the deployed instance.

All endpoints are public (read-only) in v1.

### Key Endpoints

| Method | Endpoint | Description |
| -------- | ---------- | ------------- |
| GET | `/health` | Health check (DB connectivity) |
| GET | `/api/v1/districts` | List all 77 districts (filter by province/region) |
| GET | `/api/v1/crops` | List all crop types (filter by category/export) |
| GET | `/api/v1/yields/{district_id}/{crop_id}` | Yield timeseries with statistics |
| GET | `/api/v1/climate/{district_id}` | Monthly climate data (rainfall, temp, solar) |
| GET | `/api/v1/correlation/{district_id}` | Pearson correlation between yields and climate |
| GET | `/api/v1/export-crops/{district_id}` | Export crop production and revenue |
| GET | `/api/v1/commercialization/{district_id}` | Commercialization index and score |
| GET | `/api/v1/forecasts/{district_id}/{crop_id}` | Yield forecasts with confidence intervals |
| GET | `/api/v1/heatmap/yield-climate-correlation` | Pre-computed correlation matrix |
| GET | `/api/v1/export/yields` | Download yields as CSV |
| GET | `/api/v1/export/forecasts` | Download forecasts as Excel |

### Example

```bash
# Get Kathmandu rice yields (2014–2024)
curl https://nepal-ag-backend.onrender.com/api/v1/yields/1/1?year_start=2014&year_end=2024

# Download climate data as CSV
curl https://nepal-ag-backend.onrender.com/api/v1/export/yields?district_id=1&crop_id=1 -o yields.csv
```

---

## Data Sources

| Source | Data | Update Frequency |
| -------- | ------ | ------------------ |
| FAOSTAT | Crop production, yields, exports | Weekly via ETL |
| NASA POWER | Temperature, solar radiation | Weekly via ETL |
| CHIRPS | Satellite rainfall estimates | Weekly via ETL |
| Districts Data | 77 Nepal districts with coordinates | Static |
| Crops Data | 35 crop types with categories | Static |

All seed data is committed in `backend/data/`. A weekly ETL pipeline (APScheduler) refreshes data from external APIs and falls back to cached data if any API is unavailable.

---

## Project Structure

```text
nepal-ag-dashboard/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── vercel.json
│   ├── .env.example
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Yields.tsx
│   │   │   ├── Climate.tsx
│   │   │   ├── Correlation.tsx
│   │   │   ├── ExportCrops.tsx
│   │   │   ├── Commercialization.tsx
│   │   │   ├── Forecasts.tsx
│   │   │   ├── Map.tsx
│   │   │   ├── Compare.tsx
│   │   │   └── About.tsx
│   │   ├── hooks/
│   │   │   ├── useApi.ts
│   │   │   └── useFilters.ts
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   ├── styles/
│   │   │   ├── tokens.css
│   │   │   └── globals.css
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── __tests__/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── integration/
│   └── public/
│       └── favicon.svg
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt          # Dependencies
│   ├── .env.example              # Env template
│   ├── Dockerfile                # For Render deployment
│   ├── render.yaml               # Render deploy config
│   ├── .pre-commit-config.yaml  # Pre-commit hooks
│   ├── api/
│   │   ├── __init__.py
│   │   ├── db.py               # Database/session setup
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── districts.py
│   │   │   ├── crops.py
│   │   │   ├── yields.py
│   │   │   ├── climate.py
│   │   │   ├── forecasts.py
│   │   │   ├── exports.py
│   │   │   ├── commercialization.py
│   │   │   ├── correlation.py
│   │   │   └── heatmap.py
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── schemas.py      # Pydantic models
│   │       └── db_models.py    # SQLAlchemy ORM
│   ├── services/
│   │   ├── __init__.py
│   │   ├── etl.py
│   │   ├── forecasting.py
│   │   ├── correlations.py
│   │   ├── cache.py
│   │   ├── scheduler.py
│   │   └── climate.py
│   ├── data/
│   │   ├── faostat_2014_2024.csv
│   │   ├── chirps_2014_2024.csv
│   │   ├── districts.csv
│   │   ├── crops.csv
│   │   └── nepal_districts.geojson
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   ├── scripts/
│   │   └── seed_db.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── unit/
│       │   ├── test_services.py
│   │       ├── test_schemas.py
│   │       └── test_utils.py
│       ├── integration/
│   │       │   └── test_api.py
│       └── fixtures/
│           ├── districts.json
│           ├── yields.json
│           └── climate.json
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── e2e.yml
└── README.md
```

---

## Testing

```bash
# Backend unit tests
cd backend
pytest tests/unit/ -v

# Backend integration tests
pytest tests/integration/ -v

# Backend linting, type checking, and security
cd backend
ruff check .
ruff format --check .
mypy .
bandit -r backend -ll
pip-audit

# Frontend unit tests
cd ../frontend
pnpm test

# Frontend type check
pnpm type-check

# Frontend vitest UI (optional)
pnpm test:ui

# E2E tests (requires app running locally)
npx playwright test
```

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes following the existing code style
4. Run the test suite: `pytest backend/tests/` and `pnpm test`
5. Run linting, type checking, and security checks: `ruff check .`, `ruff format --check .`, `mypy .`, `bandit -r backend -ll`, `pip-audit` (backend) and `pnpm lint` (frontend)
6. Ensure pre-commit hooks pass: `pre-commit run --all-files`
7. Commit using [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: describe your change"`
8. Push to your branch: `git push origin feat/my-feature`
9. Open a pull request

**Note:** This is primarily a solo developer project. All pull requests are reviewed with focus on correctness, code quality, and alignment with the project's goals and constraints.

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

## Credits

- **Owner:** Aashish Paudel
- **Data Sources:** [FAOSTAT](https://faostat.org), [NASA POWER](https://power.larc.nasa.gov), [CHIRPS](https://www.chc.ucsb.edu/data/chirps), Nepal MoALD
- **Inspiration:** World Bank Data Portal, FAO GIEWS, Our World in Data

---

*This project is built for public good. All data shown is publicly available agricultural statistics.*
