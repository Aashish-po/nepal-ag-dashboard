# Nepal Agricultural Intelligence Dashboard

Real-time agricultural analytics dashboard analyzing yield, climate, export crop performance, and commercialization trends across Nepal's 77 districts.

**Report Issues:** [GitHub Issues](https://github.com/Aashish-po/nepal-ag-dashboard/issues)

---

## What It Does

The Nepal Agricultural Intelligence Dashboard provides data-driven insights into Nepal's agricultural sector by combining crop yield data (FAOSTAT), climate data (NASA POWER, CHIRPS), export crop analysis, and commercialization metrics into a single interactive interface.

**Target users:** Data analysts, agricultural researchers, and development organizations (ADB, World Bank, UNDP, FAO) who need to correlate crop productivity with climate factors and identify regional commercialization gaps.

### Screens

| # | Screen | What You Can Do |
|---|--------|-----------------|
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
|-------|-----------|
| Frontend | React 18 + TypeScript, Vite, Tailwind CSS, shadcn/ui, Recharts, react-leaflet |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Statsmodels |
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
- Python 3.11+
- Node.js 18+ (npm 9+)

### 1. Clone and set up the backend

```bash
git clone https://github.com/Aashish-po/nepal-ag-dashboard.git
cd nepal-ag-dashboard/backend

python3.11 -m venv venv
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
npm install

cp .env.example .env.local
# VITE_API_BASE_URL should point to your backend: http://localhost:8000

npm run dev
```

Frontend: [http://localhost:5173](http://localhost:5173)

---

## API

The backend exposes a REST API at `/api/v1/`. Full endpoint documentation is available via Swagger UI at `http://localhost:8000/docs` when running locally, or at the deployed instance.

All endpoints are public (read-only) in v1.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
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
|--------|------|------------------|
| FAOSTAT | Crop production, yields, exports | Weekly via ETL |
| NASA POWER | Temperature, solar radiation | Weekly via ETL |
| CHIRPS | Satellite rainfall estimates | Weekly via ETL |
| Districts Data | 77 Nepal districts with coordinates | Static |
| Crops Data | 35 crop types with categories | Static |

All seed data is committed in `backend/data/`. A weekly ETL pipeline (APScheduler) refreshes data from external APIs and falls back to cached data if any API is unavailable.

---

## Project Structure

```
nepal-ag-dashboard/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variable template
│   ├── Dockerfile
│   ├── render.yaml          # Render deployment config
│   ├── api/
│   │   ├── db.py            # Database session & engine
│   │   ├── routes/          # API endpoint handlers
│   │   └── models/          # Pydantic schemas + SQLAlchemy ORM
│   ├── services/            # ETL, forecasting, correlations, caching, scheduler
│   ├── data/                # Seed CSVs, GeoJSON
│   ├── migrations/          # Database migration scripts
│   ├── scripts/
│   │   └── seed_db.py       # Database seeding script
│   └── tests/
│       ├── unit/            # Unit tests
│       ├── integration/     # Integration tests
│       └── fixtures/        # Test data fixtures
├── frontend/
│   ├── src/
│   │   ├── pages/           # 10 screen components
│   │   ├── components/      # Shared UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities & API client
│   │   └── __tests__/       # Test files
│   ├── vercel.json          # Vercel deployment config
│   ├── vite.config.ts
│   └── package.json
├── .github/
│   └── workflows/
│       ├── ci.yml           # Lint, test, type-check
│       └── e2e.yml          # End-to-end tests
├── .pre-commit-config.yaml  # Pre-commit hooks (black, isort, flake8)
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

# Frontend unit tests
cd ../frontend
npm run test

# Frontend type check
npm run type-check

# E2E tests (requires app running locally)
npx playwright test
```

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes following the existing code style
4. Run the test suite: `pytest backend/tests/` and `npm run test`
5. Ensure pre-commit hooks pass: `pre-commit run --all-files`
6. Commit using [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: describe your change"`
7. Push to your branch: `git push origin feat/my-feature`
8. Open a pull request

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
# nepal-ag-dashboard
