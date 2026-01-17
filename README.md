# Weather Sensor Metrics API

A production-ready REST API for ingesting and querying weather sensor metrics built with FastAPI, AWS Lambda, and PostgreSQL. This project demonstrates modern cloud-native architecture patterns while maintaining 100% AWS Free Tier compliance.

## 🚀 Live Demo

**API Endpoint:** `https://dsiuqwaqe3.execute-api.us-east-1.amazonaws.com/prod/`

```bash
# Ingest a temperature reading
curl -X POST "https://dsiuqwaqe3.execute-api.us-east-1.amazonaws.com/prod/metrics" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": 1,
    "metric_type": "temperature",
    "value": 22.5,
    "timestamp": "2024-01-15T10:00:00"
  }'

# Query average temperature for date range
curl "https://dsiuqwaqe3.execute-api.us-east-1.amazonaws.com/prod/query?sensors=1&metrics=temperature&statistic=avg&start_date=2024-01-15&end_date=2024-01-16"

# Query latest temperature reading (no date range)
curl "https://dsiuqwaqe3.execute-api.us-east-1.amazonaws.com/prod/query?sensors=1&metrics=temperature"
```

## 📋 Features

- **RESTful API** with FastAPI framework
- **Real-time ingestion** of sensor metrics (temperature, humidity, wind speed, etc.)
- **Statistical aggregation** (min, max, average, sum) with flexible date-range querying
- **Latest data queries** with ingestion timestamps when no date range specified
- **Multi-sensor support** with time-based filtering
- **Production-grade security** with input validation and rate limiting
- **Serverless architecture** using AWS Lambda for automatic scaling
- **Persistent storage** with PostgreSQL on Amazon RDS
- **CI/CD pipeline** with comprehensive testing and security scanning
- **100% AWS Free Tier compliant** - runs at $0/month

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│ Lambda Functions │───▶│ RDS PostgreSQL  │
│   (REST API)    │    │ (Ingest + Query) │    │   (Metrics DB)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Secrets Manager  │
                       │ (DB Credentials) │
                       └──────────────────┘
