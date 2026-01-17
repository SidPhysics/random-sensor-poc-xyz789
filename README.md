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

## 🔒 Security & IAM

### AWS IAM Architecture

The project implements a **least-privilege security model** with role-based access control across all AWS services.

#### Lambda Function Permissions

**Ingest & Query Lambda Functions:**
- **Secrets Manager**: `secretsmanager:GetSecretValue` - Read database credentials only
- **CloudWatch Logs**: Automatic logging permissions via CDK
- **No VPC permissions** - Functions run outside VPC for cost optimization

```python
# CDK automatically creates minimal IAM roles
db_secret.grant_read(self.ingest_function)  # Only read access to DB secret
db_secret.grant_read(self.query_function)   # Only read access to DB secret
```

#### Database Security

**RDS PostgreSQL Security:**
- **Network**: Security group allows connections only on port 5432
- **Authentication**: Strong auto-generated passwords stored in Secrets Manager
- **Encryption**: Data encrypted at rest and in transit
- **Public Access**: Required for Lambda outside VPC, but password-protected

```python
# Security group configuration
self.db_security_group.add_ingress_rule(
    peer=ec2.Peer.any_ipv4(),  # Public access required for Lambda outside VPC
    connection=ec2.Port.tcp(5432),  # PostgreSQL port only
    description="Allow PostgreSQL connections (Lambda outside VPC)"
)
```

#### API Gateway Security

**Rate Limiting & Throttling:**
- **Global Limit**: 1,000 requests/second with 2,000 burst
- **Per-Client Limit**: 100 requests/second with 50 burst
- **Monthly Quota**: 10,000 requests per API key
- **No Authentication Required**: Public API for demo purposes

```python
# Usage plan configuration
usage_plan = api.add_usage_plan(
    throttle=apigw.ThrottleSettings(
        rate_limit=100,   # Per client
        burst_limit=50,   # Per client
    ),
    quota=apigw.QuotaSettings(
        limit=10000,      # Per month per client
        period=apigw.Period.MONTH,
    ),
)
```

### GitHub Actions CI/CD Security

#### OpenID Connect (OIDC) Authentication

The project uses **OIDC Web Identity Federation** instead of long-lived AWS access keys for enhanced security.

**Setup Process:**
1. **OIDC Provider**: Created in AWS IAM for `token.actions.githubusercontent.com`
2. **IAM Role**: `GitHubActionsCDKDeployRole` with deployment permissions
3. **Trust Policy**: Restricts access to specific repository and branch
4. **GitHub Secret**: `AWS_ROLE_ARN` contains the role ARN for assumption

**Trust Policy (Repository-Specific):**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:SidPhysics/random-sensor-poc-xyz789:ref:refs/heads/main"
      }
    }
  }]
}
```

#### Deployment Role Permissions

The `GitHubActionsCDKDeployRole` follows **least-privilege principles** with resource-specific permissions:

**CloudFormation**: Stack management for `weather-sensor-poc-*` and `CDKToolkit` only
**S3**: CDK asset storage in account-specific buckets only
**IAM**: Role management for Lambda functions with `weather-sensor-poc-*` prefix only
**Lambda**: Function and layer management with project prefix only
**EC2**: VPC and networking resources (no instance permissions)
**RDS**: Database management with project prefix only
**Secrets Manager**: Secret management with project prefix only
**API Gateway**: REST API management in us-east-1 region only
**SSM**: CDK bootstrap parameters only

**Security Boundaries:**
- **Resource Prefixes**: All permissions scoped to `weather-sensor-poc-*` resources
- **Region Restriction**: Limited to `us-east-1` region
- **Account Boundary**: All ARNs include specific AWS account ID
- **Branch Restriction**: Only `main` branch can trigger deployments

#### Secrets Management

**Database Credentials:**
- **Auto-Generated**: RDS creates strong random passwords
- **Secrets Manager**: Credentials stored encrypted at rest
- **Rotation**: Automatic rotation capability (not enabled for cost)
- **Access**: Lambda functions have read-only access via IAM

**GitHub Repository Secrets:**
- `AWS_ROLE_ARN`: Contains the deployment role ARN for OIDC assumption
- **No AWS Keys**: No long-lived access keys stored in GitHub

#### GitHub Deploy Role Setup

**Role Creation:**
The deployment uses a dedicated IAM role `GitHubActionsCDKDeployRole` with OIDC Web Identity Federation.

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:<GITHUB_USERNAME>/<REPOSITORY_NAME>:ref:refs/heads/main"
      }
    }
  }]
}
```

