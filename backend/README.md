# Backend

## Init env

```bash
python3 -m venv env
source env/bin/activate
python install -r requirements.txt
```

## Database migration

Run database container in root folder

```bash
docker compose up db -d
```

```bash
source env/bin/activate # activate virtual environment if not active
alembic upgrade head
```

new migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Start

```bash
source env/bin/activate # activate virtual environment if not active
uvicorn app.main:app --reload --port 8000
```

## Deactivate Virtual Environment

```bash
deactivate
```
