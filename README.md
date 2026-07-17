# FastAPI CRUD

A minimal, well-structured CRUD REST API for managing **users**, built with
FastAPI, SQLAlchemy, and Pydantic — with a full pytest suite.

## Project structure

```
testing/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app + startup
│   ├── database.py        # Engine, SessionLocal, Base
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # DB operations (create/read/update/delete)
│   ├── dependencies.py    # get_db dependency
│   └── routers/
│       └── users.py       # /users endpoints
├── tests/
│   ├── conftest.py        # Fixtures (in-memory DB + TestClient)
│   ├── test_create_user.py
│   ├── test_get_users.py
│   ├── test_get_user.py
│   ├── test_update_user.py   # PUT (full replace)
│   ├── test_patch_user.py    # PATCH (partial update)
│   └── test_delete_user.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

uv init
uv venv
.venv\Scripts\activate
uv add requirements.txt

uvicorn app.main:app --reload --reload-dir app









Got it — here's the order you build the **code**, file by file, and why each comes before the next.

## Build order

**1. `database.py` — set up the engine & session first**
Everything depends on the DB connection. You create `engine`, `SessionLocal` (session factory), and `Base` (the parent class all models inherit from).
```python
engine = create_engine(SQLALCHEMY_DATABASE_URL, ...)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

**2. `models.py` — define the database table**
Uses `Base` from step 1. This is the actual `users` table (columns: id, name, email, age, is_active).
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True) ...
```

**3. `schemas.py` — define the request/response shapes**
Pydantic models that validate incoming JSON and shape outgoing JSON. Independent of the DB — this is the API's data contract (`UserCreate`, `UserUpdate`, `UserOut`).

**4. `crud.py` — write the database operations**
Now that you have `models` (step 2) and `schemas` (step 3), you write the functions that actually talk to the DB: `create_user`, `get_user`, `update_user`, `delete_user`.

**5. `dependencies.py` — the `get_db` helper**
A small function that hands a DB session to each request and closes it after. Uses `SessionLocal` from step 1.

**6. `routers/users.py` — define the endpoints**
This ties it all together: URL paths (`POST /users/`, `GET /users/{id}`, …) that call `crud` functions (step 4), validate with `schemas` (step 3), and get their session via `get_db` (step 5).

**7. `main.py` — create the app and plug in the router**
The entry point. Creates the `FastAPI()` app, creates the tables (`Base.metadata.create_all`), and includes the router from step 6.
```python
app = FastAPI()
app.include_router(users.router)
```

**8. `tests/` — write tests last**
Once the app runs, you write `conftest.py` (test DB + client fixtures) and one test file per operation.

## The dependency chain (why this order)
```
database.py  →  models.py  ┐
             →  schemas.py ┼→  crud.py  →  routers/users.py  →  main.py  →  tests
             →  dependencies.py ┘
```
Each file only imports things built **before** it — so building bottom-up (data layer → logic layer → API layer) means nothing is ever missing when you write the next file.