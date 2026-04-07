# Orders REST API Service

[![CI](https://github.com/CSCI-GA-2820-SP26-001/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-001/orders/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-001/orders/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP26-001/orders)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is the Orders microservice for the NYU DevOps class project. It provides a RESTful API to manage Orders and their associated Items, backed by a PostgreSQL database.

## Overview

The Orders service allows you to Create, Read, Update, and Delete (CRUD) Orders and Items within those Orders. All endpoints accept and return **JSON** data exclusively.

## Database Structure

The service uses two database tables with a one-to-many relationship:

```
┌─────────────────────────────┐       ┌─────────────────────────────┐
│           Order             │       │           Item               │
├─────────────────────────────┤       ├─────────────────────────────┤
│ id        INTEGER    (PK)    │───┐   │ id        INTEGER    (PK)    │
│ name      VARCHAR(63)        │   │   │ order_id  INTEGER    (FK)    │
│ address   VARCHAR(256)       │   └──>│ name      VARCHAR(63)        │
│ email     VARCHAR(256)       │       │ quantity  INTEGER             │
│ status    VARCHAR(64)        │       │ price     FLOAT               │
│           [default:          │       └─────────────────────────────┘
│           "Unprocessed"]     │
└─────────────────────────────┘
```

- **One Order** has **many Items** (one-to-many relationship)
- Deleting an Order **cascades** to delete all its Items automatically
- Item `quantity` must be a positive integer and `price` must be a positive number

## API Endpoints

All endpoints return JSON responses. Write operations (`POST`, `PUT`) require `Content-Type: application/json`.

### Order Endpoints

| Method   | URL                  | Description           | Request Body                              | Success Response |
|----------|----------------------|-----------------------|-------------------------------------------|------------------|
| `GET`    | `/`                  | Service info          | None                                      | `200 OK`         |
| `GET`    | `/orders`            | List all orders       | None                                      | `200 OK`         |
| `POST`   | `/orders`            | Create a new order    | `{name, address, email, items?}`          | `201 Created`    |
| `GET`    | `/orders/{id}`       | Read a single order   | None                                      | `200 OK`         |
| `PUT`    | `/orders/{id}`       | Update an order       | `{name, address, email}`                  | `200 OK`         |
| `DELETE` | `/orders/{id}`       | Delete an order       | None                                      | `204 No Content` |

### Item Endpoints

| Method   | URL                                  | Description         | Request Body                    | Success Response |
|----------|--------------------------------------|---------------------|---------------------------------|------------------|
| `GET`    | `/orders/{id}/items/{item_id}`       | Read an item        | None                            | `200 OK`         |
| `PUT`    | `/orders/{id}/items/{item_id}`       | Update an item      | `{name, quantity, price}`       | `200 OK`         |
| `DELETE` | `/orders/{id}/items/{item_id}`       | Delete an item      | None                            | `200 OK`         |

> **Note:** Delete item only works when the order status is `Pending` or `Unprocessed`. Otherwise it returns `409 Conflict`.

### Request / Response Examples

**Create an Order:**

```bash
POST /orders
Content-Type: application/json

{
  "name": "Alice Johnson",
  "address": "100 Broadway, New York, NY 10001",
  "email": "alice@nyu.edu",
  "items": [
    {"name": "Laptop", "quantity": 1, "price": 999.99},
    {"name": "Mouse", "quantity": 2, "price": 29.99}
  ]
}
```

Response (`201 Created`):

```json
{
  "id": 1,
  "name": "Alice Johnson",
  "address": "100 Broadway, New York, NY 10001",
  "email": "alice@nyu.edu",
  "status": "Unprocessed",
  "items": [
    {"id": 1, "order_id": 1, "name": "Laptop", "quantity": 1, "price": 999.99},
    {"id": 2, "order_id": 1, "name": "Mouse", "quantity": 2, "price": 29.99}
  ]
}
```

**Error Response** (`404 Not Found`):

```json
{
  "status": 404,
  "error": "Not Found",
  "message": "order with id '999' was not found."
}
```

### Error Codes

| Code  | Meaning                    | When                                           |
|-------|----------------------------|-------------------------------------------------|
| `400` | Bad Request                | Missing required fields or invalid data          |
| `404` | Not Found                  | Order or Item does not exist                     |
| `405` | Method Not Allowed         | HTTP method not supported on the endpoint        |
| `409` | Conflict                   | Deleting item from a non-Pending/Unprocessed order |
| `415` | Unsupported Media Type     | Missing or wrong `Content-Type` header           |

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- Dev Container (recommended) or local environment

### Running the Service

```bash
# Install dependencies
make install

# Start the service (uses honcho/Procfile)
make run
```

The service will be available at `http://localhost:8080`.

### Running Tests

```bash
make test
```

This runs the full test suite with `pytest` and enforces a minimum **95% code coverage** threshold.

### Linting

```bash
make lint
```

Runs `flake8` and `pylint` against the `service/` and `tests/` directories.

## Project Structure

```text
service/                   - service python package
├── __init__.py            - package initializer (app factory)
├── config.py              - configuration parameters
├── models.py              - Order and Item data models
├── routes.py              - REST API route handlers
└── common                 - common code package
    ├── cli_commands.py    - Flask CLI command to recreate tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - test factories for Order and Item
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for data models
└── test_routes.py         - test suite for REST API routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
