# Infrastructures-et-syst-mes-logiciels-2025
A collaborative project aiming to rebuild the core features of Tricount from scratch. The goal is to design a clean, intuitive system that allows users to split expenses, track balances, and settle debts seamlessly within a group.

## For developers

Pre-commit automatically formats your code before each commit, ensuring that all developers follow the same formatting rules. To install it:
- Install Pre-commit: `pip install pre-commit`
- Set up Pre-commit in your project: `pre-commit install`
Once installed, Pre-commit will automatically run the defined checks and formatting before each commit.

## Run the app with Docker

This project uses Docker Compose to build and run the app. Make sure you have Docker Engine installed and running on your machine.

### .env file
You need an .env file looking like
```
JWT_SECRET_KEY=xxx
```

### Env mode

You can launch the app in dev mode or prod mode. The dev mode is for developpers to implement new features and test their code, it will show the changes in the code instantly and will write the data in the developper local folder.
The prod mode is for users.
In the following setup instructions, replace env by either dev or prod, based on your utilisation of the app.

### First time setup

To build the images and start the app for the first time:

```bash
docker compose -f docker-compose.{env}.yaml up --build
```

This will:
- Build the backend and frontend images
- Start the backend service with the tricount data as a persistent volume
- Start the frontend service that depends on the backend one

### Future use

Once the images have been built, you can start the app with:

```bash
docker compose -f docker-compose.{env}.yaml up
```

### Accessing the app

The app is running at http://localhost:5173

### Stopping the app

To stop and remove all running containers:

```bash
docker compose -f docker-compose.{env}.yaml down
```

## Tests
To run the tests, you have to install the requirements:

```bash
pip install -r requirements.txt
```

and then run pytest (with verbose if you want more information on what is happening):

```bash
pytest -v
```

Both must be run from the root of the project.

As for the deployment of the app, you need an .env file looking like

```
JWT_SECRET_KEY=xxx
```
