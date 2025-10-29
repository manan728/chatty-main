# Chatty Backend - Platform-Ready Chat API

A production-ready chat application backend built with FastAPI, Socket.IO, PostgreSQL, and Redis. This project demonstrates how to evolve a working API into a platform-ready service with proper DevOps, infrastructure, and SDLC best practices.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Poetry 2.2.0+ (for local development)

### Local Development with Docker

```bash
# Clone the repository
git clone <repository-url>
cd chatty-main

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f chatty-app

# Stop services
docker-compose down
```

The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health/
- **Metrics**: http://localhost:8000/metrics

### Local Development with Poetry

```bash
# Install dependencies
cd app
poetry install

# Copy environment configuration
cp ../env.example .env

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run database migrations
poetry run alembic upgrade head

# Start the application
poetry run python run.py
```

## 🏗️ Architecture

### Core Components

- **FastAPI**: Modern, fast web framework for building APIs
- **Socket.IO**: Real-time bidirectional event-based communication
- **PostgreSQL**: Primary database for data persistence
- **Redis**: Caching and session management
- **Alembic**: Database migration management
- **Prometheus**: Metrics collection and monitoring

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
- Custom business metrics

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

- Database connectivity
- Redis connectivity
- Application status
- Dependencies status

## 🔧 Configuration

Environment variables control application behavior:

```bash
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://:password@host:6379/0

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com
```

## 🚀 Deployment

### AWS Deployment

1. **Setup Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

2. **Deploy Application**:
   ```bash
   # Build and push to ECR
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
   docker build -t chatty .
   docker tag chatty:latest <account>.dkr.ecr.us-west-2.amazonaws.com/chatty:latest
   docker push <account>.dkr.ecr.us-west-2.amazonaws.com/chatty:latest
   
   # Update ECS service
   aws ecs update-service --cluster chatty-cluster --service chatty-service --force-new-deployment
   ```

### Local Production-like Setup

```bash
# Start with monitoring stack
docker-compose --profile monitoring up -d

# Access services
# - Application: http://localhost:8000
# - Prometheus: http://localhost:9091
# - Grafana: http://localhost:3000 (admin/admin_password)
```

## 🧪 Testing

### Unit Tests

```bash
cd app
poetry run pytest -v
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run smoke tests
cd app
poetry run pytest tests_smoke/ -v
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

- **Connection Pooling**: Database connection management
- **Caching**: Redis for session and data caching
- **Async Operations**: FastAPI async/await support
- **Load Balancing**: Application Load Balancer
- **Auto Scaling**: ECS service auto-scaling

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

### Code Quality

```bash
# Linting
poetry run ruff check .
poetry run ruff format .

# Type checking
poetry run mypy .

# Security scan
poetry run bandit -r src/
```

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔄 CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Testing**: Unit tests, integration tests, smoke tests
2. **Code Quality**: Linting, type checking, security scanning
3. **Building**: Docker image creation and ECR push
4. **Deployment**: ECS service update

## 📋 TODO / Future Enhancements

- [ ] Authentication & Authorization (JWT, OAuth2)
- [ ] Rate limiting and throttling
- [ ] Message persistence with Redis streams
- [ ] File upload support
- [ ] Push notifications
- [ ] Multi-tenant support
- [ ] Advanced monitoring dashboards
- [ ] Disaster recovery procedures
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
