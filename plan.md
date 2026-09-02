# Nepal Agricultural Intelligence Dashboard - Project Completion Plan

## Context

Full-stack agricultural analytics dashboard for Nepal's 77 districts. Backend (Python/FastAPI) and frontend (React/TS/Vite) substantially implemented. Ready for production completion phase.

## Key Decisions

- **Stack**: Python 3.11 + FastAPI + SQLAlchemy (backend), React 18 + TypeScript + Vite (frontend)
- **Database**: PostgreSQL 15 (Supabase)
- **Caching**: Redis (Upstash free tier)
- **Forecasting**: Statsmodels (ARIMA, Exponential Smoothing)
- **Hosting**: Render (backend) + Vercel (frontend)
- **Orchestration**: APScheduler (weekly ETL, Tuesday 00:00 UTC)
- **Monitoring**: Sentry + PostHog
- **Scope (v1)**: District-level yield/climate analysis, export crops, commercialization trends, basic forecasting (12-36mo)
- **Out of Scope**: Real-time IoT, soil quality, farm recommendations, multi-language, mobile app, payments

## Ordered Task List

### Phase 1: Foundation & Database Setup (Week 1, ~35 hrs)

1. **Initialize backend repo** with FastAPI structure, dependencies, pre-commit hooks
2. **Initialize frontend repo** with Vite + React 18 + TypeScript + Tailwind + shadcn/ui
3. **Provision Supabase database** and run migrations (schema from Part 3)
4. **Create all tables**: districts, crops, yields, climate, export_crops, commercialization_index, forecasts
5. **Create indexes** on yields(district_id, year), yields(crop_id, year), climate(district_id, observation_date), etc.
6. **Create materialized view** vw_district_yield_summary
7. **Seed data**: Load 77 districts, 35 crops, FAOSTAT yields (23k rows), CHIRPS climate (9.2k rows), export crop metadata
8. **Configure Render** (backend) and **Vercel** (frontend) with environment variables
9. **Set up Sentry** (error tracking) and **PostHog** (analytics)
10. **Configure CI/CD** GitHub Actions (lint, test, typecheck, build)
11. **Add health endpoint** (/health) with DB connectivity check
12. **Add global exception handler**, CORS middleware, custom exception classes
13. **Verify local dev environment** works: `uvicorn main:app --reload` and `npm run dev`

### Phase 2: Backend API & ETL Pipeline (Week 2, ~48 hrs)

 1. **Build yields API endpoints**: GET /districts, /crops, /yields/{district_id}/{crop_id}, /yields/{district_id}
 2. **Build climate API endpoint**: GET /climate/{district_id} with monthly data
 3. **Build correlation API**: GET /correlation/{district_id} with Pearson correlations
 4. **Build export crops & commercialization endpoints**: /export-crops, /commercialization, /heatmap
 5. **Build forecast placeholder endpoint**: GET /forecasts/{district_id}/{crop_id}
 6. **Build export endpoints**: CSV (/export/yields) and Excel (/export/forecasts)
 7. **Implement weekly ETL scheduler** (APScheduler): fetch FAOSTAT, NASA POWER, CHIRPS, upsert, compute forecasts, refresh MV, invalidate cache
 8. **Add Redis caching layer**: district summaries (1w TTL), forecasts (1m TTL), heatmaps (1m TTL)
 9. **Add input validation** with Pydantic models, query parameter sanitization
10. **Write integration tests** for all API endpoints (≥80% coverage)

### Phase 3: Frontend Screens (Weeks 3-4, ~55 hrs)

 1. **Build layout shell**: Header, Sidebar (collapsible), Layout with React Router
 2. **Home screen**: Hero, featured insights cards, search bar, CTAs
 3. **Yields Analysis screen**: District multi-select, crop checkboxes, year slider, line chart + stats table + CSV export
 4. **Climate Intelligence screen**: District selector, date range, 3 charts (rainfall bar, temp dual-axis, solar area)
 5. **Correlation Analysis screen**: Heatmap + 3 scatter plots + summary stats
 6. **Export Crops screen**: Crop selector (cardamom/ginger/tea), production trend, district table, revenue summary
 7. **Commercialization Dashboard**: Heatmap (all districts), detail modal, provincial comparison bar chart
 8. **Forecasts screen (part 1)**: District+crop+horizon selectors, forecast chart with CI bands, model diagnostics
 9. **District Map screen**: Leaflet + GeoJSON choropleth, metric selector, click → side panel
10. **Compare Districts screen**: Multi-select (max 5), trend comparison chart + stats table
11. **About screen**: Data sources, definitions, methodologies, contact, citation
12. **Apply design tokens**: Colors, typography, spacing, component styles, verify WCAG 2.1 AA contrast

### Phase 4: Forecasting & Polish (Week 5, ~40 hrs)

 1. **Implement ARIMA & Exponential Smoothing** in services/forecasting.py with model selection
 2. **Train forecasts** for all district×crop combos (nightly ETL), store in forecasts table
 3. **Validate RMSE** on historical data (target <15% of yield variance)
 4. **Integrate real forecasts** into Forecasts frontend: CI bands, model diagnostics, Excel export
 5. **Enhance Map screen**: Pre-load GeoJSON, layer toggles, optimized choropleth
 6. **Add tooltips & accessibility**: Chart hover tooltips, ARIA labels, keyboard nav, screen reader testing
 7. **Performance optimization**: Code splitting, React.memo, virtualized tables, Lighthouse >90
 8. **Add animations**: Slide-in sidebar, fade-in charts, smooth filter transitions, toast notifications
 9. **E2E tests** (Playwright): Critical flows (Home→Yields→Export, Forecasts→Excel)

