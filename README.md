# POC Weather Sensor Metrics API

A proof-of-concept REST API for ingesting and querying weather sensor metrics such as temperature, humidity, wind speed, etc.

## 🧠 Overview

The application provides:
- An API to ingest weather sensor metrics
- An API to query aggregated metrics (min, max, sum, average)
- Persistent storage using a relational database
- Input validation and error handling
- A clean, modular Python codebase

The solution is intentionally kept simple, with optional components added to demonstrate how it could be productionized in a cloud-native environment.

## 🚀 Features

- REST API built with **FastAPI**
- Input validation using **Pydantic**
- Data persistence using **SQLAlchemy ORM**
- Statistical aggregation using database-level queries
- Supports:
  - Multiple sensors or all sensors
  - Multiple metrics
  - min / max / sum / average
  - Date ranges between 1 day and 1 month
- SQLite by default (local setup)
- Switchable to PostgreSQL via environment variables
