# Backend

## Global architecture

```
backend/
├── api/            # Application entry point and API configuration
├── routes/         # HTTP route definitions
├── services/       # Functions used by Application services (balances, settlements...)
├── models/         # Data models
├── utils/          # Shared utilities
├── extensions.py   # Initializes and exposes shared Flask extensions
├── Dockerfile.dev  # Development container configuration
├── Dockerfile.prod # Production container configuration
└── README.md       # Documentation
```

## Models

The `models/` folder defines the data structures for the application.

```
models/
├── __init__.py
├── auth_user.py    # Users informations and credentials
├── currency.py     # Currency types
├── expense.py      # Core data for transactions
├── tricount.py     # Structure containing all informations about the projects
└── user.py         # Participants informations
```

## Routes

The `routes/` folder defines the entry points and handles HTTP requests.

```
routes/
├── __init__.py
├── auth.py         # Endpoints for authentification tasks
└── tricounts.py    # Endpoints for managing groups, expenses, and members
```

## Services

The `services/` folder contains functions handling the business logic and performing calculations.

```
services/
├── __init__.py
├── balance.py      # Calculates the net total for each user in a group
├── export.py       # Generates an Excel file containing all of the project informations
└── settlement.py   # The algorithm used to resolve debts and minimize transfers
```
