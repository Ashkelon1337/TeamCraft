# TeamCraft API

An asynchronous REST API service designed for creating teams and players. The project is built using a layered architecture pattern (Routers -> Services -> Models/Schemas).

## 🛠 Tech Stack

* **Backend:** Python 3.12+ / FastAPI
* **Concurrency:** Asyncio
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (AsyncSession, using optimized selectinload strategies)
* **Migrations:** Alembic
* **Data Validation:** Pydantic
* **Authentication:** JWT, secure password hashing via bcrypt, and session tracking using Cookies
* **Containerization:** Docker / Docker Compose

## 🏗 Project Architecture

The code ensures a strict separation of concerns:

```text
src/
├── auth/            # Security logic, hashing, and JWT token generation
├── models/          # SQLAlchemy declarative models (Players, Teams)
├── routers/         # FastAPI endpoints (Request handling & Dependency Injection)
├── schemas/         # Pydantic schemas for data serialization and validation
├── services/        # Core business logic (db_service for DB operations, auth_service for sessions)
├── config.py        # Application configuration via Pydantic Settings (reads .env)
├── database.py      # Async database engine setup (AsyncEngine)
└── main.py          # Application entry point
```

## Getting Started

### 1. Clone the repository:

git clone https://github.com/Ashkelon1337/TeamCraft.git
cd TeamCraft

### 2. Rename .env.example to .env and enter your details.

### 3. Spin up the containers:

docker-compose up --build

Once up, the system automatically applies Alembic migrations and launches the web server.
Interactive Swagger UI Docs: http://127.0.0.1:8000/docs