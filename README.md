# notes-api-project
Small Google Keep-style Notes application, with a Python REST API, PostgreSQL database, and frontend.

# Notes API

A simple Google Keep-style notes application.

The project consists of a Python REST API, PostgreSQL
database and a frontend provided by the course.

## Technologies

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy
- Pydantic
- Docker
- Docker Compose

## Architecture

The application has three main services:

1. Frontend: Course reference frontend.
2. Backend: Python FastAPI REST API.
3. Database: PostgreSQL.

The frontend communicates with the API using HTTP.
The API stores and retrieves notes from PostgreSQL.

## Features

- Create notes.
- List all notes.
- Retrieve an individual note.
- Update notes.
- Delete notes.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notes/ | List notes |
| GET | /api/notes/{id} | Get a note |
| POST | /api/notes/ | Create a note |
| PUT | /api/notes/{id} | Update a note |
| DELETE | /api/notes/{id} | Delete a note |
| GET | /health | Health check |

## Run locally

### Requirements

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd notes-api-project