**Role Permissions:**
The deployment role includes the following scoped permissions:

1. **CloudFormation**: Stack management for `weather-sensor-poc-*` and `CDKToolkit` stacks
2. **S3**: CDK asset storage in account-specific buckets (`cdk-*-assets-<ACCOUNT>-us-east-1`)
3. **IAM**: Role management for Lambda functions with `weather-sensor-poc-*` and `cdk-*` prefixes
4. **Lambda**: Function and layer operations with project prefix
5. **EC2**: VPC, subnet, security group, and networking resource management
6. **RDS**: Database and subnet group operations with project prefix
7. **Secrets Manager**: Secret management with project prefix
8. **API Gateway**: REST API management in us-east-1 region
9. **SSM**: CDK bootstrap parameter access (`/cdk-bootstrap/*`)

**Deployment Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CDKBootstrapAndDeploy",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:GetTemplate",
        "cloudformation:ValidateTemplate",
        "cloudformation:CreateChangeSet",
        "cloudformation:DescribeChangeSet",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:DeleteChangeSet"
      ],
      "Resource": [
        "arn:aws:cloudformation:us-east-1:<ACCOUNT_ID>:stack/weather-sensor-poc-*",
        "arn:aws:cloudformation:us-east-1:<ACCOUNT_ID>:stack/CDKToolkit/*"
      ]
    },
    {
      "Sid": "S3CDKAssets",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:PutBucketPolicy",
        "s3:PutBucketVersioning",
        "s3:PutEncryptionConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::cdk-*-assets-<ACCOUNT_ID>-us-east-1",
        "arn:aws:s3:::cdk-*-assets-<ACCOUNT_ID>-us-east-1/*"
      ]
    },
    {
      "Sid": "IAMRolesForLambda",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PassRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRolePolicy",
        "iam:TagRole",
        "iam:UntagRole"
      ],
      "Resource": [
        "arn:aws:iam::<ACCOUNT_ID>:role/weather-sensor-poc-*",
        "arn:aws:iam::<ACCOUNT_ID>:role/cdk-*"
      ]
    },
    {
      "Sid": "LambdaFunctions",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:PublishLayerVersion",
        "lambda:DeleteLayerVersion",
        "lambda:GetLayerVersion",
        "lambda:AddPermission",
        "lambda:RemovePermission",
        "lambda:TagResource",
        "lambda:UntagResource"
      ],
      "Resource": [
        "arn:aws:lambda:us-east-1:<ACCOUNT_ID>:function:weather-sensor-poc-*",
        "arn:aws:lambda:us-east-1:<ACCOUNT_ID>:layer:weather-sensor-poc-*"
      ]
    },
    {
      "Sid": "VPCNetworking",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:DescribeVpcs",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:DescribeSubnets",
        "ec2:CreateRouteTable",
        "ec2:DeleteRouteTable",
        "ec2:DescribeRouteTables",
        "ec2:AssociateRouteTable",
        "ec2:DisassociateRouteTable",
        "ec2:CreateRoute",
        "ec2:DeleteRoute",
        "ec2:CreateInternetGateway",
        "ec2:DeleteInternetGateway",
        "ec2:AttachInternetGateway",
        "ec2:DetachInternetGateway",
        "ec2:DescribeInternetGateways",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:DescribeSecurityGroups",
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:AuthorizeSecurityGroupEgress",
        "ec2:RevokeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupEgress",
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:CreateTags",
        "ec2:DeleteTags",
        "ec2:DescribeAvailabilityZones"
      ],
      "Resource": "*"
    },
    {
      "Sid": "RDSDatabase",
      "Effect": "Allow",
      "Action": [
        "rds:CreateDBInstance",
        "rds:DeleteDBInstance",
        "rds:DescribeDBInstances",
        "rds:ModifyDBInstance",
        "rds:CreateDBSubnetGroup",
        "rds:DeleteDBSubnetGroup",
        "rds:DescribeDBSubnetGroups",
        "rds:AddTagsToResource",
        "rds:RemoveTagsFromResource"
      ],
      "Resource": [
        "arn:aws:rds:us-east-1:<ACCOUNT_ID>:db:weather-sensor-poc-*",
        "arn:aws:rds:us-east-1:<ACCOUNT_ID>:subgrp:weather-sensor-poc-*"
      ]
    },
    {
      "Sid": "SecretsManager",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:CreateSecret",
        "secretsmanager:DeleteSecret",
        "secretsmanager:DescribeSecret",
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:TagResource",
        "secretsmanager:UntagResource"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:weather-sensor-poc-*"
      ]
    },
    {
      "Sid": "APIGateway",
      "Effect": "Allow",
      "Action": [
        "apigateway:POST",
        "apigateway:PUT",
        "apigateway:PATCH",
        "apigateway:DELETE",
        "apigateway:GET"
      ],
      "Resource": [
        "arn:aws:apigateway:us-east-1::/restapis",
        "arn:aws:apigateway:us-east-1::/restapis/*"
      ]
    },
    {
      "Sid": "SSMParameters",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:PutParameter",
        "ssm:DeleteParameter"
      ],
      "Resource": [
        "arn:aws:ssm:us-east-1:<ACCOUNT_ID>:parameter/cdk-bootstrap/*"
      ]
    }
  ]
}
```

**Setup Commands:**
```bash
# Create OIDC provider (one-time setup)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Create deployment role
aws iam create-role \
  --role-name GitHubActionsCDKDeployRole \
  --assume-role-policy-document file://github-trust-policy.json

