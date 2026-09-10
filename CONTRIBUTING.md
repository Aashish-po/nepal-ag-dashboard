# Contributing Guide

Thank you for your interest in contributing to the Nepal Agricultural Intelligence Dashboard!

## Quick Links

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

---

## Ways to Contribute

- **Bug reports** — Found an issue? Let us know
- **Feature requests** — Have an idea? Open a discussion
- **Code contributions** — Fix bugs, add features, improve tests
- **Documentation** — Improve docs, add examples, fix typos
- **Data quality** — Report data anomalies, suggest better sources
- **Translations** — Help make the dashboard accessible (Phase 2)

---

## Getting Started

### Prerequisites

- Git 2.30+
- Python 3.11+
- Node.js 18+ (npm 9+)
- Docker (optional, for local PostgreSQL)

### Local Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/nepal-ag-dashboard.git
cd nepal-ag-dashboard

# 2. Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env.local  # Edit with your local DB URL
python scripts/seed_db.py --load-all
uvicorn main:app --reload

# 3. Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:5173` — you're live!

---

## Development Workflow

### Branching Strategy

```
main ──► develop ──► feature/your-feature-name
                    ├──► fix/issue-description
                    └──► docs/what-you-updated
```

- `main` — Production-ready, deployed to Vercel/Render
- `develop` — Integration branch, deployed to staging
- Feature branches — One per issue/PR

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting, no code change
- `refactor` — Code restructuring
- `perf` — Performance improvement
- `test` — Adding tests
- `chore` — Maintenance, deps, build

**Examples:**

```
feat(yields): add CAGR calculation to statistics
fix(climate): handle missing temperature data gracefully
docs(api): update forecast endpoint examples
test(correlation): add insufficient data test case
```

### Pull Request Process

1. **Create branch** from `develop`
2. **Make changes** with tests
3. **Run checks locally:**

   ```bash
   # Backend
   cd backend
   black . && isort . && flake8 .
   pytest --cov=backend
   
   # Frontend
   cd frontend
   npm run type-check
   npm run test
   npm run build
   ```

4. **Push and open PR** against `develop`
5. **Fill PR template** (auto-populated)
6. **Wait for CI** — All checks must pass
7. **Address review feedback**
8. **Squash and merge** (maintainer action)

---

## Code Standards

### Backend (Python)

- **Formatter:** Black (line length 100)
- **Import sorter:** isort
- **Linter:** flake8
- **Type hints:** Required for all public functions
- **Docstrings:** Google style for public APIs
- **Testing:** pytest, ≥80% coverage target

```python
# Example function
def calculate_yield_kg_ha(production_mt: float, area_ha: float) -> float | None:
    """Calculate yield in kg/ha from production and area.
    
    Args:
        production_mt: Total production in metric tons
        area_ha: Harvested area in hectares
        
    Returns:
        Yield in kg/ha, or None if area is zero
    """
    if area_ha <= 0:
        return None
    return (production_mt * 1000) / area_ha
```

### Frontend (TypeScript/React)

- **Formatter:** Prettier (via ESLint)
- **Linter:** ESLint + TypeScript strict mode
- **Components:** Functional, hooks-based
- **State:** Zustand for global, useState for local
- **Testing:** Vitest + React Testing Library
- **Accessibility:** WCAG 2.1 AA minimum

```tsx
// Example component
interface YieldCardProps {
  district: string;
  yield: number;
  trend: 'INCREASING' | 'STABLE' | 'DECREASING';
}

export function YieldCard({ district, yield, trend }: YieldCardProps) {
  return (
    <article className="card" aria-labelledby={district}>
      <h3 id={district}>{district}</h3>
      <p>{yield.toLocaleString()} kg/ha</p>
      <TrendBadge trend={trend} />
    </article>
  );
}
```

### Database

- Migrations via Supabase CLI (`supabase db push`)
- All migrations in `backend/migrations/`
- Never edit production DB directly

---

## Testing

### Running Tests

```bash
# Backend
cd backend
pytest                    # All tests
pytest -k "yields"        # Filter by keyword
pytest --cov=backend      # With coverage

# Frontend
cd frontend
npm run test              # Unit tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report

# E2E (requires running dev servers)
cd frontend
npm run build
npm run preview &
npx playwright test
```

### Writing Tests

- **Unit:** Test pure functions, utilities, schemas
- **Integration:** Test API endpoints with test DB
- **E2E:** Test critical user journeys (filter → chart → export)

---

## Data Contributions

### Reporting Data Issues

Found incorrect yields, missing districts, or climate anomalies?

1. Open issue with label `data-quality`
2. Include:
   - District/crop/year
   - Expected vs actual values
   - Source of correct data (if known)

### Adding New Data Sources

1. Discuss in issue first (avoid duplicate work)
2. Add ETL function in `backend/services/etl.py`
3. Update schema if new fields needed
4. Add validation rules
5. Document in Data Dictionary

---

## Documentation

### Where Docs Live

| Content | Location |
| --------- | ---------- |
| User-facing | `docs/` (GitHub Pages) |
| API reference | `plans/MASTER_PLAN.md#part-8-api-reference-v1` |
| Architecture | `plans/MASTER_PLAN.md#part-2-technical-requirements-document-trd` |
| Data dictionary | `plans/MASTER_PLAN.md#part-9-data-dictionary` |
| Deployment | `plans/MASTER_PLAN.md#part-7-deployment-guide` |

### Style Guide

- Clear, concise, imperative mood
- Code examples for all APIs
- Screenshots for UI changes
- Update relevant docs with every PR

---

## Release Process

### Versioning

[Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- `PATCH` — Bug fixes, no API changes
- `MINOR` — New features, backward compatible
- `MAJOR` — Breaking changes

### Release Checklist

- [ ] All CI checks pass
- [ ] Changelog updated (`CHANGELOG.md`)
- [ ] Version bumped in `package.json` + `backend/__init__.py`
- [ ] Git tag created: `git tag v1.2.3`
- [ ] GitHub Release published
- [ ] Deploy to staging → smoke test → production

---

## Community

- **Discussions:** GitHub Discussions for questions, ideas
- **Issues:** Bug reports, feature requests
- **Email:** <aashish.paudel@example.com> for direct contact

### Recognition

Contributors are recognized in:

- `CONTRIBUTORS.md` (auto-generated from git)
- Release notes
- Annual contributor spotlight

---

## Questions?

Open a [GitHub Discussion](https://github.com/Aashish-po/nepal-ag-dashboard/discussions) or email <aashish.paudel@example.com>.

---

*Thank you for contributing to agricultural intelligence for Nepal!* 🌾
