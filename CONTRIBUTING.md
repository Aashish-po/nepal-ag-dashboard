# Contributing to Nepal Agricultural Intelligence Dashboard

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

- Search existing issues first to avoid duplicates
- Use the bug report template when opening a new issue
- Include steps to reproduce, expected behavior, and actual behavior
- Attach relevant logs, screenshots, or error messages

### Suggesting Features

- Search existing issues and discussions first
- Use the feature request template
- Explain the use case and why it aligns with the project's goals
- Consider whether the feature fits in v1 scope or should be deferred to Phase 2+

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feat/my-feature
   ```

3. **Make your changes** following the existing code style
4. **Run tests** to ensure nothing is broken:

   ```bash
   # Backend
   cd backend
   pytest tests/

   # Frontend
   cd frontend
   npm run test
   npm run type-check
   ```

5. **Run pre-commit hooks** to ensure code quality:

   ```bash
   pre-commit run --all-files
   ```

6. **Commit your changes** using [Conventional Commits](https://www.conventionalcommits.org/):

   ```bash
   git commit -m "feat: add my feature"
   ```

7. **Push to your fork** and open a pull request against `main`

## Development Setup

See the [Quick Start guide in README.md](README.md#quick-start-local-development) for local development setup instructions.

## Coding Standards

### Backend (Python)

- Follow PEP 8
- Use `black` for formatting (line length: 100)
- Use `isort` for import sorting
- Use `flake8` for linting
- Write type hints for function signatures
- Include docstrings for public functions and classes

### Frontend (TypeScript/React)

- Use TypeScript strict mode
- Follow React best practices (functional components, hooks)
- Use Tailwind CSS for styling
- Use the existing component library (shadcn/ui)
- Write accessible components (WCAG 2.1 AA)

### Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `style:` formatting, missing semicolons, etc.
- `refactor:` code change that neither fixes a bug nor adds a feature
- `perf:` performance improvement
- `test:` adding missing tests
- `chore:` maintenance tasks

## Project Structure

```text
nepal-ag-dashboard/
├── frontend/          # React + TypeScript + Vite
├── backend/           # FastAPI + SQLAlchemy
├── plans/             # Planning documents (PRD, TRD, etc.)
├── .github/           # CI/CD workflows
└── README.md
```

## Testing

All contributions should include appropriate tests:

- **Backend:** Unit tests in `backend/tests/unit/`, integration tests in `backend/tests/integration/`
- **Frontend:** Component tests in `frontend/src/__tests__/`
- **E2E:** Critical user flows in `frontend/e2e/`

Run the full test suite before submitting a PR:

```bash
# Backend
cd backend
pytest tests/ --cov=backend

# Frontend
cd frontend
npm run test -- --coverage
npm run type-check
npm run build
```

## Questions?

- Open an issue for technical questions
- Review existing documentation in `plans/` for design decisions
- Check the [API Reference](plans/08_API_REFERENCE.md) for endpoint specifications

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
