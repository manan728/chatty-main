<<<<<<< HEAD
# Chatty Backend - Platform-Ready Chat API

A production-ready chat application backend built with FastAPI, Socket.IO, and SQLite. This project demonstrates how to evolve a working API into a platform-ready service with proper DevOps, infrastructure, and SDLC best practices.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Poetry 2.2.0+ (for local development)

### Local Development with Docker

#### Option 1: Standalone Application Container (Simple)

```bash
# Clone the repository and enter it
git clone <repository-url>
cd chatty-main

# Build the application image
docker build -t chatty:latest .

# Run the application container (uses SQLite internally)
docker run -d --name chatty \
  -p 8000:8000 \
  -e APP_ENV=development \
  -e DEBUG=false \
  -e ENABLE_METRICS=true \
  -e DATABASE_URL=sqlite:///./chatty.db \
  chatty:latest

# View logs
docker logs -f chatty

# Stop the container
docker stop chatty
docker rm chatty
```

#### Option 2: Full Stack with Monitoring

```bash
# Build the application image (only needed the first time or after code changes)
docker build -t chatty:latest .

# Start the application container
docker run -d --name chatty \
  -p 8000:8000 \
  -e APP_ENV=development \
  -e DEBUG=false \
  -e ENABLE_METRICS=true \
  -e DATABASE_URL=sqlite:///./chatty.db \
  chatty:latest

# Start only monitoring services (Prometheus + Grafana)
# Note: Start ONLY prometheus and grafana to avoid port conflicts with standalone chatty container
docker compose up -d prometheus grafana

# View app logs
docker logs -f chatty

# Stop everything
docker stop chatty && docker rm chatty
docker compose stop prometheus grafana
docker compose rm -f prometheus grafana
```

When running, the application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health/
- **Metrics**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9091 (if monitoring stack is running)
- **Grafana**: http://localhost:3000 (if monitoring stack is running)

**Current Setup (3 containers):**
- `chatty` (FastAPI + Socket.IO app using SQLite)
- `chatty-prometheus` (Prometheus metrics collection)
- `chatty-grafana` (Grafana visualization)

**Notes:**
- The app uses SQLite database stored inside the container (temporary, as per requirements)
- No external database services (Postgres/Redis) required for basic operation
- Monitoring stack is optional and can be started separately with the monitoring profile

### Local Development with Poetry

```bash
# Install dependencies
cd app
poetry install

# Set environment variables (or create .env file)
export APP_ENV=development
export DEBUG=true
export DATABASE_URL=sqlite:///./chatty.db
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run database migrations
poetry run alembic upgrade head

# Start the application
poetry run python run.py
```

**Note:** This setup uses SQLite, so no external database services are needed. The database file (`chatty.db`) will be created in the `app` directory.

## 🏗️ Architecture

### Core Components

- **FastAPI**: Modern, fast web framework for building APIs
- **Socket.IO**: Real-time bidirectional event-based communication
- **SQLite**: Embedded database for data persistence (temporary storage as per requirements)
- **Alembic**: Database migration management
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization and dashboards

### Infrastructure

- **Docker**: Containerization with multi-stage builds
- **Docker Compose**: Local development environment
- **AWS**: Cloud infrastructure (ECS, RDS, ElastiCache, ALB)
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD pipeline

## 📊 Monitoring & Observability

### Metrics

The application exposes Prometheus metrics at `/metrics`:

- HTTP request count and duration
- Socket.IO active connections
- Database connection pool status
- Message and user counts


### Logging

Structured JSON logging with configurable levels:

```json
{
  "event": "Incoming request",
  "method": "POST",
  "path": "/messages/",
  "client_ip": "192.168.1.100",
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info"
}
```

### Health Checks

Comprehensive health checks at `/health/`:

- Database connectivity (SQLite)
- Application status
- Service dependencies

## 🔧 Configuration

Environment variables control application behavior:

```bash
# Application
APP_ENV=development          # or production, staging
DEBUG=false                 # Set to true for development
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_METRICS=true         # Enable Prometheus metrics endpoint

# Database (SQLite - default)
DATABASE_URL=sqlite:///./chatty.db

# For PostgreSQL (optional, if you want to use it instead)
# DATABASE_URL=postgresql://user:pass@host:5432/db

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Optional: Monitoring Stack (Prometheus + Grafana)

**Important:** Only start monitoring services if your app is already running with `docker run` (to avoid port conflicts).

```bash
# Start only Prometheus and Grafana services
docker compose up -d prometheus grafana

# Access services
# - Application: http://localhost:8000 (must be running separately)
# - Prometheus: http://localhost:9091
# - Grafana: http://localhost:3000 (admin/admin_password)