```

### Technology Stack

**Backend**
- **FastAPI 0.115.0** - Modern Python web framework with automatic OpenAPI docs
- **SQLAlchemy 2.0.35** - Python SQL toolkit and ORM
- **Pydantic 2.9.2** - Data validation using Python type annotations
- **Mangum 0.17.0** - ASGI adapter for running FastAPI on AWS Lambda

**Infrastructure**
- **AWS Lambda** - Serverless compute (Python 3.11 runtime)
- **Amazon API Gateway** - REST API with built-in throttling and CORS
- **Amazon RDS PostgreSQL** - Managed relational database (db.t3.micro)
- **AWS Secrets Manager** - Secure credential storage
- **Amazon VPC** - Network isolation and security groups

**DevOps**
- **AWS CDK (Python)** - Infrastructure as Code
- **GitHub Actions** - CI/CD pipeline with OIDC authentication
- **Docker** - Local development environment
- **pytest** - Unit and integration testing

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Node.js 20+ (for AWS CDK)
- AWS CLI configured

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/SidPhysics/random-sensor-poc-xyz789
   cd random-sensor-poc-xyz789
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run with Docker Compose**
   
   **⚠️ Important:** Ensure Docker Desktop is running before proceeding.
   
   ```bash
   # Start Docker Desktop first, then run:
   docker-compose up --build
   ```
   
   **Troubleshooting:**
   - If you get "cannot connect to Docker daemon" error, start Docker Desktop
   - On Windows, Docker Desktop must be fully started (whale icon in system tray)
   - Alternative: Use the live API endpoints instead of local setup

4. **Test the APIs**
   ```bash
   # Ingest endpoint (port 8000)
   curl -X POST http://localhost:8000/metrics \
     -H "Content-Type: application/json" \
     -d '{
       "sensor_id": 1,
       "metric_type": "temperature",
       "value": 22.5,
       "timestamp": "2024-01-15T10:00:00"
     }'

   # Query endpoint with date range (port 8001)
   curl "http://localhost:8001/query?sensors=1&metrics=temperature&statistic=avg&start_date=2024-01-15&end_date=2024-01-16"
   
   # Query latest data (port 8001)
   curl "http://localhost:8001/query?sensors=1&metrics=temperature"
   ```

### Project Structure

```
random-sensor-poc-xyz789/
├── ingest/                 # Ingest Lambda function
│   ├── app.py             # FastAPI app for metric ingestion
│   └── handler.py         # Lambda handler
├── query/                 # Query Lambda function
│   ├── app.py             # FastAPI app for metric queries
│   └── handler.py         # Lambda handler
├── shared/                # Shared code between services
│   ├── database.py        # Database connection and session management
│   ├── models.py          # SQLAlchemy ORM models
│   └── schemas.py         # Pydantic request/response schemas
├── cdk/                   # AWS CDK infrastructure code
│   ├── stacks/
│   │   ├── network_stack.py    # VPC, subnets, security groups
│   │   ├── database_stack.py   # RDS PostgreSQL instance
│   │   ├── lambda_stack.py     # Lambda functions and layers
│   │   └── api_stack.py        # API Gateway configuration
│   └── app.py             # CDK app entry point
├── tests/                 # Test suite
│   ├── test_ingest.py     # Unit tests for ingest API
│   ├── test_query.py      # Unit tests for query API
│   └── integration/       # Integration tests against live API
├── scripts/               # Utility scripts
│   └── validate_free_tier.py  # Free tier compliance validator
├── .github/workflows/     # CI/CD pipeline
│   └── ci-cd.yml         # GitHub Actions workflow
├── docker-compose.yml     # Local development setup
└── requirements.txt       # Python dependencies
```

## 🔧 API Reference

### Ingest Metrics

**POST** `/metrics`

Ingest a new sensor metric reading.

**Request Body:**
```json
{
  "sensor_id": 1,
  "metric_type": "temperature",
  "value": 22.5,
  "timestamp": "2024-01-15T10:00:00"
}
```

**Response:**
```json
{
  "message": "Metric ingested successfully",
  "id": 123
}
```

**Supported Metric Types:**
- `temperature` (°C)
- `humidity` (%)
- `wind_speed` (m/s)
- `pressure` (hPa)

### Query Metrics

**GET** `/query`

Query aggregated sensor metrics with flexible filtering.

**Query Parameters:**
- `sensors` - Sensor IDs (comma-separated) or "all"
- `metrics` - Metric types (comma-separated)
- `statistic` - Aggregation function: `min`, `max`, `avg`, `sum` (required for date ranges)
- `start_date` - Start date (YYYY-MM-DD, optional)
- `end_date` - End date (YYYY-MM-DD, optional)

**Query Types:**

1. **Latest Data Query** (no date range):
   ```
   GET /query?sensors=1&metrics=temperature
   ```
   Returns the most recent value with ingestion timestamp.

2. **Aggregated Query** (with date range):
   ```
   GET /query?sensors=1&metrics=temperature&statistic=avg&start_date=2024-01-15&end_date=2024-01-16
   ```
   Returns statistical aggregation over the specified period.

**Example:**
```
GET /query?sensors=1,2&metrics=temperature,humidity&statistic=avg&start_date=2024-01-15&end_date=2024-01-16
```

**Latest Data Response:**
```json
{
  "statistic": "latest",
  "results": {
    "1": {
      "temperature": 22.5,
      "ingested_at": "2024-01-15T10:00:00"
    }
  }
}
```

**Aggregated Data Response:**
```json
{
  "statistic": "avg",
  "results": {
    "1": {
      "temperature": 23.75,
      "humidity": 65.0
    },
    "2": {
      "temperature": 18.5
    }
  }
}
```

## 🚀 Deployment

### AWS Infrastructure

The application uses AWS CDK for Infrastructure as Code. All resources are configured for AWS Free Tier compliance.

**Key Components:**
- **API Gateway REST API** - Request routing and throttling (100 req/client)
- **Lambda Functions** - Serverless compute (128MB memory, 30s timeout)
- **RDS PostgreSQL** - db.t3.micro instance with 20GB storage
- **VPC** - Network isolation with public subnets only
- **Secrets Manager** - Secure database credential storage

### CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline:

1. **Security Scanning**
   - Dependency vulnerability scan (Safety)
   - Code security analysis (Bandit)
   - Secret detection (TruffleHog)
   - Static analysis (CodeQL)

2. **Code Quality**
   - Code formatting (Black)
   - Linting (Flake8)
   - Type checking (MyPy)

3. **Testing & Deployment**
   - Unit tests (pytest) - Run before deployment
   - Integration tests against live API - Run after deployment
   - Free tier compliance validation

4. **Deployment**
   - CDK synthesis and deployment
   - Automatic rollback on failure

### Manual Deployment

1. **Install CDK**
   ```bash
   npm install -g aws-cdk
   pip install -r requirements-cdk.txt
   ```

2. **Configure AWS credentials**
   ```bash
   aws configure
   ```

3. **Deploy infrastructure**
   ```bash
   cdk bootstrap
   cdk deploy --all
   ```

## 🧪 Testing

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests (requires deployed API)
pytest tests/integration/ -v

# Code quality checks
black --check .
flake8 .
mypy .
```

