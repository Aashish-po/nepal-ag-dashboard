# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public issue for security vulnerabilities
2. Send a detailed report to the project owner (see README.md for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- You will receive an acknowledgment within **48 hours**
- You will receive a detailed response within **7 days** with next steps
- Critical vulnerabilities will be patched as soon as possible

## Security Best Practices

This project follows these security practices:

- All dependencies are regularly audited (Dependabot, `pip-audit`)
- Secrets are managed via environment variables (never committed)
- CORS is configured to restrict origins in production
- Input validation is enforced via Pydantic schemas
- HTTPS is enforced in production
- No PII is collected; all data is public agricultural statistics
