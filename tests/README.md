# Testing Strategy

## Overview

Tests use **timestamp-based isolation** to ensure production safety and test independence. Each test uses specific dates, so tests can run safely against any database without deleting data.

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_ingest.py
pytest tests/test_query.py
```

## Test Isolation Strategy

### Timestamp-Based Isolation
Tests seed data with specific timestamps (e.g., `2024-01-15`) and query using date ranges. This approach:

✅ **Production Safe**: Never deletes existing data  
✅ **Parallel Execution**: Tests don't interfere with each other  
✅ **Realistic**: Mimics real-world query patterns  
✅ **Simple**: No complex database setup required  

### Example
```python
# Test 1: Seeds data for 2024-01-15, queries that date
# Test 2: Seeds data for 2024-01-16, queries that date
# → No conflicts, no cleanup needed
```

## Test Structure

### Ingest Tests (`test_ingest.py`)
- Valid input validation
- Schema validation errors
- Edge cases (negative values, empty strings)

### Query Tests (`test_query.py`)
- Aggregation functions (min, max, avg, sum)
- Single/multiple sensors
- Single/multiple metrics
- Date range filtering
- Empty results handling
- Invalid parameter validation

## Database Configuration

Tests use the application's default database configuration:
- **Local Development**: SQLite (`sensor_data.db`)
- **CI/CD**: Set `DATABASE_URL` environment variable
- **Production**: Tests should never run in production


