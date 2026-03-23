# DevCats Marketplace Backend

High-performance asynchronous backend for the DevCats Marketplace, built with FastAPI and SQLAlchemy.

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous)
- **Database**: PostgreSQL with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async engine)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Storage**: MinIO/S3 compatible storage via [aioboto3](https://github.com/terryclyne/aioboto3)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Image Processing**: [Pillow](https://python-pillow.org/) (Processed in ThreadPool to avoid blocking)

## Architecture

The backend follows a layered architecture to ensure maintainability and testability:

1.  **API Layer (`app/api/`)**: Router definitions, dependency injection, and request/response handling.
2.  **Service Layer (`app/services/`)**: Business logic, database interactions using SQLAlchemy.
3.  **Schema Layer (`app/schemas/`)**: Pydantic models for data validation and serialization.
4.  **Model Layer (`app/models/`)**: SQLAlchemy ORM models.
5.  **Core (`app/core/`)**: Configuration, security, and exception handling.

## Key Features

- **Asynchronous S3 Integration**: File uploads to MinIO are fully non-blocking.
- **Efficient Querying**: Utilizes `selectinload` for relationship loading to avoid N+1 issues and SQL-side aggregations for performance.
- **Cursor-based Pagination**: Optimized for infinite scrolling on the frontend.
- **Admin Auth**: JWT-based authentication for administrative operations.

## Local Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure environment**:
    Copy `.env.example` to `.env` and fill in the details.
3.  **Run Migrations**:
    ```bash
    alembic upgrade head
    ```
4.  **Seed Database (Optional)**:
    ```bash
    python -m app.db.seed
    ```
5.  **Start Dev Server**:
    ```bash
    uvicorn main:app --reload
    ```

## Testing

Smoke tests are available in the `tests/` directory:
```bash
pytest
```
