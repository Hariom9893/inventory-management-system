# Inventory Management System

A backend-focused Inventory Management System built using Python, Flask, MySQL, and SQLAlchemy.

## Features

- User registration and login with password hashing
- JWT-based authentication and admin authorization
- Category and product CRUD operations
- Stock-in and stock-out management
- Inventory transaction history
- Product search and filtering
- Category and low-stock filtering
- Pagination
- Dashboard statistics
- Database constraints and input validation
- Automated tests using pytest

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- MySQL
- Flask-JWT-Extended
- Pytest

## Project Structure

```text
inventory-management-system/
├── app.py
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   └── routes/
└── tests/
    └── test_products.py
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Hariom9893/inventory-management-system.git
cd inventory-management-system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure your MySQL database credentials and JWT secret.

Never commit your actual `.env` file or secrets to GitHub.

### 5. Create the database

Create a MySQL database named `inventory_db`, then configure the database connection in `.env`.

### 6. Run the application

```bash
python app.py
```

The development server should be available at:

`http://127.0.0.1:5000`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/register` | Register a user |
| POST | `/login` | Log in and obtain a JWT |
| GET | `/me` | Get the authenticated user's details |
| POST | `/categories` | Create a category |
| GET | `/categories` | List categories |
| GET | `/categories/<id>` | Get a category |
| PUT | `/categories/<id>` | Update a category |
| DELETE | `/categories/<id>` | Delete a category |
| POST | `/products` | Create a product |
| GET | `/products` | Search, filter and paginate products |
| GET | `/products/<id>` | Get a product |
| PUT | `/products/<id>` | Update a product |
| DELETE | `/products/<id>` | Delete a product when history permits |
| POST | `/products/<id>/stock-in` | Add stock |
| POST | `/products/<id>/stock-out` | Issue stock |
| GET | `/products/low-stock` | Get low-stock products |
| GET | `/inventory/transactions` | View inventory transaction history |
| GET | `/dashboard` | Get dashboard statistics |

Protected endpoints require a JWT access token in the request header:

```text
Authorization: Bearer <access_token>
```

## Query Examples

```text
GET /products?search=laptop
GET /products?category_id=1
GET /products?low_stock=true
GET /products?page=1&per_page=10
GET /inventory/transactions?type=IN
GET /inventory/transactions?product_id=1
```

## Running Tests

```bash
python -m pytest -v
```

## Security Notes

- Passwords are stored as hashes.
- JWT authentication protects private endpoints.
- Admin-only operations use role authorization.
- Input validation and database constraints help protect inventory data.
- Stock changes and transaction records are committed together.

## Future Improvements

- Frontend dashboard
- Database migrations
- More comprehensive automated tests
- Deployment and production configuration
