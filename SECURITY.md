# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do

- **Report privately** - Do not open a public issue for security vulnerabilities
- **Email or DM** - Contact the maintainers directly through GitHub
- **Provide details** - Include steps to reproduce, potential impact, and suggested fixes if possible
- **Allow time** - Give us reasonable time to address the issue before public disclosure

### Don't

- Don't exploit the vulnerability beyond what's necessary to demonstrate it
- Don't access or modify other users' data
- Don't perform actions that could harm the service or its users

## Security Measures

This project implements the following security practices:

### Application Security

- **No sensitive data storage** - We don't collect or store user credentials
- **Input validation** - All API inputs are validated
- **SQL injection prevention** - Using SQLModel ORM with parameterized queries
- **CORS configuration** - Restricted to allowed origins

### Scraping Security

- **No authentication bypass** - We only access public endpoints
- **Rate limiting** - Conservative delays to prevent service impact
- **Respectful crawling** - Following robots.txt directives

### Infrastructure

- **Docker isolation** - Services run in isolated containers
- **Environment variables** - Sensitive configuration via env vars
- **No hardcoded secrets** - Credentials are never committed to the repository

## Response Timeline

- **Initial response**: Within 48 hours
- **Status update**: Within 7 days
- **Resolution target**: Within 30 days (depending on complexity)

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report valid vulnerabilities (with their permission).

---

Thank you for helping keep this project secure!
