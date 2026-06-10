# Contributing to VisionGrid

Thank you for your interest in contributing to VisionGrid! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional, for containerized development)
- A camera or video source for testing (webcam, RTSP stream, or video file)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend
pytest
pytest --cov=visiongrid  # With coverage

# Frontend
cd frontend
npm test
npm run test:coverage
```

## Code Style

### Python (Backend)

- We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Type hints are required for all public functions
- Follow PEP 8 naming conventions

```bash
ruff check .
ruff format .
mypy .
```

### TypeScript (Frontend)

- ESLint + Prettier for linting/formatting
- Strict TypeScript mode enabled
- Functional components with hooks

```bash
npm run lint
npm run format
```

## Git Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run tests and linting
5. Commit with conventional commits: `feat: add zone crossing detection`
6. Push and open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `refactor:` — Code change that neither fixes a bug nor adds a feature
- `test:` — Adding or updating tests
- `chore:` — Build process or auxiliary tool changes

## Architecture Guidelines

### Adding a New Camera Protocol

1. Create a new connector in `backend/visiongrid/cameras/`
2. Implement the `CameraConnector` protocol (see `base.py`)
3. Register it in the connector factory
4. Add tests in `backend/tests/cameras/`

### Adding a New Detection Model

1. Create a model wrapper in `backend/visiongrid/detection/models/`
2. Implement the `DetectionModel` protocol
3. Register it in the model registry
4. Add benchmarks and tests

### Adding a New Alert Channel

1. Create a notifier in `backend/visiongrid/events/notifiers/`
2. Implement the `Notifier` protocol
3. Register in the notification router
4. Document configuration in the README

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include your OS, Python version, and camera model when reporting bugs
- Provide minimal reproduction steps

## Code of Conduct

Be respectful, inclusive, and constructive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
