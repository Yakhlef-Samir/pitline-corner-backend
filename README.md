# Pitline Corner - Backend

Virtual Pit Wall : API Backend FastAPI pour l'analyse stratégique post-course Formula 1.

## Tech Stack

- **Framework:** FastAPI 0.100+ with Python 3.11+
- **Database:** PostgreSQL with SQLAlchemy 2.0+ (async)
- **Cache:** Redis
- **Migrations:** Alembic
- **Documentation:** OpenAPI/Swagger (auto-generated)
- **Testing:** Pytest
- **Linting:** Black, isort, flake8

## Project Structure

```
pitline-corner-backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core configuration
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── utils/          # Utility functions
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── Dockerfile          # Docker configuration
└── README.md          # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

### Development

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black .
isort .

# Lint code
flake8 .
```

### API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Database

### Models

- Users (authentication)
- Races (F1 race data)
- Sessions (practice, qualifying, race)
- Drivers, Teams, Circuits
- Strategy simulations

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Redis Cache

Used for:
- Session storage
- API response caching
- Real-time data

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
DEBUG=True
```

## Deployment

### Docker

```bash
# Build image
docker build -t pitline-corner-backend .

# Run container
docker run -p 8000:8000 pitline-corner-backend
```

### Render (Recommended)

1. Connect GitHub repository to Render
2. Configure environment variables
3. Deploy automatically on push

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token

### Races
- `GET /api/v1/races` - List races
- `GET /api/v1/races/{id}` - Race details
- `GET /api/v1/races/{id}/sessions` - Race sessions

### Strategy
- `POST /api/v1/strategy/simulate` - Run simulation
- `GET /api/v1/strategy/results/{id}` - Get simulation results

## Code Conventions

- **Python:** Black formatting, PEP 8
- **Database:** snake_case for tables/columns
- **API:** RESTful, snake_case for endpoints
- **Testing:** pytest with fixtures

## Browser Support

API supports all modern browsers and HTTP clients.

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

Private - All rights reserved
