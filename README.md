# SCEMAS – Smart City Environmental Monitoring & Alert System (Backend)

SCEMAS (Smart City Environmental Monitoring & Alert System) is a backend service built with Flask to support environmental data monitoring, alert generation, and operational insights for smart city infrastructure.

This repository contains the backend API, which handles:

- Sensor data management
- Alert generation and rules processing
- Account and subscription management
- Operational logging and monitoring

The system integrates with Firebase for authentication and data storage, and exposes RESTful APIs documented via Swagger.

## Prerequisites

Make sure you have the following installed:

- Python (3.9+ recommended)
- pip (Python package manager)
- Virtual environment support (venv)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/BilalM04/SCEMAS-backend
cd SCEMAS-backend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

- Create a `.env` file in the root directory following `.env.example`
- Fill in all Firebase secrets (project ID, private key, client email, etc.)

### 5. Run the application

```bash
python app.py
```

The server will start in development mode.

## Swagger API Documentation

Swagger UI is available for exploring and testing the API.

- Access it at: `http://localhost:5000/api`

The Swagger interface includes:

- Full API documentation
- Endpoint details and request/response schemas
- Authentication instructions (Firebase Bearer tokens)
- Interactive testing of endpoints

All API usage details and examples are available directly within Swagger.
