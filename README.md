# Enterprise-Decision-Tracker
Enterprise Decision Tracker API. Built with Django REST Framework.

## Installation Guide

### Local Installation

The local version uses SQLite as the database.
Python 3.10 was used during development.

1. Clone the repository to your local machine.

    ```bash
    git clone https://github.com/Daneality/Enterprise-Decision-Tracker.git
    cd Enterprise-Decision-Tracker
    ```

2. Create a virtual environment and activate it.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages from `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4. You can easily run tests using pytest in the local    version to simplify testing :)
    
    ```bash
    pytest
    ```

5. Run the Django server.

    ```bash
    python manage.py runserver
    ```
The application should now be running at `http://localhost:8000`.
With Api's base URL at `localhost:8000/api`.

### Docker Installation

The Docker version uses a full-blown PostgreSQL database, which runs in a separate container.

1. Clone the repository to your local machine.

    ```bash
    git clone https://github.com/Daneality/Enterprise-Decision-Tracker.git
    cd Enterprise-Decision-Tracker
    ```

2. Build and run the Docker containers.

    ```bash
    docker-compose up --build
    ```

The application should now be running at `http://localhost:8000`.
With Api's base URL at `localhost:8000/api`.
I have **intentionally** added .env file to the repo to simplify testing.

## Documentation

The API documentation is automatically generated and can be accessed in two ways:

1. Swagger UI: You can interact with the API and try out its endpoints by visiting the Swagger UI at `http://localhost:8000/swagger`.

2. Schema: You can view the raw OpenAPI schema in JSON or YAML format by visiting `http://localhost:8000/swagger.json` or `http://localhost:8000/swagger.yaml`, respectively.

## Bonuses

All bonus features have been implemented:

- **Authentication**: Basic token-based authentication has been implemented to protect the API endpoints. Only authenticated users can create, update, delete, or evaluate decisions.

- **Search and Filter**: Query parameters have been implemented for filtering decisions by status, title, or measurable goal.

- **Pagination**: Pagination has been added to the `GET /decisions` endpoint. The pagination is set to 10 items per page.

- **User Management**: Different permissions for accessing certain endpoints. The `evaluate` endpoint requires the Admin (superuser) role.

More details about these features can be found in the API documentation.

## Authentication

To interact with the API, you need to acquire a token by using the `authentication/login` or `authentication/register` endpoints.

Once you have the token, you need to pass it in the header of your requests. The header should have the name `Authorization` and the value `Token <aquired_token>`, where `<aquired_token>` is the token you acquired.

All endpoints that involve write operations require authentication. The `evaluate` endpoint requires superuser rights. To register a user with superuser rights, you need to set `admin: true` when using the `authentication/register` endpoint.

To play around in the Swagger UI, you can set the authentication header by clicking the 'Authorize' button almost at the top of the page.

## API Endpoints

Here is a list of the available API endpoints:

- **Create Decision** (`POST /decisions`)
  - Accepts a JSON object with the following fields:
    - `title` (string, required)
    - `description` (string, required)
    - `measurable_goal` (string, required)
    - `status` (string, optional, default: "Pending")
  - Returns the created decision object with a unique id.

- **Get All Decisions** (`GET /decisions`)
  - Returns a paginated list of all decisions, including their `title`, `description`, `measurable_goal`, `status`, and `evaluation` if completed. The pagination is set to 10 items per page.
  - Supports query parameters for searching and filtering.

- **Get Single Decision** (`GET /decisions/:id`)
  - Returns the details of a single decision based on its id.

- **Update Decision** (`PUT /decisions/:id`)
  - Updates the `title`, `description`, `status`, or `measurable_goal` of an existing decision.
  - Updating the `status` to "Completed" allows an evaluation process.
  - Deletes the evaluation if the `status` has changed from "Completed" to "Pending" or if the `measurable_goal` has changed.

- **Delete Decision** (`DELETE /decisions/:id`)
  - Deletes a decision based on its id.

- **Evaluate Completed Decision** (`POST /decisions/:id/evaluate`)
  - Requires **admin** (superuser) rights to trigger.
  - Accepts a JSON object with the following fields:
    - `goal_met` (boolean, required)
    - `comments` (string, optional)
  - Only applicable if the decision's status is "Completed".
  - Stores the evaluation and associates it with the decision.

- **Register** (`POST /authentication/register`)
  - Accepts a JSON object with the following fields:
    - `username` (string, required)
    - `email` (string, required, format: email)
    - `password` (string, required)
    - `confirm_password` (string, required)
    - `admin` (boolean, optional, default: false)
  - Returns a token and a user.

- **Login** (`POST /authentication/login`)
  - Accepts a JSON object with the following fields:
    - `username` (string, required)
    - `password` (string, required)
  - Returns a token and a user.