# Attach deployment policy
aws iam put-role-policy \
  --role-name GitHubActionsCDKDeployRole \
  --policy-name GitHubDeployPolicy \
  --policy-document file://github-deploy-policy.json
```

### Security Best Practices Implemented

#### ✅ **Implemented Security Measures**

1. **Least Privilege Access**
   - IAM roles with minimal required permissions
   - Resource-specific ARN restrictions
   - Time-limited OIDC tokens instead of permanent keys

2. **Defense in Depth**
   - API Gateway rate limiting
   - Database password authentication
   - Security group network restrictions
   - Input validation with Pydantic schemas

3. **Secrets Protection**
   - No hardcoded credentials in code
   - AWS Secrets Manager for database passwords
   - OIDC federation for CI/CD authentication

4. **Monitoring & Logging**
   - CloudWatch Logs for all Lambda functions
   - API Gateway access logging
   - CloudFormation stack event tracking

#### ⚠️ **Security Trade-offs for Cost Optimization**

1. **Public RDS Access**
   - **Risk**: Database accessible from internet
   - **Mitigation**: Strong password authentication, security groups
   - **Reason**: Avoids NAT Gateway costs ($32/month)

2. **No API Authentication**
   - **Risk**: Public API endpoints
   - **Mitigation**: Rate limiting, input validation
   - **Reason**: Demo/POC simplicity

3. **Lambda Outside VPC**
   - **Risk**: Functions not in private network
   - **Mitigation**: IAM permissions, encrypted connections
   - **Reason**: Avoids VPC Endpoint costs ($7/month)

### Security Compliance

**Industry Standards:**
- **OWASP**: Input validation, secure credential storage
- **AWS Well-Architected**: Security pillar best practices
- **NIST**: Least privilege access controls

**Automated Security Scanning:**
- **SAST**: Bandit for Python security analysis
- **Dependency Scanning**: Safety for known CVEs
- **Secret Detection**: TruffleHog for credential leaks
- **Code Quality**: CodeQL for security patterns

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
- [ ] IoT Core integration with Kinesis Firehose for scalable sensor ingestion
- [ ] Machine learning models for predictive analytics

### Long Term
- [ ] Multi-region deployment for global availability
- [ ] Data lake integration with Amazon S3
- [ ] Advanced monitoring with custom CloudWatch metrics


---