### Phase 5: Launch & Operations (Week 6, ~30 hrs)

 1. **Final QA**: Manual test all 10 screens (desktop + tablet), verify exports, test error states
 2. **Fix bugs** from QA
 3. **Configure production Supabase** DB, run migrations, load seed data, verify backups
 4. **Deploy backend to Render** production, verify health endpoint, monitor cold starts
 5. **Deploy frontend to Vercel** production, verify API base URL, test all screens
 6. **Configure production ETL** (Render cron/background job), test weekly run, set up alerts
 7. **Set up Sentry alerting** (email on critical errors), PostHog event tracking
 8. **Documentation**: Comprehensive README, GitHub Pages landing, API docs (Swagger), case study blog post
 9. **Launch checklist**: All screens ✓, API ✓, DB seeded ✓, Backend ✓, Frontend ✓, ETL ✓, Analytics ✓, Errors ✓, Docs ✓, Case study ✓, Repo public ✓

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
| ------ | ------------- | -------- | ------------ |
| FAOSTAT/NASA API unavailable | Medium | High | Cache locally on first load; fallback to published CSVs; serve stale data with warning |
| MoALD data not machine-readable | Medium | High | Manual scraping/PDF extraction as fallback; contact MoALD for direct access |
| Forecast accuracy low (<5 years data) | Medium | Medium | Start with exponential smoothing; upgrade to ARIMA; flag low-confidence forecasts |
| Render cold starts (free tier) | High | Low | Acceptable for v1; health-check cron every 15min; upgrade to paid in Phase 2 |
| Supabase free tier limits (5GB) | Low | High | Monitor DB size; expected ~12MB v1; upgrade before limit |
| Scope creep | High | High | Strict non-goals list; track requests for Phase 2 backlog |
| Redis cache miss storms | Low | High | Lazy loading; circuit breaker; fallback to DB |
| ETL failure | Medium | Medium | Retry 3x with 30s timeout; email alert on failure; serve cached data for 7 days |

## Success Metrics (Validation Steps)

- **Performance**: API p95 <500ms (cached), page load p95 <3s, DB query p95 <200ms
- **Quality**: Backend test coverage ≥80%, frontend ≥60%, E2E critical paths 100% pass
- **Quality**: Zero critical security vulnerabilities, WCAG 2.1 AA compliance
- **Operational**: Uptime ≥99%, MTTD <5min, MTTR <30min, deployment success 100%
- **Business**: ≥3 development orgs pilot within 6 months, forecast RMSE <15% yield variance

## Open Questions

1. Stakeholder availability for validation and feedback sessions
2. Need for custom production domains (e.g., api.nepalagri.dev)
3. Data usage restrictions or attribution requirements for source data
4. Post-launch Phase 2 feature prioritization
5. Planned support and maintenance approach post-launch

---

## Phase Dependencies & Critical Path

```
Phase 1 (Foundation)
    ↓
Phase 2 (Backend API + ETL)
    ↓
Phase 3 (Frontend Screens) ← depends on Phase 2 endpoints
    ↓
Phase 4 (Forecasting + Polish) ← depends on Phase 3 screens + Phase 2 forecast endpoint
    ↓
Phase 5 (Launch) ← depends on Phase 4 completion
```

**Total estimated effort:** ~208 hours ≈ 5.2 weeks at 40 hrs/week

---

## Quick Reference: Key Files & Commands

| Area | Key Files |
| ------ | ----------- |
| Backend entry | `backend/main.py` |
| API routes | `backend/api/routes/*.py` |
| Services | `backend/services/*.py` |
| DB models | `backend/api/models/db_models.py` |
| Pydantic schemas | `backend/api/models/schemas.py` |
| ETL | `backend/services/etl.py`, `backend/services/scheduler.py` |
| Forecasting | `backend/services/forecasting.py` |
| Frontend pages | `frontend/src/pages/*.tsx` |
| Components | `frontend/src/components/*.tsx` |
| Hooks | `frontend/src/hooks/*.ts` |
| Styles | `frontend/src/styles/tokens.css`, `globals.css` |
| Tests (backend) | `backend/tests/` |
| Tests (frontend) | `frontend/src/__tests__/`, `frontend/e2e/` |
| CI/CD | `.github/workflows/ci.yml`, `render.yaml`, `vercel.json` |
| DB migrations | `backend/migrations/001_initial_schema.sql` |
| Seed data | `backend/data/*.csv`, `backend/scripts/seed_db.py` |

**Key commands:**

```bash
# Backend
cd backend && uvicorn main:app --reload
pytest backend/tests/ -v --cov=backend
python scripts/seed_db.py --load-all

# Frontend
cd frontend && npm run dev
npm run test
npm run build
npm run type-check

# E2E
cd frontend && npx playwright test
```

---

**Last updated:** September 2026  
**Version:** 2.0 (aligned with MASTER_PLAN.md)
