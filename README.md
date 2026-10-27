# Newspaper Distribution System

A full-stack Python application for managing newspaper delivery agents, customer subscriptions, and monthly billing.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Workspace Setup](#3-workspace-setup)
4. [Environment Configuration](#4-environment-configuration)
5. [Database Setup](#5-database-setup)
6. [Install Dependencies](#6-install-dependencies)
7. [Initialise the Database](#7-initialise-the-database)
8. [Launch the Application](#8-launch-the-application)
9. [Login Credentials](#9-login-credentials)
10. [Application Modules](#10-application-modules)
    - [Login](#101-login)
    - [Customer Bills](#102-customer-bills)
    - [Purchase Orders](#103-purchase-orders)
    - [Publications](#104-publications)
    - [Customers](#105-customers)
11. [Navigation Guide](#11-navigation-guide)
12. [API Reference](#12-api-reference)
13. [Running Tests](#13-running-tests)
14. [Project Structure](#14-project-structure)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Architecture Overview

| Layer | Technology | Port |
|---|---|---|
| Frontend UI | Python · Streamlit 1.58 | 8501 |
| Backend API | Python · FastAPI 0.136 · Uvicorn 0.48 | 8000 |
| Database | PostgreSQL 14+ · SQLAlchemy 2.0 · asyncpg | 5432 |
| Auth | JWT (python-jose 3.5) · bcrypt 5.0 | — |
| ORM / Migrations | SQLAlchemy 2.0 declarative · Alembic 1.18 | — |

The frontend communicates with the backend exclusively through HTTP REST calls (`httpx`).  
The backend exposes a fully documented OpenAPI interface at `http://localhost:8000/docs`.

---

## 2. Prerequisites

Install the following software **before** setting up the project.

### 2.1 Python 3.11 or later

**Windows**

1. Download the installer from <https://www.python.org/downloads/>.
2. Run the installer — tick **"Add Python to PATH"** on the first screen.
3. Verify:

```powershell
python --version
# Expected: Python 3.11.x or higher
```

**macOS / Linux**

```bash
# macOS (Homebrew)
brew install python@3.11

# Ubuntu / Debian
sudo apt update && sudo apt install python3.11 python3.11-venv python3-pip
```

---

### 2.2 PostgreSQL 14 or later

**Windows**

1. Download the installer from <https://www.postgresql.org/download/windows/>.
2. Run the installer. When prompted:
   - Set a **superuser password** (e.g. `postgres`) — you will need this later.
   - Leave the default port **5432** unless it conflicts.
3. Ensure `pg_ctl` / `psql` are on your PATH (the installer offers this option).
4. Verify:

```powershell
psql --version
# Expected: psql (PostgreSQL) 14.x or higher
```

**macOS**

```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu / Debian**

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### 2.3 Git (optional — for cloning the repository)

Download from <https://git-scm.com/downloads> or install via your package manager.

---

## 3. Workspace Setup

### 3.1 Obtain the project files

```powershell
# Option A — Clone via Git
git clone <repository-url> C:\stage\publ
cd C:\stage\publ

# Option B — If you already have the files
cd C:\stage\publ
```

### 3.2 Create a Python virtual environment

Using a virtual environment keeps the project's dependencies isolated from your system Python.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note:** If you see an error about execution policy, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> then activate again.

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Your prompt will change to show `(.venv)` when the environment is active.

---

## 4. Environment Configuration

Copy the example environment file and fill in your PostgreSQL credentials:

**Windows**

```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS / Linux**

```bash
cp .env.example .env
nano .env   # or: code .env
```

Edit the following values in `.env`:

```dotenv
# ── Application ────────────────────────────────────
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=change-me-in-production-use-a-long-random-string

# ── PostgreSQL ─────────────────────────────────────
# Format: postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/newsdb

# ── Frontend ───────────────────────────────────────
FRONTEND_PORT=8501
BACKEND_URL=http://localhost:8000
```

| Variable | Description |
|---|---|
| `DATABASE_URL` | Full async PostgreSQL connection string. Replace `postgres:postgres` with your PostgreSQL username and password. Replace `newsdb` with the database name you want the app to use (it will be created automatically). |
| `SECRET_KEY` | Used to sign JWT tokens. Change this to a long random string before deploying. |
| `APP_PORT` | Backend API port (default 8000). |
| `FRONTEND_PORT` | Streamlit UI port (default 8501). |

---

## 5. Database Setup

The application creates its own database automatically. You only need to ensure PostgreSQL is running and the credentials in `.env` are correct.

### 5.1 Confirm PostgreSQL is running

**Windows**

```powershell
# Check service status
Get-Service postgresql*

# Start if stopped
Start-Service postgresql-x64-14   # adjust version suffix as needed
```

**macOS**

```bash
brew services list | grep postgresql
brew services start postgresql@14
```

**Ubuntu**

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### 5.2 Verify your credentials

```powershell
# Replace 'postgres' with your PostgreSQL username if different
psql -U postgres -c "\l"
```

Enter the password when prompted. If the connection succeeds you will see a list of databases.

---

## 6. Install Dependencies

With the virtual environment **active**:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all runtime and development packages:

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.136 | REST API framework |
| `uvicorn[standard]` | 0.48 | ASGI server |
| `sqlalchemy` | 2.0 | Async ORM |
| `alembic` | 1.18 | Database migrations |
| `asyncpg` | 0.31 | Async PostgreSQL driver |
| `pydantic` | 2.9 | Request / response validation |
| `pydantic-settings` | 2.x | `.env` configuration loading |
| `python-jose[cryptography]` | 3.5 | JWT token signing & verification |
| `bcrypt` | 5.0 | Password hashing |
| `httpx` | 0.27 | HTTP client (frontend → backend) |
| `streamlit` | 1.58 | Web UI framework |
| `pandas` | 3.0 | Data tables in the UI |
| `python-multipart` | 0.0.x | Form data parsing |

Verify the install:

```powershell
pip list | Select-String "fastapi|streamlit|sqlalchemy"
```

---

## 7. Initialise the Database

```powershell
python scripts/init_db.py
```

This script:

1. Connects to your PostgreSQL server.
2. Creates the `newsdb` database if it does not exist.
3. Creates all tables (`users`, `publications`, `customers`, `purchase_orders`, `bill_items`, `bills`).
4. Removes any stale duplicate rows (if the script has been run before).
5. Seeds the default **admin** user if no users exist yet.

Expected output:

```
=== Newspaper Distribution System — DB Init ===
  Database 'newsdb' already exists.
  Duplicate bill rows removed (if any).
  All tables created / verified.
  Seeded default admin user  (username: admin / password: admin123)
  IMPORTANT: Change the admin password after first login.
=== Init complete ===
```

---

## 8. Launch the Application

```powershell
python start.py
```

The launcher:

1. Runs `scripts/init_db.py` automatically (safe to re-run).
2. Starts the **backend API** on `http://localhost:8000`.
3. Waits 3 seconds for the backend to be ready.
4. Starts the **Streamlit frontend** on `http://localhost:8501`.

Expected console output:

```
========================================================
  Newspaper Distribution System
========================================================

[1/3] Initialising database…
  ...

[2/3] Starting backend API on http://localhost:8000 …
[3/3] Starting frontend UI on http://localhost:8501 …

========================================================
  Application is running!
  Frontend : http://localhost:8501
  API      : http://localhost:8000
  API Docs : http://localhost:8000/docs
  Login    : admin / admin123  (change after first login)
  Press Ctrl+C to stop all services.
========================================================
```

Open your browser and navigate to **`http://localhost:8501`**.

Press **`Ctrl + C`** in the terminal to stop both services.

---

## 9. Login Credentials

| Field | Value |
|---|---|
| **Username** | `admin` |
| **Password** | `admin123` |

> **Security notice:** These are the default seeded credentials.  
> Change the password immediately after first login by asking your system administrator to update the admin user record via the backend API or by modifying it directly in the database.

---

## 10. Application Modules

### 10.1 Login

**URL:** `http://localhost:8501`

The login screen is the application entry point. Users must authenticate before accessing any module.

**Fields**

| Field | Description |
|---|---|
| Username | Your assigned application username |
| Password | Your password (masked) |

**Behaviour**

- Empty fields are rejected with an inline error message before any network call is made.
- Invalid credentials show an "Invalid username or password" error.
- On success the user is redirected to the **Customer Bills** dashboard.
- The **Sign Out** button in the sidebar ends the session and returns to the login screen.

---

### 10.2 Customer Bills

**Navigation label:** 🧾 Customer Bills

This is the home dashboard after login. It allows you to search for bills, view itemised bill details, and generate new bills from purchase orders.

#### Search

Two search modes are available via a radio selector:

**Mode A — Search by Customer**

| Control | Description |
|---|---|
| Type-to-filter box | Start typing a customer name; the dropdown below updates in real time to show matching names only. |
| Customer dropdown | Select the specific customer from the filtered list. |
| Month (optional) | Filter results to a specific month. Choose "All" to include all months. |
| Year (optional) | Filter results to a specific year. Choose "All" to include all years. |

Click **🔍 Search** to fetch results. At least one of Customer, Month, or Year must be specified.

**Mode B — Search by Month & Year**

| Control | Description |
|---|---|
| Month | Select a calendar month (January – December). Required. |
| Year | Select a year from the dropdown. Required. |

Searches all customers for bills in the selected period.

#### Search Results

If no bills match, the message **"No bills found for selected range"** is displayed.

If bills are found, a list appears with the following columns:

| Column | Description |
|---|---|
| Billing Month | The month and year the bill covers (e.g. January 2024) |
| Customer | Name of the customer |
| Total Amount | Consolidated bill total in ₹ |
| Details | **View →** link |

Click **View →** on any row to open the **Bill Details** popup.

#### Bill Details Popup

Displays all line items that make up the selected bill:

| Column | Description |
|---|---|
| Publication | Name of the newspaper / magazine |
| Qty | Number of issues delivered in the billing month |
| Unit Price (₹) | Sale price per issue |
| Discount (%) | Discount applied to this line |
| Amount (₹) | Line total after discount |

The **Net Amount Payable** metric at the bottom shows the bill total.  
Click **✕ Close** to dismiss the popup.

#### Generate Bills

Click the **📄 Generate Bills** button (top-right of the page) to open the generation popup.

| Control | Description |
|---|---|
| Month | Month to generate bills for |
| Year | Year to generate bills for |
| Generate For | "All Customers" or a specific customer |

Click **Generate Now**. The system:

1. Finds all active purchase orders (subscriptions) up to the end of the selected month.
2. Calculates the number of deliveries based on each publication's frequency.
3. Creates or updates Bill Items grouped by customer and publication.
4. Creates or updates consolidated Bills per customer.

The operation is **idempotent** — running it again for the same period updates existing records rather than creating duplicates.

After generation a summary is shown:
- Bills Created / Updated
- Bill Items Created / Updated

Click **✕ Clear** to reset the search and start a new query.

---

### 10.3 Purchase Orders

**Navigation label:** 📋 Purchase Orders

A purchase order represents a customer's **subscription** to a publication. The billing engine uses these records to calculate how many issues were delivered in each billing month.

#### Search

Type any text in the **🔍 Search orders** field to filter the list in real time by:
- Customer name
- Publication name
- Purchase date (format `YYYY-MM-DD`)

The table shows all matching orders with columns: ID, Date, Customer, Publication, Sale Price, Discount.

#### Add New Order (➕ Tab)

| Field | Description | Default |
|---|---|---|
| Customer | Select from all registered customers | — |
| Publication | Select from all publications | — |
| Purchase Date | Date the subscription was created | Today |
| Sale Price (₹) | Price charged to the customer | Publication's base price |
| Discount (%) | Percentage discount applied to each bill | 0.00 |

Click **Add Order** to save. The sale price defaults to the selected publication's base price automatically when the publication is chosen.

#### Edit Order (✏️ Tab)

1. Enter the **Order ID** (visible in the ID column of the table).
2. Click **Load Order** to populate the form.
3. Modify Purchase Date, Sale Price, or Discount.
4. Click **Save Changes**.

#### Delete Order (🗑️ Tab)

1. Enter the **Order ID**.
2. A confirmation warning shows the order details.
3. Click **Confirm Delete** to permanently remove the order.

> **Note:** Deleting an order does not automatically remove previously generated bill items for that order.

---

### 10.4 Publications

**Navigation label:** 📰 Publications

Publications are the newspapers and magazines that customers subscribe to. Each publication has a delivery frequency that determines how many issues are counted per billing month.

#### Search

Type in the **🔍 Search publications** field to filter by name or frequency (e.g. type `daily` to show all daily titles).

The table shows: ID, Name, Frequency, Base Price, Purchase Price.

#### Frequency Values

| Value | Meaning | Issues per Month |
|---|---|---|
| `daily` | One issue every day | Days in the month |
| `weekly` | One issue per week | ≈ 4 |
| `monthly` | One issue per month | 1 |
| `quarterly` | One issue per quarter | 1 (Jan, Apr, Jul, Oct only) |
| `bi_annual` | Twice per year | 1 (Jan, Jul only) |
| `annual` | Once per year | 1 (January only) |

#### Add New Publication (➕ Tab)

| Field | Description |
|---|---|
| Publication Name | Display name of the title |
| Frequency | Delivery frequency (see table above) |
| Base Price (₹) | Price charged to the customer (default sale price) |
| Purchase Price (₹) | Your cost price from the distributor |

Click **Add Publication** to save.

#### Edit Publication (✏️ Tab)

1. Enter the **Publication ID**.
2. Click **Load Publication**.
3. Edit any field.
4. Click **Save Changes**.

#### Delete Publication (🗑️ Tab)

1. Enter the **Publication ID**.
2. Confirm the warning.
3. Click **Confirm Delete**.

> **Warning:** Deleting a publication that has active purchase orders will leave those orders referencing a non-existent publication. Remove associated purchase orders first.

---

### 10.5 Customers

**Navigation label:** 👥 Customers

Customers are the individuals or households that receive newspaper deliveries.

#### Search

Type in the **🔍 Search customers** field to filter by:
- Customer name
- PIN code
- Contact number
- Address

The table shows: ID, Name, Address, PIN, Contact.

#### Add New Customer (➕ Tab)

| Field | Description |
|---|---|
| Customer Name | Full name of the customer |
| Contact Number | Mobile or landline number |
| PIN Code | Postal / delivery area PIN |
| Address | Full delivery address |

Click **Add Customer** to save.

#### Edit Customer (✏️ Tab)

1. Enter the **Customer ID**.
2. Click **Load Customer**.
3. Edit any field.
4. Click **Save Changes**.

#### Delete Customer (🗑️ Tab)

1. Enter the **Customer ID**.
2. A warning describes the impact.
3. Click **Confirm Delete**.

> **Warning:** Deleting a customer does not cascade to their purchase orders or bills. Remove associated records first to keep data consistent.

---

## 11. Navigation Guide

```
┌─────────────────────────────┐
│  📰  News Distribution      │
│      Management System      │
├─────────────────────────────┤
│                             │
│  🧾  Customer Bills         │ ← Search & view monthly bills,
│                             │   bill item details, generate bills
│  📋  Purchase Orders        │ ← Manage customer subscriptions
│                             │
│  📰  Publications           │ ← Manage publication catalogue
│                             │
│  👥  Customers              │ ← Manage customer records
│                             │
├─────────────────────────────┤
│  Signed in as admin         │
│  [ Sign Out ]               │
└─────────────────────────────┘
```

**Typical workflow for billing:**

```
1. Add Publications         →  Publications tab
2. Add Customers            →  Customers tab
3. Create Subscriptions     →  Purchase Orders tab
4. Generate Bills           →  Customer Bills → 📄 Generate Bills
5. View / Print Bills       →  Customer Bills → Search → View →
```

---

## 12. API Reference

The backend exposes a full OpenAPI (Swagger) interface.

| URL | Description |
|---|---|
| `http://localhost:8000/docs` | Swagger UI — interactive API browser |
| `http://localhost:8000/redoc` | ReDoc — printable API documentation |

### Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Obtain a JWT bearer token |
| `GET` | `/users/` | List all users |
| `POST` | `/users/` | Create a user |
| `PUT` | `/users/{id}` | Update a user |
| `DELETE` | `/users/{id}` | Delete a user |
| `GET` | `/publications/` | List publications |
| `POST` | `/publications/` | Create a publication |
| `PUT` | `/publications/{id}` | Update a publication |
| `DELETE` | `/publications/{id}` | Delete a publication |
| `GET` | `/customers/` | List customers |
| `POST` | `/customers/` | Create a customer |
| `PUT` | `/customers/{id}` | Update a customer |
| `DELETE` | `/customers/{id}` | Delete a customer |
| `GET` | `/purchase-orders/` | List purchase orders |
| `POST` | `/purchase-orders/` | Create a purchase order |
| `PUT` | `/purchase-orders/{id}` | Update a purchase order |
| `DELETE` | `/purchase-orders/{id}` | Delete a purchase order |
| `GET` | `/bill-items/` | List bill items (filter by customer, month) |
| `GET` | `/bills/` | List bills (filter by customer) |
| `POST` | `/bills/generate` | Generate bills from purchase orders |

All endpoints except `/auth/login` require an `Authorization: Bearer <token>` header.

---

## 13. Running Tests

The test suite uses **pytest** with an in-memory SQLite database — no PostgreSQL connection is needed to run tests.

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run all tests with coverage
python -m pytest tests/backend/ -v --tb=short --cov=src --cov-report=term-missing
```

Expected output: **22 tests passed**.

| Test file | What it covers |
|---|---|
| `test_auth.py` | Login success, wrong password, unknown user, unauthenticated access |
| `test_users.py` | Create, list, duplicate username, update, delete |
| `test_publications.py` | Full CRUD cycle |
| `test_customers.py` | Full CRUD cycle |
| `test_purchase_orders.py` | Create with default price, custom price, list |
| `test_bill_generation.py` | Generate, idempotency, per-customer filter |

---

## 14. Project Structure

```
c:\stage\publ\
├── start.py                    ← Single-command launcher
├── .env                        ← Local environment variables (not committed)
├── .env.example                ← Template — copy to .env
├── pyproject.toml              ← Build config, linting, pytest settings
├── requirements.txt            ← Runtime dependencies
├── requirements-dev.txt        ← Dev / test dependencies
├── Makefile                    ← make dev / test / lint shortcuts
│
├── src/
│   ├── backend/
│   │   ├── main.py             ← FastAPI application factory
│   │   ├── api/routes/         ← One router per module
│   │   ├── core/
│   │   │   ├── config.py       ← pydantic-settings (.env loader)
│   │   │   ├── security.py     ← JWT + bcrypt helpers
│   │   │   └── deps.py         ← FastAPI dependency injection
│   │   ├── db/
│   │   │   ├── models/         ← SQLAlchemy declarative models
│   │   │   ├── migrations/     ← Alembic migration scripts
│   │   │   └── session.py      ← Async engine + session factory
│   │   ├── schemas/            ← Pydantic request/response models
│   │   └── services/           ← Business logic (no code in routes)
│   │
│   └── frontend/
│       ├── main.py             ← Streamlit entry point + routing
│       ├── assets/style.css    ← Formal business CSS theme
│       ├── _pages/             ← Page modules (_pages/ ignored by Streamlit auto-nav)
│       │   ├── login.py
│       │   ├── customer_bills.py
│       │   ├── purchase_orders.py
│       │   ├── publications.py
│       │   └── customers.py
│       ├── components/
│       │   └── navbar.py       ← Left sidebar navigation
│       └── utils/
│           ├── api_client.py   ← httpx wrappers (GET/POST/PUT/DELETE)
│           └── auth.py         ← Login / logout / auth check
│
├── tests/
│   └── backend/
│       ├── conftest.py         ← SQLite in-memory fixtures
│       └── test_*.py
│
├── config/
│   ├── alembic.ini
│   ├── development.yaml
│   ├── production.yaml
│   └── testing.yaml
│
├── scripts/
│   ├── init_db.py              ← Create tables + seed admin user
│   └── setup.ps1               ← One-shot venv + install script
│
└── .sessions/
    ├── checkpoints/            ← Live session state (*.rd.json)
    ├── snapshots/              ← Immutable session archives (*.rd.json)
    └── .rd_manifest.json       ← Session schema documentation
```

---

## 15. Troubleshooting

### "Could not connect to PostgreSQL"

- Verify PostgreSQL is running (see [Section 5.1](#51-confirm-postgresql-is-running)).
- Check the `DATABASE_URL` in `.env` — username, password, host, and port must be correct.
- Test with: `psql -U postgres -h localhost -p 5432`

### "Module not found" on startup

- Ensure the virtual environment is **activated** before running `python start.py`.
- Run `pip install -r requirements.txt` again.

### "Address already in use" (port 8000 or 8501)

Another process is using the port. Find and stop it:

```powershell
# Windows — find the process using port 8000
netstat -ano | findstr :8000
# Note the PID in the last column, then:
Stop-Process -Id <PID> -Force
```

Or change `APP_PORT` / `FRONTEND_PORT` in `.env` and update `start.py` accordingly.

### Streamlit shows a blank page after login

- Confirm the backend is reachable: open `http://localhost:8000/docs` in a browser.
- Check the terminal running `start.py` for backend error messages.

### "MultipleResultsFound" on bill generation

- Run `python scripts/init_db.py` — it removes stale duplicate rows and applies unique constraints.
- Then retry bill generation.

### Tests fail with "connection refused"

Tests use an in-memory SQLite database and do **not** require PostgreSQL. If they fail, ensure:
- All packages are installed: `pip install -r requirements-dev.txt`
- `PYTHONPATH` is set: `$env:PYTHONPATH = "src"` (PowerShell) or `export PYTHONPATH=src` (bash)

---

## Quick-Start Cheatsheet

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Configure database URL
Copy-Item .env.example .env   # then edit DATABASE_URL

# 4. Launch everything
python start.py

# ─── Separate terminal ───────────────────────────
# Run tests
$env:PYTHONPATH = "src"
python -m pytest tests/backend/ -v
```

**Application URLs after launch:**

| Service | URL |
|---|---|
| Frontend UI | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

**Default credentials:** `admin` / `admin123`

---

*Newspaper Distribution System — version 0.3.0*
