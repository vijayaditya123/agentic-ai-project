# Agentic Data Analyst

Ask a business question in plain English and get an answer computed from a real database.

Example: *"Which product categories had the most late deliveries in 2018?"*

The agent is a Claude model on **AWS Bedrock** running in a tool-calling loop written from scratch with `boto3` (no agent framework). It looks at the database schema, writes SQL, runs it safely, optionally analyses the result and draws a chart, then explains the answer.

---

## Features

- Natural-language questions over a PostgreSQL database (Olist Brazilian e-commerce dataset, 8 tables, about 100k orders)
- Hand-written agent loop: the model chooses tools, the code runs them, results go back to the model until it gives a final answer
- Four tools: `get_schema`, `run_sql`, `run_python`, `make_chart`
- Self-correction: SQL errors are sent back to the model so it can fix its own query
- Safety by design: read-only database user, 10-second statement timeout, row limit, step cap
- Session memory for follow-up questions
- Logging of every tool call
- Evaluation set of 30+ questions with expected answers and a score
- FastAPI backend and Streamlit chat UI
- Docker for local development, AWS for deployment

---

## Architecture

```
User (Streamlit chat)
        |
        v
FastAPI  /chat
        |
        v
Agent loop (agent.py)  <------------------+
        |                                  |
        v                                  |
AWS Bedrock (Claude model)                 |
        |  asks for a tool                 |
        v                                  |
Tools (tools.py) ---- result as text ------+
  get_schema | run_sql | run_python | make_chart
        |
        v
PostgreSQL (read-only user)
```

**Loop in plain steps**

1. Send the question, the system prompt and the tool descriptions to the model.
2. If the model asks for a tool, run the matching Python function and send the result back.
3. Repeat until the model returns a final answer, or the step cap is reached.

---

## Tools

| Tool | What it does |
|---|---|
| `get_schema` | Returns every table, column, type, primary key and foreign key as plain text, so the model can write correct JOINs |
| `run_sql` | Runs a SELECT query as the read-only user, with a row limit, and returns the rows as text |
| `run_python` | Runs short calculations on query results in a restricted sandbox |
| `make_chart` | Draws a chart (bar, line) from query results and returns the image |

Every tool returns a string, so the loop can send any result back to the model in the same way.

---

## Database

Dataset: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle).

| Table | Description |
|---|---|
| `customers` | One row per customer |
| `orders` | One row per order, with status and 5 date columns |
| `order_items` | Items in each order (links orders, products, sellers) |
| `order_payments` | Payments per order |
| `order_reviews` | Review scores and comments per order |
| `products` | Product details and category |
| `sellers` | Seller details |
| `product_category_translation` | Portuguese to English category names |

The geolocation file is not loaded.

### Safety

| Measure | Purpose |
|---|---|
| Read-only user `analyst_ro` with `SELECT` only | Generated SQL can never change or delete data |
| `statement_timeout = 10s` | Stops slow or runaway queries |
| Row limit in `run_sql` | Keeps results small |
| Step cap in the agent loop | Prevents endless loops |
| Secrets in `appsettings.json` (git-ignored) | No passwords in code |

---

## Project structure

```
Agentic Ai Project/
├── data/raw/                  Olist CSV files (git-ignored)
├── config.py                  Reads appsettings.json
├── db.py                      Admin engine and read-only engine
├── models.py                  ORM classes for the 8 tables
├── load_data.py               One-time script: CSV to PostgreSQL
├── tools.py                   get_schema, run_sql, run_python, make_chart
├── prompts.py                 System prompt
├── agent.py                   The agent loop (Bedrock + tools)
├── main.py                    FastAPI app
├── streamlit_app.py           Chat UI
├── evals/
│   ├── questions.json         30+ questions with expected answers
│   └── run_evals.py           Scores the agent
├── tests/                     Unit tests
├── docker-compose.yml         Local PostgreSQL
├── appsettings.example.json   Settings template
├── requirements.txt
└── README.md
```

---

## Getting started

### Requirements

- Python 3.12 or newer
- Docker Desktop
- An AWS account with Bedrock model access enabled in your region
- pgAdmin (optional, for browsing the database)

### 1. Set up Python

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure settings

Copy `appsettings.example.json` to `appsettings.json` and fill in your values:

```json
{
  "Database": {
    "Host": "localhost",
    "Port": 5433,
    "Name": "analytics",
    "User": "postgres",
    "Password": "your-password",
    "ReadOnlyUser": "analyst_ro",
    "ReadOnlyPassword": "your-readonly-password"
  },
  "Bedrock": {
    "Region": "your-region",
    "ModelId": "your-model-id"
  }
}
```

Set AWS credentials in the terminal (never commit them):

```
$env:AWS_ACCESS_KEY_ID="your-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret"
```

### 3. Start PostgreSQL

```
docker compose up -d
docker compose ps
```

The port column should show `5433->5432`.

### 4. Create the tables

Create the 8 tables with the SQL script (or Alembic), then check them in pgAdmin.

### 5. Load the data

Download the Olist CSV files into `data/raw/`, then run once:

```
python load_data.py
```

To reload, empty the tables first:

```sql
TRUNCATE order_reviews, order_payments, order_items, orders,
         products, sellers, customers, product_category_translation
RESTART IDENTITY CASCADE;
```

### 6. Create the read-only user

Run in pgAdmin on the `analytics` database:

```sql
CREATE ROLE analyst_ro LOGIN PASSWORD 'your-readonly-password';
GRANT CONNECT ON DATABASE analytics TO analyst_ro;
GRANT USAGE ON SCHEMA public TO analyst_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst_ro;
ALTER ROLE analyst_ro SET statement_timeout = '10s';
```

Check that reading works and deleting is blocked:

```
python -c "from db import engine_read; from sqlalchemy import text; print(engine_read.connect().execute(text('select count(*) from orders')).scalar())"
```

### 7. Run the app

```
uvicorn main:app --reload
streamlit run streamlit_app.py
```

---

## Evaluation

`evals/questions.json` holds 30+ questions, each with the expected answer. `run_evals.py` asks the agent every question, compares the result, and prints a score.

```
python evals/run_evals.py
```

The score is recorded before and after each prompt or schema change, so improvements are measured instead of guessed.

---

## Deployment (AWS)

| Component | AWS service |
|---|---|
| Database | RDS for PostgreSQL |
| App container | ECS, image built with Docker |
| Secrets | Secrets Manager |
| Charts and files | S3 |
| Infrastructure | Terraform |

Only the settings change between local and AWS (host, password, region), and the code stays the same.

---

## Lessons learned

- **Return the schema with foreign keys.** Without `-> table.column` hints the model guessed joins wrongly.
- **Feed errors back.** Sending the database error to the model lets it repair its own SQL.
- **Make safety structural.** A read-only database user is stronger than asking the model not to modify data.
- **Measure before tuning.** The evaluation set shows which prompt changes actually help.

---

## Tech stack

Python, AWS Bedrock (Claude), boto3, PostgreSQL 16, SQLAlchemy, pandas, FastAPI, Streamlit, Docker, pytest, AWS (RDS, ECS, S3, Secrets Manager), Terraform
