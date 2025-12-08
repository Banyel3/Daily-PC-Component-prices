# Contributing to Daily PC Component Prices

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Git

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Banyel3/Daily-PC-Component-prices.git
   cd Daily-PC-Component-prices
   ```

2. **Start services with Docker**

   ```bash
   docker-compose up -d
   ```

3. **For frontend development**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **For backend development**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Banyel3/Daily-PC-Component-prices/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, browser, etc.)

### Suggesting Features

1. Open a new issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

### Python (Backend)

- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow ESLint configuration
- Use functional components with hooks

## Project Structure

```
├── backend/
│   ├── models/         # SQLModel database models
│   ├── routes/         # FastAPI route handlers
│   ├── scrapers/       # Web scraping logic
│   ├── tasks/          # Celery background tasks
│   └── main.py         # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   └── layouts/    # Layout components
│   └── package.json
├── scripts/            # Utility scripts
└── docker-compose.yml
```

## Important Notes

### Scraping Ethics

When contributing to scraping functionality:

- **Always respect robots.txt** - Check allowed/disallowed paths
- **Maintain rate limits** - Keep delays at 5+ seconds between requests
- **No aggressive scraping** - Don't add features that allow users to trigger scrapes
- **Test responsibly** - Use small page limits during development

See [LEGAL.md](LEGAL.md) for full compliance details.

## Questions?

Feel free to open an issue for any questions about contributing.

---

Thank you for contributing! 🎉
