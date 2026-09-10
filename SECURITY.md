# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly:

**Do not** create a public GitHub issue for security vulnerabilities.

Instead, email us at **<security@nepal-ag-dashboard.org>** (or <poudelashish572@gmail.com>) with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Any suggested fixes

We will:

- Acknowledge receipt within 48 hours
- Provide a timeline for fix within 7 days
- Credit you in the security advisory (if desired)

## Security Measures

### Application Security

- All API endpoints validate input with Pydantic models
- CORS restricted to known frontend domains
- No authentication required (v1 is public read-only)
- Rate limiting planned for v2
- Dependency scanning via Dependabot + pip-audit in CI

### Data Security

- All data is public agricultural statistics (no PII)
- HTTPS enforced at CDN/proxy layer
- Environment variables for all secrets (Render/Vercel dashboards)
- No hardcoded secrets in codebase

### Infrastructure Security

- Supabase: Row-level security available (Phase 2)
- Render: DDoS protection, WAF via Cloudflare (recommended)
- Upstash Redis: TLS encryption, IP allowlist
- Sentry: Error tracking with PII scrubbing

## Disclosure Policy

We follow coordinated vulnerability disclosure:

1. **Private disclosure** → We investigate and fix
2. **Fix released** → Patch deployed to production
3. **Public advisory** → GitHub Security Advisory published
4. **Credit** → Reporter acknowledged (with permission)

## Security Contacts

- **Primary**: Aashish Paudel (<aashish.paudel@example.com>)
- **Backup**: <security@nepal-ag-dashboard.org>

## Bug Bounty

No formal bug bounty program at this time. We appreciate responsible disclosure and will acknowledge contributors in our security advisories.