### Test Strategy

**Unit Tests**
- FastAPI endpoint testing with TestClient
- Database operations with SQLite in-memory
- Input validation and error handling
- Timestamp-based test isolation

**Integration Tests**
- End-to-end API testing against live AWS deployment
- Real database operations with PostgreSQL
- Error handling and rate limiting validation
- Data consistency verification

## 🔒 Security

### Security Measures

- **Input Validation** - Pydantic schemas prevent injection attacks
- **Rate Limiting** - API Gateway throttling (100 requests per client)
- **Network Security** - VPC with security groups restricting database access
- **Credential Management** - AWS Secrets Manager for database passwords
- **Least Privilege IAM** - Lambda functions have minimal required permissions
- **HTTPS Only** - All API communication encrypted in transit

### Security Scanning

Automated security scanning in CI/CD pipeline:
- **SAST** (Static Application Security Testing) with Bandit
- **Dependency Scanning** with Safety for known CVEs
- **Secret Detection** with TruffleHog
- **Code Quality** analysis with CodeQL

## 💰 Cost Optimization

### AWS Free Tier Compliance

The entire infrastructure runs within AWS Free Tier limits:

- **Lambda**: 1M requests/month, 400,000 GB-seconds compute
- **API Gateway**: 1M API calls/month
- **RDS**: db.t3.micro instance, 20GB storage, single-AZ
- **Secrets Manager**: 30-day free trial, then ~$0.40/month
- **Data Transfer**: 1GB/month outbound

**Estimated Monthly Cost: $0.40** (Secrets Manager only)

### Cost-Saving Design Decisions

1. **Lambda Outside VPC** - Avoids NAT Gateway costs ($32/month)
2. **ZIP Deployment** - No ECR storage charges
3. **Single-AZ RDS** - No Multi-AZ redundancy costs
4. **Public Subnets Only** - No VPC Endpoint costs ($7/month)
5. **Minimal Lambda Memory** - 128MB reduces compute costs

## 🔄 Design Decisions

### Lambda Outside VPC

**Decision:** Deploy Lambda functions outside VPC instead of inside private subnets.

**Rationale:**
- Eliminates need for NAT Gateway ($32/month) or VPC Endpoints ($7/month)
- Faster cold starts (no ENI creation delay)
- Direct access to AWS services (Secrets Manager, CloudWatch)
- Maintains security through RDS security groups and encrypted credentials

**Trade-off:** RDS must be publicly accessible, but still protected by security groups and strong authentication.

### Microservices Architecture

**Decision:** Split into separate Lambda functions for ingest and query operations.

**Benefits:**
- Independent scaling based on workload patterns
- Isolated deployments and rollbacks
- Different IAM permissions per function
- Separate monitoring and logging

### Timestamp-Based Test Isolation

**Decision:** Use specific timestamps in tests instead of database cleanup.

**Benefits:**
- Tests never delete production data
- Parallel test execution without conflicts
- Realistic testing scenarios
- Simple test setup without complex teardown

## 🚧 Future Enhancements

### Short Term
- [ ] API authentication with JWT tokens
- [ ] Metric data retention policies
- [ ] Real-time alerting for anomalous readings

### Medium Term
- [ ] GraphQL API for complex queries
- [ ] WebSocket support for real-time data streaming
- [ ] Machine learning models for predictive analytics

### Long Term
- [ ] Multi-region deployment for global availability
- [ ] Data lake integration with Amazon S3
- [ ] Advanced monitoring with custom CloudWatch metrics


---

