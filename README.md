# Infrastructures et Systèmes Logiciels 2025 Project: 3Comptes

This collaborative student project is aiming to rebuild the core features of Tricount from scratch. The goal is to design a clean, intuitive system that allows users to split expenses, track balances, and settle debts seamlessly within a group.

The frontend of this application was developed with the guidance and advices of a real frontend developer, working in the same company as one of the group members.

## Run the Application

**ℹ️ Important**
Docker Engine must be installed and running for the application to work.

### `.env` File

You need an `.env` file looking like
```
JWT_SECRET_KEY=xxx
```

### First Time Setup

To build the images and start the application for the first time:

```bash
docker compose -f docker-compose.prod.yaml up --build
```

This will:
- Build the backend and frontend images
- Start the backend service with the tricount data as a persistent volume
- Start the frontend service that depends on the backend one

### Future Use

Once the images have been built, you can start the application with:

```bash
docker compose -f docker-compose.prod.yaml up
```

### Accessing the Application

The application will be running at http://localhost:5173

### Stopping the Application

To stop and remove all running containers:

```bash
docker compose -f docker-compose.prod.yaml down
```

## User Guide

The application provides a centralized platform for managing group expenses and simplifying financial settlements between participants.

### Project Management

- Users can create new projects to track shared expenses. The user creating a project is referenced to as the owner of the project.

- Existing projects can be joined using a unique project identifier, allowing multiple users to collaborate within the same group.

- Each project maintains its own list of participants and expenses.

- Only the owner of the project can delete it.

### Participant Management

- Users can add or invite participants to a project.

- Only the owner of the project can delete participants.

### Expense Tracking

- Expenses can be logged with a description, amount, and payer.

- Costs can be split equally among all participants, or proportionally, using custom weights.

- Any participant of the project can delete expenses.

- All expenses are stored and updated in real time within the project.

### Balance Calculation and Settlements

- The application automatically computes live balances for each participant based on all recorded expenses.

- An optimized settlement list is generated to minimize the number of reimbursements required, making it easier to settle debts efficiently.

### Export

- Projects can be exported to Excel, allowing users to perform external analysis, reporting, or archiving.

## For Developers

### Pre-commit

Pre-commit automatically formats your code before each commit, ensuring that all developers follow the same formatting rules. To install it:
- Install Pre-commit: `pip install pre-commit`
- Set up Pre-commit in your project: `pre-commit install`
Once installed, Pre-commit will automatically run the defined checks and formatting before each commit.

### Run the Application in Dev Mod

The dev mode allows you to implement new features and test your code. It will show the changes in the code instantly and will write the data in your local folder.

Follows the instructions to run the application and just replace ```prod``` by ```dev``` in the commands:

```bash
docker compose -f docker-compose.dev.yaml up --build
```

### Tests

To run the tests, you have to install the requirements:

```bash
pip install -r requirements.txt
```

and then run pytest (with verbose if you want more information on what is happening):

```bash
pytest -v
```

Both must be run from the root of the project.

## Global Architecture

The application follows a containerized client–server architecture orchestrated with Docker Compose.

The backend is a Python API responsible for authentication, expense management, balance computation, and data management.

The frontend is a React web application built with Vite.

```
.
├── backend/                # Server-side logic
├── data/                   # Application data
├── frontend/               # Client-side application
├── tests/                  # Unit tests
├── .env                    # Environment variables
├── .gitignore              # Files/folders ignored by Git
├── .pre-commit-config.yaml # Linting configuration
├── docker-compose.dev.yaml # Docker setup for development
├── docker-compose.prod.yaml# Docker setup for production
├── README.md               # Project documentation
├── requirements-test.txt   # Python testing dependencies
└── requirements.txt        # Python application dependencies
```

For more informations on the architecture of the backend and the frontend, you can read the corresponding documentation:
- [Backend](backend/README.md)
- [Frontend](frontend/README.md)

## To Be Done

This project was completed within a limited timeframe, and we identified several aspects we would have liked to improve but did not have enough time to address. Among these, the most important are:

- Deploy the application (for example using Google Cloud Run). The application is intended to be deployed, and without deployment some elements may seem unnecessary or unclear (such as the JWT secret key or features requiring multiple users).

- Refactor the data structure. We initially used a single file containing all information about tricounts, including users and expenses. Once development was underway, we did not have time to revise this design. A better approach would be to use separate files with proper identifiers to link related entities.

- Rename `user` to something like `participant` to avoid confuson with the global users of the application

- Improve the development workflow. We try to make extensive use of GitHub, but some best practices were overlooked for efficiency, particularly around pull requests (e.g. mandatory reviews, automated checks).