# Stop monitoring services
docker compose stop prometheus grafana
```

**Setup Grafana Dashboard:**

1. Open http://localhost:3000 and login (admin/admin_password)
2. Go to **Configuration** → **Data Sources** → **Add data source**
3. Select **Prometheus**
4. Set URL to: `http://chatty-prometheus:9090`
5. Click **Save & Test**
6. Create dashboards with metrics like:
   - `rate(http_requests_total[5m])` - Request rate
   - `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` - Response time
   - `socketio_active_connections` - Active Socket.IO connections

**Note:** Prometheus is configured to scrape your app at `http://host.docker.internal:8000/metrics`. Make sure your app container has `ENABLE_METRICS=true` set.

### Rebuilding the App Image After Code Changes

```bash
# Stop the running container
docker stop chatty && docker rm chatty

# Rebuild the image
docker build -t chatty:latest .

# Start the container again
docker run -d --name chatty \
  -p 8000:8000 \
  -e APP_ENV=development \
  -e DEBUG=false \
  -e ENABLE_METRICS=true \
  -e DATABASE_URL=sqlite:///./chatty.db \
  chatty:latest
```

## 🧪 Testing

### Unit Tests

```bash
cd app
poetry run pytest -v
```

Or without Poetry (if using venv):
```bash
cd app
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest -v
```

### Code Coverage

**Coverage Requirement:** 70% minimum (enforced in CI/CD pipeline)

**Run tests with coverage:**
```bash
cd app
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Install coverage tool if not already installed
pip install pytest-cov

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=70

# View HTML report
open htmlcov/index.html  # macOS
# or just open htmlcov/index.html in your browser
```

**Coverage reports include:**
- Terminal output showing coverage percentage and missing lines
- HTML report (generated in `htmlcov/` directory) with detailed line-by-line coverage
- XML report (for CI/CD integration)

**CI/CD Pipeline:**
- Coverage is automatically calculated on every push/PR
- Pipeline **fails** if coverage drops below 70%
- Coverage HTML report is uploaded as an artifact

### Integration Tests

```bash
# Start services
docker compose up -d prometheus grafana

# Run smoke tests
cd app
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests_smoke/ -v
```

### Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/docs/getting-started/installation/

# Run load test
k6 run load-test.js
```

## 🔒 Security

- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models for request/response validation
- **SQL Injection**: SQLAlchemy ORM prevents SQL injection
- **Secrets Management**: Environment-based configuration
- **Container Security**: Non-root user, minimal base images
- **Network Security**: VPC, security groups, encrypted storage

## 📈 Performance

- **Async Operations**: FastAPI async/await support for high concurrency
- **Database Indexes**: Optimized queries with proper indexing on foreign keys
- **Connection Management**: Efficient SQLite connection handling
- **Load Balancing**: Application Load Balancer (for AWS deployment)
- **Auto Scaling**: ECS service auto-scaling (for AWS deployment)

## 🛠️ Development

### Database Migrations

```bash
# Create migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Socket.IO Real-Time Communication

The application includes Socket.IO for real-time message updates! 

**See [SOCKETIO_GUIDE.md](SOCKETIO_GUIDE.md) for complete client connection examples and usage.**

**Quick Start:**
- Socket.IO server runs at: `http://localhost:8000/socket.io`
- Connect your client and emit `join` event with `user_id` and `chatroom_id`
- Listen for `new_message` events to receive real-time updates
- Messages posted via REST API are automatically broadcasted to all clients in the chatroom

**Example:** When someone posts a message via `POST /messages/`, all Socket.IO clients joined to that chatroom receive the `new_message` event instantly!

## 🔄 CI/CD Pipeline 

The GitHub Actions workflow includes:

1. **Testing**: Unit tests, integration tests, smoke tests
   - Code coverage requirement: **70% minimum** (pipeline fails if below threshold)
   - Coverage reports generated in multiple formats (terminal, HTML, XML)
2. **Code Quality**: Linting, type checking, security scanning
3. **Building**: Docker image creation and ECR push (only if tests pass)
4. **Deployment**: ECS service update (only if build succeeds)

## 📋 TODO / Future Enhancements

- [ ] Authentication & Authorization (JWT, OAuth2)
- [ ] Rate limiting and throttling
- [ ] Push notifications
- [ ] Advanced monitoring dashboards
- [ ] Performance optimization
- [ ] API versioning strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
=======
# chatty-main
Chat service for members
>>>>>>> 6d16dc0200723f11d1cd4992f7d89e7a608c46cd
